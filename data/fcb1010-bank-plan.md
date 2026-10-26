# FCB1010 Bank Plan — Amp Switching + Routing
## Rig: Mesa Mark V:35 / Peavey Bandit 112 (as of 2026-10-24)

The Marshall DSL201 left the rig on 2026-09-14. The original three-amp
version of this document (seven banks, Marshall on SWITCH1, Bandit on
SWITCH2, Mesa on CCs) is in git history; commit 380ea49 has the full
three-amp combo matrix.

The per-switch table lives in `fcb1010-bank-matrix.md`. The data itself is
`fcb1010-patch-data.json`, compiled by `scripts/bank_plan.py`.

---

## System Overview

Every preset sets five things:

1. **Switch-Track routing** (MIDI ch2, one Program Change) -- which amps get
   signal. OUTA = Peavey, OUTB = Mesa. Factory presets, no programming.
2. **Mesa state** (MIDI ch1, one Program Change) -- recalls a preset saved on
   the Voodoo Lab Control Switcher (Channel, EQ, Solo1, Solo2 together).
3. **Peavey channel** -- FCB1010 built-in relay SWITCH1.
4. **Peavey FX loop** -- FCB1010 built-in relay SWITCH2.
5. **Daisy Seed patch** (MIDI ch3, one Program Change) -- 127 = dry.

No Control Changes are used.

---

## Switch-Track (MIDI ch2)

Factory presets, used as-is:

| PC | State | Meaning in this rig |
|----|-------|---------------------|
| 1 | A only | Peavey alone |
| 3 | B only | Mesa alone |
| 5 | A+B | both amps |
| 7 | Mute | neither amp (switches 5 and 10 only) |

PCs 2/4/6/8 are the same states with OUTB phase inverted -- not used.

The PC is not a free choice per patch: it follows from which amps are
audible (`peavey.present`, `mesa_preset != "muted"`). `bank_plan.py`
checks each patch's `switchtrack_pc_channel2` against that and refuses to
build on a mismatch.

Silencing one amp is done by routing, not by Mute: on 6/8 only B gets
signal, on 7/9 only A. Mute (PC7) is only for switches 5 and 10, where
neither amp should sound.

---

## Mesa -- Voodoo Lab Control Switcher (MIDI ch1, PC mode)

The Control Switcher is in PC mode and drives the Mesa through a BTPA cable
into its 5-pin DIN jack. Each PC recalls a preset that has to be saved on
the Control Switcher by hand first (hold button 1 + button 4 while its
switches are in the target combination):

| PC | Name | Setting |
|----|------|---------|
| 1 | clean_eq_on | Channel=Clean, Solo1=off, EQ=on |
| 2 | clean_eq_off | Channel=Clean, Solo1=off, EQ=off (not used now) |
| 3 | dirty_eq_on | Channel=Dirty, Solo1=off, EQ=on |
| 4 | dirty_eq_off | Channel=Dirty, Solo1=off, EQ=off (not used now) |
| 5 | muted | Channel=Clean, Solo1=on (mute), EQ=on |

When the Mesa isn't audible (7, 9, and the mutes) it gets `muted` as well
as being cut by the Switch-Track -- a harmless backup.

Relay map behind the BTPA cable, confirmed by hand: Relay 1 = Channel,
Relay 2 = EQ, Relay 3 = Solo1, Relay 4 = Solo2. Mesa's channel selector
must be in the FOOTSWITCH position.

---

## Peavey Bandit -- FCB1010 SWITCH1 / SWITCH2

The Bandit's footswitch jack is TRS: **TIP = FX loop, RING = channel**. A
TRS-to-2xTS Y cable splits it onto the FCB1010's two mono relay jacks:

```
Bandit RING (channel) -> FCB1010 SWITCH1   closed = dirty, open = clean
Bandit TIP  (FX loop) -> FCB1010 SWITCH2   closed = loop ON, open = loop off
```

Both polarities confirmed on the amp 2026-10-24. The Y cable replaced a
tip/ring-swapped TRS cable that went into SWITCH1 alone; the FCB's mono jack
shorted the plug's ring (the loop contact) to ground, which held the loop
off.

On stock firmware the `switch1_enabled`/`switch2_enabled` flag *is* the
relay state: every preset sets both relays, enabled = closed.

**Peavey muted** (`peavey.present` false) means all three together:
Switch-Track not routing A, FX loop off, and **clean channel** -- muted on
the dirty channel is still not quiet. `bank_plan.py` forces clean on every
muted patch regardless of `fcb_switch1_relay`.

---

## Daisy Seed (FX loops)

A Daisy Seed effects unit (daisy-fx) sits in both amps' FX loops: Peavey
send/return on the Daisy's left, Mesa on the right. That's why the Peavey's
loop is on in every patch where the Peavey plays.

The Daisy is on the end of the MIDI chain and answers program changes on
**ch3 only**. Every FCB preset sends it one, from the FCB's PC3 slot
(`daisy_pc` per patch, required). Program **127 is dry**: it's kept empty on
the Daisy's SD card, and the Daisy also boots on it, so it's dry from
power-up until a preset picks a patch. A patch chosen on the Daisy's own
buttons lasts until the next FCB press. Patch names are in
`meta.daisy_patches`.

If either amp's loop is series, that amp is silent while the Daisy is off or
booting -- dry still passes through the Daisy's converters. The Peavey can be
taken out of the loop by opening SWITCH2; the Mesa's loop can't be switched
from the FCB.

---

## Physical Connections

### MIDI chain
```
FCB1010 MIDI OUT -> Voodoo Lab Control Switcher MIDI IN
Control Switcher MIDI OUT (thru) -> Switch-Track MIDI IN
Switch-Track MIDI OUT/THRU -> Daisy Seed MIDI IN
```
Control Switcher listens on ch1, Switch-Track on ch2, Daisy on ch3.

### Audio
```
Guitar -> Switch-Track INPUT   (the only audio device on the pedalboard)
                          OUTA -> Peavey Bandit input
                          OUTB -> Mesa Mark V input
Peavey FX loop <-> Daisy Seed left;  Mesa FX loop <-> Daisy Seed right
```
Effects come from the Daisy Seed in the amps' FX loops, not from pedals in
front of the amps. The earlier Carcosa -> Blood Moon -> SCF Gold chain is gone.

### Switching cables
```
FCB1010 SWITCH1 + SWITCH2 <- TRS-to-2xTS Y cable <- Bandit footswitch jack
Voodoo Lab Control Switcher -> BTPA cable (10 ft) -> Mesa 5-pin DIN jack
```

### Power
- FCB1010: its own supply
- Voodoo Lab Control Switcher: 9-12VDC, 100mA, 2.1x5.5mm barrel
- Switch-Track: 9VDC, ~100mA, 2.1x5.5mm barrel, negative center

---

## FCB1010 notes

- Footswitch 10 is digit "0" (labeled 10/0).
- Everything is in bank 0, so no bank navigation is needed. DIRECT SELECT
  (Global Configuration) makes any preset two presses away if more banks
  come back.
- Switch-Track manual: mesa-boogie.imgix.net/media/User%20Manuals/SwitchTrack-Manual-web-combined.pdf

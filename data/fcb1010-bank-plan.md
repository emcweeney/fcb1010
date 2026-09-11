# FCB1010 Bank Plan — Amp Switching + Routing
## Rig: Mesa Mark V:35 / Marshall DSL201 / Peavey Bandit 112

---

## System Overview

Three amps, each with two channel states (Clean / Dirty), controlled
via three coordinated systems:

1. **FCB1010's own built-in relay outputs** (SWITCH 1, SWITCH 2) --
   direct analog relay closures, not MIDI -- handle channel switching
   for **Marshall and Bandit**. Already tested and working.

2. **Voodoo Lab Control Switcher** (MIDI Channel 1, CC mode) --
   handles **Mesa only**, via a BTPA custom cable into Mesa's
   proprietary 5-pin DIN switching jack. A single CC message (CC80)
   per patch sets Mesa's channel.

3. **Switch-Track** (MIDI Channel 2, changed from factory default of
   1 to avoid collision with Voodoo Lab) -- audio routing on the
   right leg of the SCF Gold stereo split. Determines whether
   Marshall, Bandit, both, or neither actually receive signal.

4. **Mesa Solo mute** -- triggered via Voodoo Lab CC82 (Solo 1) or
   CC83 (Solo 2) (see Mesa CC Mapping below), sent through the BTPA
   cable to Mesa's Solo1/Solo2 pins. This is entirely a Voodoo Lab Control Switcher
   function -- Switch-Track has no role in Mesa's muting at all, it
   only routes Marshall/Bandit presence on the right SCF Gold leg.
   Requires a one-time physical prerequisite: Mesa's own Solo Level
   knob(s) must be turned down to zero on the amp, since Solo is
   normally a boost -- only becomes a mute once its level is set to
   zero first. Mesa sits permanently on the left leg of the SCF Gold
   (always part of the stereo pair) and cannot be silenced via audio
   routing the way Marshall/Bandit can -- the Solo-mute is the only
   way to silence it.

FCB1010 has 10 banks (0-9), 10 switches per bank -- 100 presets total.

---

## Switch-Track MIDI Control -- No Custom Programming Needed

Switch-Track has its own internal preset memory (256 presets,
recalled via MIDI Program Change 1-128 in two banks). Critically,
**the factory default presets already cover every state this rig
needs** -- no manual programming, no SysEx work required.

From the Switch-Track manual's factory preset table, 8 unique
combinations repeat across all 256 slots. The four that matter:

| Program Change # | MUTE | BOTH | OUTA | OUTB | Meaning |
|-------------------|------|------|------|------|---------|
| **1** | off | off | on | off | **A** (Marshall only) |
| **3** | off | off | off | on | **B** (Bandit only) |
| **5** | off | on | on | on | **A+B** (both) |
| **7** | on | off | off | off | **Mute** (neither) |

(Presets 2, 4, 6, 8 are the same four states with OUTB phase
inverted -- not needed unless a phase cancellation issue comes up.)

**Each FCB1010 patch sends two simultaneous MIDI messages:**
- Program Change on **Channel 1** -- tells Voodoo Lab which
  amp-channel combo to recall
- Program Change **1, 3, 5, or 7** on **Channel 2** -- tells
  Switch-Track which routing state to recall (A / B / A+B / Mute)

This is standard FCB1010 behavior (each preset can transmit multiple
MIDI messages across different channels) -- more setup per patch, but
nothing exotic, and it means Switch-Track works entirely on factory
defaults.

---

## Footswitch Numbering -- Important

The FCB1010's physical footswitches are labeled **1 through 10**, but
footswitch **10 is actually digit "0"** (labeled "10/0" on the unit
itself). Footswitches 1-9 map directly to digits 1-9.

---

## DIRECT SELECT Mode -- Fast Navigation

By default, the FCB1010 requires stepping through banks one at a time
before selecting a preset. **DIRECT SELECT mode** (Global
Configuration menu, off by default) allows any preset in any bank to
be reached in exactly 2 presses: press the footswitch for the bank
number, then the footswitch for the preset number.

**Example:** Bank 9, preset 4 -- press footswitch #9, then #4.

**Once the UnO chip arrives**, a favorites feature adds single-press
recall on top of this for specific stored presets.

---

## Bank Map

| Bank | Contents |
|------|----------|
| 0 | Isolated tone-building (each amp alone, clean/dirty) |
| 1 | Mesa clean -- complete |
| 2 | Mesa dirty -- complete |
| 3 | Marshall clean -- complete |
| 4 | Marshall dirty -- complete |
| 5 | Bandit clean -- complete |
| 6 | Bandit dirty -- complete |
| 7 | Open -- reserved for performance/favorites bank |
| 8 | Open -- reserved for performance/favorites bank |
| 9 | Open -- reserved for performance/favorites bank |

---

## Physical Connections

### MIDI Chain
```
FCB1010 MIDI OUT
  -> Voodoo Lab Control Switcher MIDI IN
Voodoo Lab Control Switcher MIDI OUT (echoes/passes through)
  -> Switch-Track MIDI IN
```
One MIDI cable run, daisy-chained through both devices. Voodoo Lab
listens on Channel 1 (CC only), Switch-Track listens on Channel 2
(PC only) -- each device ignores messages not on its assigned channel.

### Audio Signal Chain
```
Guitar -> Carcosa -> Blood Moon -> SCF Gold
  Left Out  -> Mesa amp input
  Right Out -> Switch-Track INPUT
                 Switch-Track OUTA -> Marshall input
                 Switch-Track OUTB -> Bandit input
                 Switch-Track TUNER -> (unused / actual tuner if desired)
```

### Amp Switching / Control Cabling
```
FCB1010 SWITCH 1 (built-in relay, 1/4" TS) -> Marshall channel/footswitch jack
FCB1010 SWITCH 2 (built-in relay, 1/4" TS) -> Bandit channel/footswitch jack
Voodoo Lab Control Switcher -> BTPA custom cable (10 ft) -> Mesa 5-pin DIN jack
  (BTPA cable internally maps Voodoo Lab's relays 1/2/3 to Mesa's
  Channel/Solo1/Solo2 pins -- already correctly wired by BTPA, no
  further pin-mapping needed)
```

### Power
- FCB1010: standard 9V pedal supply
- Voodoo Lab Control Switcher: 9-12VDC, 100mA, 2.1x5.5mm barrel
- Switch-Track: 9VDC, ~100mA, 2.1x5.5mm barrel, negative center
- All three can share a multi-output pedalboard power supply


---

## Mesa CC Mapping (Voodoo Lab, Channel 1)

Voodoo Lab Control Switcher is dedicated entirely to Mesa. EQ is left
as a manual, physical setting on the amp -- set once, never MIDI
controlled, not part of any patch.

| CC Number | Voodoo Lab Relay | Function |
|-----------|-------------------|----------|
| CC80 | Relay 1 | Channel (Clean/Dirty) |
| CC81 | Relay 2 | EQ -- set manually, not used per-patch |
| CC82 | Relay 3 | Solo 1 -- clean channel solo/mute |
| CC83 | Relay 4 | Solo 2 -- lead channel solo/mute |

**Confirmed against real hardware** via manual relay testing once the
BTPA cable arrived -- this corrected an earlier assumption (originally
CC81 was assumed to be Solo1; testing showed Relay 2 is actually EQ,
shifting Solo1 to Relay 3/CC82 and adding Solo2 at Relay 4/CC83).

**Per-patch load:** Channel CC is sent on every patch. A Solo CC is
only sent on "amp alone" mute-style patches (using whichever Solo
number matches the currently active channel) -- never both
simultaneously. Maximum 2 CCs per patch, comfortably within the
FCB1010's per-preset capacity.

---

## Bank 0 -- Isolated Tone-Building

Each amp completely alone -- fast access for dialing in individual
tones without any combo logic in the way. These are the same six
"alone" patches that also exist as switch 1 of Banks 1-6, consolidated
here for quick side-by-side comparison.

| Sw | Function | Mesa CC (Ch1) | Marshall Relay | Bandit Relay | Switch-Track PC (Ch2) |
|----|----------|---------------|-----------------|----------------|------------------------|
| 1 | Mesa clean (alone) | CC80=0 | SWITCH1=n/a (muted via routing) | SWITCH2=n/a (muted via routing) | PC7 (Mute) |
| 2 | Mesa dirty (alone) | CC80=127 | SWITCH1=n/a (muted via routing) | SWITCH2=n/a (muted via routing) | PC7 (Mute) |
| 3 | Marshall clean (alone) | CC80=0 (Clean, default) + CC82=127 (Solo1 mute) | SWITCH1=OFF (Clean) | SWITCH2=n/a (muted via routing) | PC1 (A) |
| 4 | Marshall dirty (alone) | CC80=0 (Clean, default) + CC82=127 (Solo1 mute) | SWITCH1=ON (Dirty) | SWITCH2=n/a (muted via routing) | PC1 (A) |
| 5 | Bandit clean (alone) | CC80=0 (Clean, default) + CC82=127 (Solo1 mute) | SWITCH1=n/a (muted via routing) | SWITCH2=OFF (Clean) | PC3 (B) |
| 6 | Bandit dirty (alone) | CC80=0 (Clean, default) + CC82=127 (Solo1 mute) | SWITCH1=n/a (muted via routing) | SWITCH2=ON (Dirty) | PC3 (B) |
| 7-10 | empty | -- | -- | -- | -- |

---

## Bank 1 -- Mesa Clean (Complete)

| Sw | Function | Mesa CC (Ch1) | Marshall Relay | Bandit Relay | Switch-Track PC (Ch2) |
|----|----------|---------------|-----------------|----------------|------------------------|
| 1 | Mesa clean (alone) | CC80=0 | SWITCH1=n/a (muted via routing) | SWITCH2=n/a (muted via routing) | PC7 (Mute) |
| 2 | Mesa clean + Marshall clean | CC80=0 | SWITCH1=OFF (Clean) | SWITCH2=n/a (muted via routing) | PC1 (A) |
| 3 | Mesa clean + Bandit clean | CC80=0 | SWITCH1=n/a (muted via routing) | SWITCH2=OFF (Clean) | PC3 (B) |
| 4 | Mesa clean + Marshall clean + Bandit clean | CC80=0 | SWITCH1=OFF (Clean) | SWITCH2=OFF (Clean) | PC5 (A+B) |
| 5 | Mesa clean + Marshall dirty | CC80=0 | SWITCH1=ON (Dirty) | SWITCH2=n/a (muted via routing) | PC1 (A) |
| 6 | Mesa clean + Marshall clean + Bandit dirty | CC80=0 | SWITCH1=OFF (Clean) | SWITCH2=ON (Dirty) | PC5 (A+B) |
| 7 | Mesa clean + Bandit dirty | CC80=0 | SWITCH1=n/a (muted via routing) | SWITCH2=ON (Dirty) | PC3 (B) |
| 8 | Mesa clean + Marshall dirty + Bandit clean | CC80=0 | SWITCH1=ON (Dirty) | SWITCH2=OFF (Clean) | PC5 (A+B) |
| 9 | Mesa clean + Marshall dirty + Bandit dirty | CC80=0 | SWITCH1=ON (Dirty) | SWITCH2=ON (Dirty) | PC5 (A+B) |
| 10 | empty | -- | -- | -- | -- |

---

## Bank 2 -- Mesa Dirty (Complete)

| Sw | Function | Mesa CC (Ch1) | Marshall Relay | Bandit Relay | Switch-Track PC (Ch2) |
|----|----------|---------------|-----------------|----------------|------------------------|
| 1 | Mesa dirty (alone) | CC80=127 | SWITCH1=n/a (muted via routing) | SWITCH2=n/a (muted via routing) | PC7 (Mute) |
| 2 | Mesa dirty + Marshall clean | CC80=127 | SWITCH1=OFF (Clean) | SWITCH2=n/a (muted via routing) | PC1 (A) |
| 3 | Mesa dirty + Bandit clean | CC80=127 | SWITCH1=n/a (muted via routing) | SWITCH2=OFF (Clean) | PC3 (B) |
| 4 | Mesa dirty + Marshall clean + Bandit clean | CC80=127 | SWITCH1=OFF (Clean) | SWITCH2=OFF (Clean) | PC5 (A+B) |
| 5 | Mesa dirty + Marshall dirty | CC80=127 | SWITCH1=ON (Dirty) | SWITCH2=n/a (muted via routing) | PC1 (A) |
| 6 | Mesa dirty + Marshall clean + Bandit dirty | CC80=127 | SWITCH1=OFF (Clean) | SWITCH2=ON (Dirty) | PC5 (A+B) |
| 7 | Mesa dirty + Bandit dirty | CC80=127 | SWITCH1=n/a (muted via routing) | SWITCH2=ON (Dirty) | PC3 (B) |
| 8 | Mesa dirty + Marshall dirty + Bandit clean | CC80=127 | SWITCH1=ON (Dirty) | SWITCH2=OFF (Clean) | PC5 (A+B) |
| 9 | Mesa dirty + Marshall dirty + Bandit dirty | CC80=127 | SWITCH1=ON (Dirty) | SWITCH2=ON (Dirty) | PC5 (A+B) |
| 10 | empty | -- | -- | -- | -- |

---

## Bank 3 -- Marshall Clean (Complete)

| Sw | Function | Mesa CC (Ch1) | Marshall Relay | Bandit Relay | Switch-Track PC (Ch2) |
|----|----------|---------------|-----------------|----------------|------------------------|
| 1 | Marshall clean (alone) | CC80=0 (Clean, default) + CC82=127 (Solo1 mute) | SWITCH1=OFF (Clean) | SWITCH2=n/a (muted via routing) | PC1 (A) |
| 2 | Marshall clean + Mesa clean | CC80=0 | SWITCH1=OFF (Clean) | SWITCH2=n/a (muted via routing) | PC1 (A) |
| 3 | Marshall clean + Bandit clean | CC80=0 (Clean, default) + CC82=127 (Solo1 mute) | SWITCH1=OFF (Clean) | SWITCH2=OFF (Clean) | PC5 (A+B) |
| 4 | Marshall clean + Mesa clean + Bandit clean | CC80=0 | SWITCH1=OFF (Clean) | SWITCH2=OFF (Clean) | PC5 (A+B) |
| 5 | Marshall clean + Mesa dirty | CC80=127 | SWITCH1=OFF (Clean) | SWITCH2=n/a (muted via routing) | PC1 (A) |
| 6 | Marshall clean + Mesa clean + Bandit dirty | CC80=0 | SWITCH1=OFF (Clean) | SWITCH2=ON (Dirty) | PC5 (A+B) |
| 7 | Marshall clean + Bandit dirty | CC80=0 (Clean, default) + CC82=127 (Solo1 mute) | SWITCH1=OFF (Clean) | SWITCH2=ON (Dirty) | PC5 (A+B) |
| 8 | Marshall clean + Mesa dirty + Bandit clean | CC80=127 | SWITCH1=OFF (Clean) | SWITCH2=OFF (Clean) | PC5 (A+B) |
| 9 | Marshall clean + Mesa dirty + Bandit dirty | CC80=127 | SWITCH1=OFF (Clean) | SWITCH2=ON (Dirty) | PC5 (A+B) |
| 10 | empty | -- | -- | -- | -- |

---

## Bank 4 -- Marshall Dirty (Complete)

| Sw | Function | Mesa CC (Ch1) | Marshall Relay | Bandit Relay | Switch-Track PC (Ch2) |
|----|----------|---------------|-----------------|----------------|------------------------|
| 1 | Marshall dirty (alone) | CC80=0 (Clean, default) + CC82=127 (Solo1 mute) | SWITCH1=ON (Dirty) | SWITCH2=n/a (muted via routing) | PC1 (A) |
| 2 | Marshall dirty + Mesa clean | CC80=0 | SWITCH1=ON (Dirty) | SWITCH2=n/a (muted via routing) | PC1 (A) |
| 3 | Marshall dirty + Bandit clean | CC80=0 (Clean, default) + CC82=127 (Solo1 mute) | SWITCH1=ON (Dirty) | SWITCH2=OFF (Clean) | PC5 (A+B) |
| 4 | Marshall dirty + Mesa clean + Bandit clean | CC80=0 | SWITCH1=ON (Dirty) | SWITCH2=OFF (Clean) | PC5 (A+B) |
| 5 | Marshall dirty + Mesa dirty | CC80=127 | SWITCH1=ON (Dirty) | SWITCH2=n/a (muted via routing) | PC1 (A) |
| 6 | Marshall dirty + Mesa clean + Bandit dirty | CC80=0 | SWITCH1=ON (Dirty) | SWITCH2=ON (Dirty) | PC5 (A+B) |
| 7 | Marshall dirty + Bandit dirty | CC80=0 (Clean, default) + CC82=127 (Solo1 mute) | SWITCH1=ON (Dirty) | SWITCH2=ON (Dirty) | PC5 (A+B) |
| 8 | Marshall dirty + Mesa dirty + Bandit clean | CC80=127 | SWITCH1=ON (Dirty) | SWITCH2=OFF (Clean) | PC5 (A+B) |
| 9 | Marshall dirty + Mesa dirty + Bandit dirty | CC80=127 | SWITCH1=ON (Dirty) | SWITCH2=ON (Dirty) | PC5 (A+B) |
| 10 | empty | -- | -- | -- | -- |

---

## Bank 5 -- Bandit Clean (Complete)

| Sw | Function | Mesa CC (Ch1) | Marshall Relay | Bandit Relay | Switch-Track PC (Ch2) |
|----|----------|---------------|-----------------|----------------|------------------------|
| 1 | Bandit clean (alone) | CC80=0 (Clean, default) + CC82=127 (Solo1 mute) | SWITCH1=n/a (muted via routing) | SWITCH2=OFF (Clean) | PC3 (B) |
| 2 | Bandit clean + Mesa clean | CC80=0 | SWITCH1=n/a (muted via routing) | SWITCH2=OFF (Clean) | PC3 (B) |
| 3 | Bandit clean + Marshall clean | CC80=0 (Clean, default) + CC82=127 (Solo1 mute) | SWITCH1=OFF (Clean) | SWITCH2=OFF (Clean) | PC5 (A+B) |
| 4 | Bandit clean + Mesa clean + Marshall clean | CC80=0 | SWITCH1=OFF (Clean) | SWITCH2=OFF (Clean) | PC5 (A+B) |
| 5 | Bandit clean + Mesa dirty | CC80=127 | SWITCH1=n/a (muted via routing) | SWITCH2=OFF (Clean) | PC3 (B) |
| 6 | Bandit clean + Mesa clean + Marshall dirty | CC80=0 | SWITCH1=ON (Dirty) | SWITCH2=OFF (Clean) | PC5 (A+B) |
| 7 | Bandit clean + Marshall dirty | CC80=0 (Clean, default) + CC82=127 (Solo1 mute) | SWITCH1=ON (Dirty) | SWITCH2=OFF (Clean) | PC5 (A+B) |
| 8 | Bandit clean + Mesa dirty + Marshall clean | CC80=127 | SWITCH1=OFF (Clean) | SWITCH2=OFF (Clean) | PC5 (A+B) |
| 9 | Bandit clean + Mesa dirty + Marshall dirty | CC80=127 | SWITCH1=ON (Dirty) | SWITCH2=OFF (Clean) | PC5 (A+B) |
| 10 | empty | -- | -- | -- | -- |

---

## Bank 6 -- Bandit Dirty (Complete)

| Sw | Function | Mesa CC (Ch1) | Marshall Relay | Bandit Relay | Switch-Track PC (Ch2) |
|----|----------|---------------|-----------------|----------------|------------------------|
| 1 | Bandit dirty (alone) | CC80=0 (Clean, default) + CC82=127 (Solo1 mute) | SWITCH1=n/a (muted via routing) | SWITCH2=ON (Dirty) | PC3 (B) |
| 2 | Bandit dirty + Mesa clean | CC80=0 | SWITCH1=n/a (muted via routing) | SWITCH2=ON (Dirty) | PC3 (B) |
| 3 | Bandit dirty + Marshall clean | CC80=0 (Clean, default) + CC82=127 (Solo1 mute) | SWITCH1=OFF (Clean) | SWITCH2=ON (Dirty) | PC5 (A+B) |
| 4 | Bandit dirty + Mesa clean + Marshall clean | CC80=0 | SWITCH1=OFF (Clean) | SWITCH2=ON (Dirty) | PC5 (A+B) |
| 5 | Bandit dirty + Mesa dirty | CC80=127 | SWITCH1=n/a (muted via routing) | SWITCH2=ON (Dirty) | PC3 (B) |
| 6 | Bandit dirty + Mesa clean + Marshall dirty | CC80=0 | SWITCH1=ON (Dirty) | SWITCH2=ON (Dirty) | PC5 (A+B) |
| 7 | Bandit dirty + Marshall dirty | CC80=0 (Clean, default) + CC82=127 (Solo1 mute) | SWITCH1=ON (Dirty) | SWITCH2=ON (Dirty) | PC5 (A+B) |
| 8 | Bandit dirty + Mesa dirty + Marshall clean | CC80=127 | SWITCH1=OFF (Clean) | SWITCH2=ON (Dirty) | PC5 (A+B) |
| 9 | Bandit dirty + Mesa dirty + Marshall dirty | CC80=127 | SWITCH1=ON (Dirty) | SWITCH2=ON (Dirty) | PC5 (A+B) |
| 10 | empty | -- | -- | -- | -- |

---

---

## Bank 7 -- Open

Open -- reserved for performance/favorites bank.

---

## Bank 8 -- Open

Open -- reserved for performance/favorites bank.

---

## Bank 9 -- Open

Open -- reserved for performance/favorites bank.

---

## Design Notes

- **Every patch sends exactly 2 MIDI messages simultaneously:** one
  CC on Channel 1 (to Voodoo Lab, setting Mesa's channel and
  occasionally Solo) and one PC on Channel 2 (to Switch-Track,
  setting audio routing). Marshall and Bandit channel switching is
  handled entirely by the FCB1010's own built-in relays -- no MIDI
  involved for those two amps at all.
- **Switch-Track requires zero custom programming.** Its factory
  default presets already contain the exact A/B/A+B/Mute states
  needed (PC1/3/5/7) -- confirmed directly from the manual's factory
  preset table.
- **Mesa Solo CC (CC81) is only sent** on patches where Marshall
  and/or Bandit are present but Mesa is not part of the named combo.
  On these patches Mesa defaults to Clean (CC80=0) + Solo1 mute
  (CC81=127) -- the specific channel doesn't matter since Mesa is
  silent either way, but a consistent default keeps behavior
  predictable.
- **"Mesa alone" patches** (Bank 0/1, switch 1) only need
  Switch-Track PC7 (Mute) -- no Solo CC needed, since Mesa is already
  present and audible by default.
- **A+B summing:** when Marshall and Bandit are both routed onto the
  same (right) leg via Switch-Track, that side of the stereo field
  carries two amps' worth of signal versus Mesa alone on the left.
  This is expected and intentional, not a fault -- may need volume
  balancing across the two legs depending on the combo.

---

## Hardware Notes

- **Marshall & Bandit channel switching** -- FCB1010's own built-in
  analog relay outputs (SWITCH 1, SWITCH 2). These are direct relay
  closures triggered by preset selection, not MIDI messages -- they
  do not count against the FCB1010's per-preset MIDI message budget.
  Already tested and working.
- **Mesa channel switching** -- Voodoo Lab Control Switcher (MIDI
  Channel 1, CC mode), via BTPA custom cable (10 ft) into Mesa's
  5-pin DIN jack. See Mesa CC Mapping section above for CC80/81/82.
  EQ is set manually on the amp, not MIDI controlled.
- **Audio routing (Marshall/Bandit presence)** -- Switch-Track (MIDI
  Channel 2, changed from factory default 1), on the right leg of the
  SCF Gold, after the stereo split. Runs entirely on factory preset
  defaults (PC1/3/5/7) -- no SysEx or custom programming required.
- **FCB1010 per-patch MIDI budget check:** each patch sends 1 CC
  (Mesa, Channel 1) + 1 PC (Switch-Track, Channel 2) -- well within
  the FCB1010's per-preset capacity (up to 5 PC + 2 CC + more).
  Marshall/Bandit switching uses the built-in relays, not MIDI, so
  they add no load to this budget.
- Mesa's channel selector switch must be set to FOOTSWITCH position
  for external switching to respond
- Switch-Track power: 9VDC, 2.1x5.5mm barrel, negative center,
  ~100mA -- compatible with standard pedalboard power supply
- Switch-Track manual: mesa-boogie.imgix.net/media/User%20Manuals/
  SwitchTrack-Manual-web-combined.pdf

---

*Complete bank map including both channel switching (Voodoo Lab) and
audio routing (Switch-Track via factory defaults on a second MIDI
channel), plus the Mesa solo-hack override for patches requiring true
Mesa silence. Banks 6-9 remain open for a future performance/favorites
bank and additional functions.*

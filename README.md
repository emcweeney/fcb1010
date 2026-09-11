# fcb1010
Behringer FCB1010 pedalboard sysex interface

> **This is a fork of [riban-bw/fcb1010](https://github.com/riban-bw/fcb1010)**
> (MIT licensed, see `LICENSE`). `scripts/fcb1010.py` is riban-bw's original
> sysex engine with a few bug fixes (see below); everything else in
> `scripts/` and `data/` is new tooling built on top of it to bulk-program an
> FCB1010 via CSV/JSON instead of its own front-panel buttons.

This code sends and receives MIDI System Exclusive messages between a
computer and a Behringer FCB1010 (**stock V2.5 firmware** -- untested against
other firmware, including third-party replacements). It reads/writes all 100
presets (10 banks x 10 switches) plus the device's global MIDI-channel and
config settings, round-tripping through a CSV file that's easy to bulk-edit.
Sysex structure has no official Behringer documentation and was reverse
engineered by riban-bw.

## Repository layout

- `scripts/` -- all Python code:
  - `fcb1010.py` -- the sysex engine (parse/build sysex, load/save CSV).
    Generic; works for any stock FCB1010.
  - `dump_fcb1010.py` / `send_fcb1010.py` -- receive a full config from the
    device / push one back, over MIDI. Generic.
  - `send_test_cc.py` / `send_test_pc.py` -- send one raw CC or Program
    Change message, for verifying MIDI-channel numbering and downstream
    relay/routing behavior against real hardware. Generic.
  - `bank_plan.py` -- bulk-programs banks 0-6 for **my specific rig** from
    `data/fcb1010-patch-data.json`. Not generic -- see below.
- `dumps/` -- CSV exports/backups of my FCB1010's config, plus a couple of
  older note-bank CSVs from a previous (Bass Station II) use of this pedal.
- `data/` -- the source data and docs behind `bank_plan.py`:
  `fcb1010-patch-data.json` (the 60-patch dataset), `fcb1010-bank-plan.md`
  (full narrative writeup of the rig and every patch), and the original task
  brief.

Run scripts from the repo root, e.g. `python3 scripts/bank_plan.py`; their
default input/output/data paths resolve relative to the repo regardless of
your current directory.

## Using this generically (any FCB1010)

The bottom of this file has riban-bw's original example: use `fcb1010.py`
directly as a library to parse/build sysex from your own script.

For a no-code workflow, the three top-level scripts cover the standard
backup/edit/restore cycle:

1. `python3 scripts/dump_fcb1010.py` -- put the FCB1010 into SYSEX SEND mode
   (Global Config, footswitch #7 per the stock manual) and capture its
   current state to a CSV.
2. Edit the CSV -- by hand, in a spreadsheet, or with a script of your own --
   then `fcb.load()` it back into an `fcb1010` object (see `bank_plan.py` for
   an example of loading, mutating, and saving).
3. `python3 scripts/send_fcb1010.py` -- put the FCB1010 into SYSEX RCV mode
   and push the edited CSV back as a sysex dump.

`send_test_cc.py [channel] [controller] [value]` and
`send_test_pc.py [channel] [program]` send one raw MIDI message each --
useful for confirming what channel number/byte convention your downstream
gear expects, independent of the FCB1010 entirely.

Each preset (`fcb1010_preset` in `fcb1010.py`) exposes exactly what the
device's hardware supports and no more: 5 Program Changes (`pc1`..`pc5`,
each with its own enable flag and program number), 2 Control Changes
(`cc1`/`cc2`, each with enable/controller/value), the 2 built-in relay
outputs (`switch1_enabled`/`switch2_enabled`), 2 expression-pedal
configs (`expA`/`expB`, each with controller/min/max), and 1 note
(`note_value`). Each message type's MIDI channel is a *global* setting
(`fcb.pc1_midi_channel`, `fcb.cc1_midi_channel`, etc.) shared by every
preset, not settable per-preset.

## My rig: `bank_plan.py`

I use one FCB1010 to switch between three amps (Mesa Mark V:35, Marshall
DSL201, Peavey Bandit 112) with independent clean/dirty channel control on
each, plus audio routing so combinations of amps can be selectively muted.
Programming that by hand across 60 individual presets isn't practical, so
`bank_plan.py` reads `data/fcb1010-patch-data.json` -- one JSON object per
patch describing which amps are present, on which channel, and what MIDI/
relay messages that implies -- and writes all 60 presets in one shot.

The full narrative (amp signal chain, MIDI wiring, why each CC number was
chosen, per-bank tables) is in `data/fcb1010-bank-plan.md`. The short version
of what `bank_plan.py` actually programs per patch:

- 1 Program Change on MIDI channel 2, to a Mesa Switch-Track (audio routing)
- 1-2 Control Changes on MIDI channel 1, to a Voodoo Lab Control Switcher
  (Mesa's channel, and occasionally a Solo-mute)
- The FCB1010's own built-in relay outputs (SWITCH1/SWITCH2), which control
  the Marshall and Bandit amps' channel footswitch jacks directly -- not
  MIDI messages at all

None of the specific CC numbers, relay assignments, or amp names in
`bank_plan.py`/`fcb1010-patch-data.json` mean anything outside this exact
rig -- this section exists to be explicit that it's a worked example, not a
generic tool.

## Adapting the bank-plan approach to your own rig

The reusable idea in `bank_plan.py` isn't the Mesa/Marshall/Bandit data --
it's the pattern: **describe your rig's patches as structured data, then
mechanically translate that into the FCB1010's fixed per-preset message
slots.** That pattern only requires knowing two things about your own
setup:

1. **What your other gear needs to hear.** Figure out, for each downstream
   device (an amp switcher, a MIDI-controllable amp, a multi-effects unit,
   whatever), which MIDI channel it listens on and which Program Change or
   Control Change values do what you want. `send_test_cc.py`/
   `send_test_pc.py` are built for exactly this discovery step -- send one
   message at a time and watch what happens, before committing anything to
   a full bank plan.
2. **How that maps onto the FCB1010's slots.** Every preset has, at most,
   5 PCs + 2 CCs + 2 built-in relays + 2 expression-pedal configs + 1 note
   -- and each PC/CC's MIDI channel is shared across the whole device, not
   per-preset. If your rig needs more independent MIDI channels than that
   per patch, you'll hit the same ceiling this rig did (which is why Mesa's
   channel and Switch-Track's routing were deliberately put on two
   different channels sharing the device's 2 CC + PC1 slots, rather than
   needing more).

Concretely, to reuse this for a different rig:

- Write your own patch-data JSON, structured however makes sense for your
  gear (it doesn't need to match this repo's field names -- those are Mesa/
  Voodoo-Lab-specific).
- Copy `bank_plan.py`'s shape (`load_patch_data`, `apply_patch_data`,
  `_clear_preset`) but replace the body of `apply_patch_data`'s per-patch
  loop so it reads your JSON's fields and writes them onto the preset's
  actual attributes (`preset.pc1_enabled`/`pc1_program`, `preset.cc1_*`/
  `cc2_*`, `preset.switch1_enabled`/`switch2_enabled`, etc.) instead of the
  Mesa-specific ones.
- Set `fcb.pc1_midi_channel`/`cc1_midi_channel`/etc. to whatever channels
  your gear actually listens on (see the "0 = channel 1" note below).
- Everything else -- CSV load/save, the dump/send scripts, `PLANNED_BANKS`
  as a way to leave some banks untouched -- carries over unchanged.

## Notes from testing against real hardware

- `fcb1010.py` stores each MIDI channel as a raw 0-15 byte matching the
  standard MIDI status-byte convention: **channel 1 is stored as `0`**, not
  `1`. Confirmed by sending a raw CC on wire-byte `0` and observing a
  hardware device configured for "Channel 1" react to it.
- The per-preset `switch1_enabled`/`switch2_enabled` flags are **not**
  inverted the way the PC/CC enable flags are in the raw sysex (see
  `parse_sysex`/`get_raw_sysex` in `fcb1010.py`) -- a quirk worth knowing if
  you're reading the class implementation rather than just using it.

---

Data may be printed out with the `show_config` function. Data may be stored
to and recalled from a comma separated variable (CSV) file using `save` and
`load` functions. The CSV file is in a specific format which allows simple
editing within any spreadsheet application, or by editing the CSV text
directly.

# Example use (direct library use, from riban-bw's original README):

```
from fcb1010 import fcb1010
import rtmidi
from time import sleep

#   Handle MIDI input (callback)
#   event: Tuple with received MIDI data as list of integers, time since last message (float in seconds)
#   data: fcb1010 object to populate when a valid fcb1010 sysex message received
def on_midi_in(event, data):
    if data.parse_sysex(event[0]):
        print("Parsed FCB1010 sysex")
    else:
        for byte in event[0]:
            print(hex(byte), end=' ')
        print()

#   Send FCB1010 sysex
#   fcb: fcb1010 object
def send_sysex(fcb):
    global midiin
    midiin.cancel_callback()
    midiout.send_message(fcb.get_raw_sysex())
    sleep(2)
    midiin.set_callback(on_midi_in, fcb_rx)

# Create MIDI input and output ports
midiout = rtmidi.MidiOut(rtmidi.API_LINUX_ALSA)
midiin = rtmidi.MidiIn(rtmidi.API_LINUX_ALSA)
# For testing I connect to my second MIDI interface. For production should probably open virtual ports and manually connect
out_port = midiout.open_port(2)
in_port = midiin.open_port(2)
#out_port = midiout.open_virtual_port()
#in_port = midiin.open_virtual_port()

fcb_rx = fcb1010() # fcb1010 object used to receive sysex messages
midiin.ignore_types(sysex=False) # Enable reception of sysex
midiin.set_callback(on_midi_in, fcb_rx) # fcb_rx will be populated with any received sysex
```

Sending sysex from FCB1010 will populate the fcb1010 object called fcb_rx. Beware that MIDI thru on FCB1010 will mean that sending sysex may result in fcb_rx being updated

Save fcb_rx to file
```
fcb_rx.save()
```

Create a default FCB1010 object and send to device
```
fcb_tx = fcb1010()
send_sysex(fcb_tx)
```

Load fcb_tx from file then send to device
```
fcb_tx = fcb1010()
fcb_tx.load()
send_sysex(fcb_tx)
```

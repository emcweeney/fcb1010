# FCB1010 Bulk Programming -- Claude Code Task Brief

## Objective

Program a Behringer FCB1010 (stock firmware) with 54 presets across
6 banks, using a bulk SysEx export/edit/load workflow rather than
manual on-device button programming.

## Starting Point

Clone and build on top of:
**https://github.com/riban-bw/fcb1010**

This is a Python tool (uses `rtmidi`) that:
- Reads a full SysEx dump from a connected FCB1010 (100 presets, 10
  banks x 10 switches)
- Exports it to CSV for editing
- Loads a modified CSV back and sends it as a SysEx dump to write to
  the device

Review its README and CSV schema before writing any new code. Prefer
adapting this tool over writing a SysEx parser from scratch -- the
format is already solved there.

## Source Data

`fcb1010-patch-data.json` (attached alongside this brief) contains
all 54 target patches as structured data: bank/switch number, human
readable function description, and the exact MIDI values each patch
needs to encode.

Each patch has:
- `mesa.cc80_channel_value` -- Control Change 80, value 0 or 127,
  MIDI Channel 1 -- sets Mesa's amp channel via Voodoo Lab Control
  Switcher relay 1
- `mesa.cc82_solo1_mute_value` -- Control Change 82, value 127 (or
  `null` if not needed), MIDI Channel 1 -- fires Voodoo Lab relay 3,
  mutes Mesa. Only present on patches where Mesa is not part of the
  named combo.
- `marshall.fcb_switch1_relay` -- "on"/"off"/null -- NOT a MIDI
  message. This is the FCB1010's own built-in relay output (SWITCH1),
  configured as part of the preset itself, controlling Marshall's
  amp channel directly via a hardware relay closure.
- `bandit.fcb_switch2_relay` -- same as above but SWITCH2, controls
  Bandit.
- `switchtrack_pc_channel2` -- Program Change value (1, 3, 5, or 7),
  MIDI Channel 2 -- recalls a Mesa Switch-Track factory preset that
  sets audio routing (which of Marshall/Bandit actually receive
  signal). Switch-Track requires no custom programming -- its factory
  defaults already match: PC1=Marshall only, PC3=Bandit only,
  PC5=both, PC7=neither.

Per patch, this means: 1-2 CC messages on Channel 1 (Voodoo Lab), one
PC message on Channel 2 (Switch-Track), plus 0-2 built-in relay
states configured on the FCB1010 preset itself (not MIDI). Confirm
against riban-bw's CSV schema that all of these are representable --
particularly the two built-in relay states, since those may be a
separate CSV column/concept from PC/CC message data.

Banks 6-9 are intentionally excluded from this dataset -- they're
reserved for a future performance/favorites bank not yet designed.

## Hardware Context (for reference, not required reading to build the tool)

- Full narrative documentation: `fcb1010-bank-plan.md`
- Voodoo Lab relay 2 (CC81) controls Mesa's EQ -- deliberately
  excluded from the patch dataset since EQ is being left as a
  manual, constant setting on the amp, not something that changes
  per patch
- Voodoo Lab relay 4 (CC83, Solo2) exists but is unused in the
  current 54-patch set -- all "Mesa muted" patches default Mesa to
  Clean + Solo1 mute rather than tracking a "last known channel"

## Task

1. Set up the riban-bw/fcb1010 tool against the actual FCB1010
   hardware (requires a MIDI interface between the FCB1010 and the
   computer -- confirm what's available)
2. Perform an initial read/export to confirm the tool works and to
   see the real CSV schema/column layout
3. Write a script that takes `fcb1010-patch-data.json` and produces
   a correctly formatted CSV (matching riban-bw's schema) with all
   54 target presets populated
4. Load that CSV back through riban-bw's tool to generate and send
   the SysEx dump to the FCB1010
5. Verify against the real device -- step through several patches
   and confirm the amp actually responds as expected (this requires
   the full rig: FCB1010 -> Voodoo Lab -> Switch-Track -> amps, all
   physically connected)

## Open Questions to Resolve Early

- Does riban-bw's CSV format support setting the FCB1010's own
  built-in SWITCH1/SWITCH2 relay states per preset, or is that
  configured through a different mechanism?
- Does it support multiple CC/PC messages targeting different MIDI
  channels within a single preset?
- What MIDI interface is being used to connect the FCB1010 to the
  computer running this tool?

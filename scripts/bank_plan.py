#   Bulk-program FCB1010 banks (Mesa + Peavey amp switching rig) from
#   data/fcb1010-patch-data.json, on top of an existing exported CSV dump.
#   Which banks get touched is whatever's in the JSON's top-level "banks"
#   list, not hardcoded here - currently that's just bank 0.
#
#   Usage:
#       python3 bank_plan.py [input.csv] [output.csv] [patch-data.json]
#   Defaults:
#       input       = dumps/FCB1010_backup.csv
#       output      = dumps/FCB1010_bank_plan.csv
#       patch-data  = data/fcb1010-patch-data.json
#
#   Reuses fcb1010.py (riban-bw) as the read/write engine - this module only
#   supplies the per-preset data (from the JSON) and mutates an already-loaded
#   fcb1010 object. Banks 1-9, and every global setting except the two
#   MIDI channels below, are left exactly as they came in from the input dump.
#
#   REQUIRES a one-time manual setup step on the Voodoo Lab Control Switcher
#   itself before this does anything useful: each entry in the JSON's
#   meta.mesa_presets_pc mapping must be physically programmed onto Control
#   Switcher (hold button 1 + button 4 while its four switches are in the
#   target combination) under the listed PC number. See meta.mesa_preset_definitions
#   in the JSON for what each preset's switch combination should be.

import json
import sys
from pathlib import Path

from fcb1010 import fcb1010

REPO_ROOT = Path(__file__).resolve().parent.parent
DUMPS_DIR = REPO_ROOT / "dumps"
DATA_DIR = REPO_ROOT / "data"

#   Global MIDI channels shared by every preset in bank 0.
#   fcb1010.py stores MIDI channel as a raw 0-15 byte (channel 1 = 0),
#   matching standard MIDI status-byte convention.
MESA_MIDI_CHANNEL = 0          # Voodoo Lab Control Switcher - MIDI Channel 1
#   CONFIRMED 2026-08-31 against real hardware: scripts/send_test_cc.py 1 80 127
#   made the Voodoo Lab's Mesa-channel LED react (back when Mesa used raw CC;
#   the channel number itself is unaffected by the later switch to PC mode).
SWITCHTRACK_MIDI_CHANNEL = 1   # Switch-Track - MIDI Channel 2
#   CONFIRMED 2026-08-31 against real hardware: scripts/send_test_pc.py 2 3
#   produced a real A-to-B transition (OUTB lit).

#   2026-09-14: Mesa moved from raw CC control (CC80 channel, CC82 Solo-mute)
#   to Control Switcher's PC-preset-recall feature - one Program Change now
#   recalls an entire saved 4-switch combination (Channel + EQ + Solo1 +
#   Solo2) at once, instead of needing a separate CC per switch. This frees
#   both of the FCB1010's CC slots (now unused) and is what makes 5 distinct
#   Mesa presets (clean/dirty x EQ on/off, plus muted) representable at all
#   without exceeding the FCB1010's 2-CC-per-preset ceiling. The actual PC
#   numbers are just the mapping in the JSON's meta.mesa_presets_pc - keep
#   code and data in sync if that mapping ever changes.

#   2026-10-05: consolidated everything into a single bank (0) - switches
#   1-4 are the stereo amp combos (dirty-to-clean), switch 5 is mute,
#   switches 6-9 are single-amp reference tones (dirty-to-clean), switch 10
#   is mute. The old 3-bank layout (clean section / dirty section /
#   single-amp reference) is fully superseded, recoverable from git history
#   if ever wanted back. Which banks get touched is no longer hardcoded here
#   - it's whatever banks actually appear in the JSON's `patches` (see
#   apply_patch_data), so the two can't drift out of sync.


def _clear_preset(preset):
    preset.pc1_enabled = False
    preset.pc2_enabled = False
    preset.pc3_enabled = False
    preset.pc4_enabled = False
    preset.pc5_enabled = False
    preset.cc1_enabled = False
    preset.cc2_enabled = False
    preset.switch1_enabled = False
    preset.switch2_enabled = False
    preset.expA_enabled = False
    preset.expB_enabled = False
    preset.note_enabled = False


def load_patch_data(json_path):
    with open(json_path) as file:
        data = json.load(file)
    return data["meta"]["mesa_presets_pc"], data["banks"]


def apply_patch_data(fcb, mesa_presets_pc, banks):
    """Mutate an fcb1010 instance in place: set the two shared MIDI channels
    and program every preset in `banks` (each a {"bank": n, "patches": [...]}
    dict). Any switch position in those banks not present in the data is
    cleared."""
    fcb.pc1_midi_channel = SWITCHTRACK_MIDI_CHANNEL
    fcb.pc2_midi_channel = MESA_MIDI_CHANNEL

    populated = set()
    for bank_entry in banks:
        bank = bank_entry["bank"]
        for patch in bank_entry["patches"]:
            switch = patch["switch"]
            if not 1 <= switch <= 10:
                raise ValueError(f"patch switch out of range: {switch}")
            index = bank * 10 + (switch - 1)
            populated.add(index)

            preset = fcb.preset[index]
            _clear_preset(preset)

            #   Switch-Track routing - Program Change on MIDI channel 2
            preset.pc1_enabled = True
            preset.pc1_program = patch["switchtrack_pc_channel2"]

            #   Mesa preset recall - Program Change on MIDI channel 1, sent on
            #   every patch. Recalls a Control Switcher preset that was manually
            #   programmed to set Channel/EQ/Solo1/Solo2 together (see module
            #   docstring). Being a PC (not CC), this is inherently a "set to
            #   exactly this state" message every time, same as the old CC80 -
            #   no stale-state risk the way the old CC82 mute hack had.
            preset.pc2_enabled = True
            preset.pc2_program = mesa_presets_pc[patch["mesa_preset"]]

            #   Peavey channel - FCB1010's own built-in SWITCH2 relay, not MIDI.
            #   "on" = dirty, "off"/null = clean or n/a - confirmed correct
            #   (non-inverted) against real hardware 2026-09-11 - back when this
            #   relay drove Peavey via SWITCH2.
            #
            #   2026-09-14: Peavey's cable moved from SWITCH2 to SWITCH1 (Marshall's
            #   old, now-unused relay output), consolidating onto SWITCH1 since
            #   Marshall isn't expected back. NOT independently re-verified on
            #   SWITCH1 - the assumption is that polarity is a property of each
            #   amp's own footswitch jack circuit (confirmed different between
            #   Marshall and Peavey on their original relays), not of which FCB1010
            #   relay output drives it, so Peavey should behave identically here.
            #   Sanity-check this against the real amp before trusting a full send.
            preset.switch1_enabled = patch["peavey"]["fcb_switch1_relay"] == "on"
            #   SWITCH2 stays disabled everywhere - unused now that Peavey has
            #   moved to SWITCH1 and Marshall (SWITCH1's original amp) is gone.

    for bank_entry in banks:
        bank = bank_entry["bank"]
        for switch in range(1, 11):
            index = bank * 10 + (switch - 1)
            if index not in populated:
                _clear_preset(fcb.preset[index])


def main():
    in_file = sys.argv[1] if len(sys.argv) > 1 else str(DUMPS_DIR / "FCB1010_backup.csv")
    out_file = sys.argv[2] if len(sys.argv) > 2 else str(DUMPS_DIR / "FCB1010_bank_plan.csv")
    json_file = sys.argv[3] if len(sys.argv) > 3 else str(DATA_DIR / "fcb1010-patch-data.json")

    mesa_presets_pc, banks = load_patch_data(json_file)

    fcb = fcb1010()
    if not fcb.load(in_file):
        sys.exit(1)

    apply_patch_data(fcb, mesa_presets_pc, banks)

    if not fcb.save(out_file):
        sys.exit(1)
    patch_count = sum(len(b["patches"]) for b in banks)
    bank_numbers = sorted(b["bank"] for b in banks)
    print(f"Applied {patch_count} patches (bank {bank_numbers}) from {json_file}")
    print(f"Wrote {out_file}")
    print()
    print("Reminder: Control Switcher must have these presets programmed")
    print("onto it directly before this plan does anything useful:")
    for name, pc in mesa_presets_pc.items():
        print(f"  PC{pc} = {name}")


if __name__ == "__main__":
    main()

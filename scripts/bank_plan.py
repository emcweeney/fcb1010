#   Bulk-program FCB1010 banks 0-6 (Mesa/Marshall/Bandit amp switching rig)
#   from data/fcb1010-patch-data.json, on top of an existing exported CSV dump.
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
#   fcb1010 object. Banks 7-9 and every global setting except the three MIDI
#   channels below are left exactly as they came in from the input dump.

import json
import sys
from pathlib import Path

from fcb1010 import fcb1010

REPO_ROOT = Path(__file__).resolve().parent.parent
DUMPS_DIR = REPO_ROOT / "dumps"
DATA_DIR = REPO_ROOT / "data"

#   Global MIDI channels shared by every preset in banks 0-6.
#   fcb1010.py stores MIDI channel as a raw 0-15 byte (channel 1 = 0),
#   matching standard MIDI status-byte convention.
MESA_MIDI_CHANNEL = 0          # Voodoo Lab Control Switcher - MIDI Channel 1
#   CONFIRMED 2026-08-31 against real hardware: scripts/send_test_cc.py 1 80 127
#   made the Voodoo Lab's Mesa-channel LED react.
SWITCHTRACK_MIDI_CHANNEL = 1   # Switch-Track - MIDI Channel 2
#   CONFIRMED 2026-08-31 against real hardware: scripts/send_test_pc.py 2 3
#   produced a real A-to-B transition (OUTB lit). Also confirms Switch-Track's
#   factory preset table (PC1=A, PC3=B, PC5=A+B, PC7=Mute) is exactly as
#   documented, no off-by-one in the program numbers.

MESA_CHANNEL_CC = 80          # Voodoo Lab relay 1 - Mesa Clean/Dirty
#   CONFIRMED 2026-09-10 against real hardware with the BTPA cable connected:
#   Control Switcher button 1 = Channel (CC80), button 2 = EQ (CC81, unused),
#   button 3 = Solo 1 (CC82), button 4 = Solo 2 (CC83, unused). This matches
#   data/fcb1010-patch-data.json and supersedes the earlier fcb1010-bank-plan.md,
#   which had Solo1 on CC81 and no EQ relay.
MESA_SOLO1_MUTE_CC = 82

#   Banks covered by this dataset (0=isolated tone-building alone patches,
#   1-6=combo banks). Banks 7-9 are left untouched.
PLANNED_BANKS = range(7)


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
    return data["patches"]


def apply_patch_data(fcb, patches):
    """Mutate an fcb1010 instance in place: set the three shared MIDI channels
    and program every preset in banks 0-6 from `patches`. Any switch position
    in banks 0-6 not present in the data (e.g. switch 10, or 7-10 in bank 0)
    is cleared."""
    fcb.cc1_midi_channel = MESA_MIDI_CHANNEL
    fcb.cc2_midi_channel = MESA_MIDI_CHANNEL
    fcb.pc1_midi_channel = SWITCHTRACK_MIDI_CHANNEL

    populated = set()
    for patch in patches:
        bank = patch["bank"]
        switch = patch["switch"]
        if bank not in PLANNED_BANKS or not 1 <= switch <= 10:
            raise ValueError(f"patch bank/switch out of range: {bank}/{switch}")
        index = bank * 10 + (switch - 1)
        populated.add(index)

        preset = fcb.preset[index]
        _clear_preset(preset)

        #   Switch-Track routing - Program Change on MIDI channel 2
        preset.pc1_enabled = True
        preset.pc1_program = patch["switchtrack_pc_channel2"]

        #   Mesa channel select - CC80 on MIDI channel 1, sent on every patch
        preset.cc1_enabled = True
        preset.cc1_controller = MESA_CHANNEL_CC
        preset.cc1_value = patch["mesa"]["cc80_channel_value"]

        #   Mesa Solo1 mute - CC82 on MIDI channel 1, only when Mesa is not
        #   part of the named combo (value is null otherwise). The controller/
        #   value bytes are written even when disabled so the CSV is
        #   deterministic regardless of what the input dump had in this slot.
        solo_mute = patch["mesa"]["cc82_solo1_mute_value"]
        preset.cc2_enabled = solo_mute is not None
        preset.cc2_controller = MESA_SOLO1_MUTE_CC
        preset.cc2_value = solo_mute if solo_mute is not None else 0

        #   Marshall / Bandit channel - FCB1010's own built-in relays, not MIDI.
        #   "on" = dirty channel selected; "off" or null = relay open (amp is
        #   either on its clean channel or muted via Switch-Track routing).
        preset.switch1_enabled = patch["marshall"]["fcb_switch1_relay"] == "on"
        preset.switch2_enabled = patch["bandit"]["fcb_switch2_relay"] == "on"

    for bank in PLANNED_BANKS:
        for switch in range(1, 11):
            index = bank * 10 + (switch - 1)
            if index not in populated:
                _clear_preset(fcb.preset[index])


def main():
    in_file = sys.argv[1] if len(sys.argv) > 1 else str(DUMPS_DIR / "FCB1010_backup.csv")
    out_file = sys.argv[2] if len(sys.argv) > 2 else str(DUMPS_DIR / "FCB1010_bank_plan.csv")
    json_file = sys.argv[3] if len(sys.argv) > 3 else str(DATA_DIR / "fcb1010-patch-data.json")

    patches = load_patch_data(json_file)

    fcb = fcb1010()
    if not fcb.load(in_file):
        sys.exit(1)

    apply_patch_data(fcb, patches)

    if not fcb.save(out_file):
        sys.exit(1)
    print(f"Applied {len(patches)} patches (banks 0-6) from {json_file}")
    print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()

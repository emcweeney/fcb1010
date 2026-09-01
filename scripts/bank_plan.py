#   Bulk-program FCB1010 banks 0-5 (Mesa/Marshall/Bandit amp switching rig)
#   per the locked bank plan, on top of an existing exported CSV dump.
#
#   Usage:
#       python3 bank_plan.py [input.csv] [output.csv]
#   Defaults: input=dumps/FCB1010_backup.csv, output=dumps/FCB1010_bank_plan.csv
#
#   Reuses fcb1010.py (riban-bw) as the read/write engine - this module only
#   supplies the per-preset data and mutates an already-loaded fcb1010 object.

import sys
from pathlib import Path

from fcb1010 import fcb1010

DUMPS_DIR = Path(__file__).resolve().parent.parent / "dumps"

#   Global MIDI channels shared by every preset in banks 0-5.
#   NOTE: fcb1010.py stores MIDI channel as a raw 0-15 byte (channel 1 = 0),
#   matching standard MIDI status-byte convention. Verify against the real
#   Voodoo Lab / Switch-Track units on first load - if nothing responds,
#   this is the first thing to flip.
MESA_MIDI_CHANNEL = 0          # Voodoo Lab Control Switcher - MIDI Channel 1
SWITCHTRACK_MIDI_CHANNEL = 1   # Switch-Track - MIDI Channel 2

MESA_CHANNEL_CC = 80
MESA_SOLO1_CC = 81

#   Switch-Track factory preset numbers (routing states)
ST_A = 1        # Marshall only
ST_B = 3        # Bandit only
ST_AB = 5       # Both
ST_MUTE = 7     # Neither

#   One row per active switch (1-9) in banks 0-5, straight from
#   fcb1010-bank-plan.md. Switch 10 in each of these banks is left empty.
#
#   Fields: (bank, switch, cc80_value, solo1_mute, marshall_relay, bandit_relay, switchtrack_pc)
#   marshall_relay / bandit_relay: True=ON(Dirty) False=OFF(Clean) None=n/a (muted via routing, relay set OFF)
BANK_PLAN = [
    # Bank 0 - Mesa Clean
    (0, 1, 0,   False, None,  None,  ST_MUTE),
    (0, 2, 0,   False, False, None,  ST_A),
    (0, 3, 0,   False, None,  False, ST_B),
    (0, 4, 0,   False, False, False, ST_AB),
    (0, 5, 0,   False, True,  None,  ST_A),
    (0, 6, 0,   False, False, True,  ST_AB),
    (0, 7, 0,   False, None,  True,  ST_B),
    (0, 8, 0,   False, True,  False, ST_AB),
    (0, 9, 0,   False, True,  True,  ST_AB),

    # Bank 1 - Mesa Dirty
    (1, 1, 127, False, None,  None,  ST_MUTE),
    (1, 2, 127, False, False, None,  ST_A),
    (1, 3, 127, False, None,  False, ST_B),
    (1, 4, 127, False, False, False, ST_AB),
    (1, 5, 127, False, True,  None,  ST_A),
    (1, 6, 127, False, False, True,  ST_AB),
    (1, 7, 127, False, None,  True,  ST_B),
    (1, 8, 127, False, True,  False, ST_AB),
    (1, 9, 127, False, True,  True,  ST_AB),

    # Bank 2 - Marshall Clean
    (2, 1, 0,   True,  False, None,  ST_A),
    (2, 2, 0,   False, False, None,  ST_A),
    (2, 3, 0,   True,  False, False, ST_AB),
    (2, 4, 0,   False, False, False, ST_AB),
    (2, 5, 127, False, False, None,  ST_A),
    (2, 6, 0,   False, False, True,  ST_AB),
    (2, 7, 0,   True,  False, True,  ST_AB),
    (2, 8, 127, False, False, False, ST_AB),
    (2, 9, 127, False, False, True,  ST_AB),

    # Bank 3 - Marshall Dirty
    (3, 1, 0,   True,  True,  None,  ST_A),
    (3, 2, 0,   False, True,  None,  ST_A),
    (3, 3, 0,   True,  True,  False, ST_AB),
    (3, 4, 0,   False, True,  False, ST_AB),
    (3, 5, 127, False, True,  None,  ST_A),
    (3, 6, 0,   False, True,  True,  ST_AB),
    (3, 7, 0,   True,  True,  True,  ST_AB),
    (3, 8, 127, False, True,  False, ST_AB),
    (3, 9, 127, False, True,  True,  ST_AB),

    # Bank 4 - Bandit Clean
    (4, 1, 0,   True,  None,  False, ST_B),
    (4, 2, 0,   False, None,  False, ST_B),
    (4, 3, 0,   True,  False, False, ST_AB),
    (4, 4, 0,   False, False, False, ST_AB),
    (4, 5, 127, False, None,  False, ST_B),
    (4, 6, 0,   False, True,  False, ST_AB),
    (4, 7, 0,   True,  True,  False, ST_AB),
    (4, 8, 127, False, False, False, ST_AB),
    (4, 9, 127, False, True,  False, ST_AB),

    # Bank 5 - Bandit Dirty
    (5, 1, 0,   True,  None,  True,  ST_B),
    (5, 2, 0,   False, None,  True,  ST_B),
    (5, 3, 0,   True,  False, True,  ST_AB),
    (5, 4, 0,   False, False, True,  ST_AB),
    (5, 5, 127, False, None,  True,  ST_B),
    (5, 6, 0,   False, True,  True,  ST_AB),
    (5, 7, 0,   True,  True,  True,  ST_AB),
    (5, 8, 127, False, False, True,  ST_AB),
    (5, 9, 127, False, True,  True,  ST_AB),
]

#   Preset indices (bank*10 + switch-1) intentionally left empty (switch 10
#   in each of banks 0-5) - no PC/CC/relay messages sent.
EMPTY_PRESETS = [bank * 10 + 9 for bank in range(6)]


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


def apply_bank_plan(fcb):
    """Mutate an fcb1010 instance in place: set global channels and program
    banks 0-5 (presets 0-59) per BANK_PLAN. Banks 6-9 and all global
    settings other than the three MIDI channels below are left untouched,
    so this should be applied on top of a real dump/backup, not a bare
    default fcb1010()."""
    fcb.cc1_midi_channel = MESA_MIDI_CHANNEL
    fcb.cc2_midi_channel = MESA_MIDI_CHANNEL
    fcb.pc1_midi_channel = SWITCHTRACK_MIDI_CHANNEL

    for bank, switch, cc80, solo_mute, marshall, bandit, st_pc in BANK_PLAN:
        preset = fcb.preset[bank * 10 + (switch - 1)]
        _clear_preset(preset)
        preset.pc1_enabled = True
        preset.pc1_program = st_pc
        preset.cc1_enabled = True
        preset.cc1_controller = MESA_CHANNEL_CC
        preset.cc1_value = cc80
        preset.cc2_enabled = solo_mute
        preset.cc2_controller = MESA_SOLO1_CC
        preset.cc2_value = 127 if solo_mute else 0
        preset.switch1_enabled = bool(marshall)
        preset.switch2_enabled = bool(bandit)

    for index in EMPTY_PRESETS:
        _clear_preset(fcb.preset[index])


def main():
    in_file = sys.argv[1] if len(sys.argv) > 1 else str(DUMPS_DIR / "FCB1010_backup.csv")
    out_file = sys.argv[2] if len(sys.argv) > 2 else str(DUMPS_DIR / "FCB1010_bank_plan.csv")

    fcb = fcb1010()
    if not fcb.load(in_file):
        sys.exit(1)

    apply_bank_plan(fcb)

    if not fcb.save(out_file):
        sys.exit(1)
    print(f"Applied bank plan to banks 0-5, wrote {out_file}")


if __name__ == "__main__":
    main()

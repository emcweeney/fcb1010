#   Receive a full SysEx dump from a stock-firmware FCB1010 and save it as CSV
#
#   On the FCB1010, trigger a MIDI dump send (Global Config menu, per the
#   stock V2.5 manual) after this script is listening.
#
#   Usage: python3 dump_fcb1010.py [output.csv]
#   Default output: dumps/FCB1010_backup.csv
#   Depends on rtmidi

import sys
from pathlib import Path

from fcb1010 import fcb1010

DUMPS_DIR = Path(__file__).resolve().parent.parent / "dumps"


def choose_port(midiin):
    ports = midiin.get_ports()
    if not ports:
        print("No MIDI input ports found.")
        sys.exit(1)
    print("Available MIDI input ports:")
    for i, name in enumerate(ports):
        print(f"  {i}: {name}")
    return int(input("Select input port number: "))


def main():
    out_file = sys.argv[1] if len(sys.argv) > 1 else str(DUMPS_DIR / "FCB1010_backup.csv")

    import rtmidi
    fcb = fcb1010()
    received = {"ok": False}

    def on_midi_in(event, _data):
        message, _delta_time = event
        if fcb.parse_sysex(message):
            received["ok"] = True
            print("Received valid FCB1010 dump.")

    midiin = rtmidi.MidiIn()
    port = choose_port(midiin)
    midiin.open_port(port)
    midiin.ignore_types(sysex=False)
    midiin.set_callback(on_midi_in, None)

    input("Listening. Trigger the dump on the FCB1010, then press Enter here once it's sent...\n")
    midiin.close_port()

    if not received["ok"]:
        print("No valid FCB1010 sysex was received - nothing saved.")
        sys.exit(1)

    if fcb.save(out_file):
        print(f"Saved dump to {out_file}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

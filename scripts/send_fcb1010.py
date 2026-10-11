#   Load an FCB1010 CSV and send it as a SysEx dump to a stock-firmware FCB1010
#
#   Usage: python3 send_fcb1010.py [input.csv]
#   Default input: dumps/FCB1010_bank_plan.csv
#   Depends on rtmidi

import sys
import time
from pathlib import Path

from fcb1010 import fcb1010
from fcb_log import log_event

DUMPS_DIR = Path(__file__).resolve().parent.parent / "dumps"


def choose_port(midiout):
    ports = midiout.get_ports()
    if not ports:
        print("No MIDI output ports found.")
        sys.exit(1)
    print("Available MIDI output ports:")
    for i, name in enumerate(ports):
        print(f"  {i}: {name}")
    return int(input("Select output port number: "))


def send_config(fcb, source):
    """Send an fcb1010 object to the pedal and log it. source labels where the config came from."""
    import rtmidi
    midiout = rtmidi.MidiOut()
    port = choose_port(midiout)
    port_name = midiout.get_ports()[port]
    midiout.open_port(port)

    print(f"Sending {source} to FCB1010...")
    midiout.send_message(fcb.get_raw_sysex())
    time.sleep(2)
    midiout.close_port()
    log_event("send", fcb, source=source, port=port_name)
    print("Done. Step through a few presets on the unit to verify.")


def main():
    in_file = sys.argv[1] if len(sys.argv) > 1 else str(DUMPS_DIR / "FCB1010_bank_plan.csv")

    fcb = fcb1010()
    if not fcb.load(in_file):
        sys.exit(1)
    send_config(fcb, in_file)


if __name__ == "__main__":
    main()

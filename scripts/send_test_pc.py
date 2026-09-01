#   Send a single raw Program Change message, for verifying MIDI channel
#   numbering against real hardware (e.g. does Switch-Track react when we
#   send on "channel 2" as encoded by bank_plan.py?)
#
#   Usage: python3 send_test_pc.py <channel 1-16> <program 0-127>
#   Example: python3 send_test_pc.py 2 1
#       Sends PC1 (Switch-Track's "A" / Marshall-only routing preset) on
#       human-numbered MIDI channel 2 (wire byte 1) - watch for
#       Switch-Track's OUTA LED.
#
#   Depends on rtmidi

import sys


def choose_port(midiout):
    ports = midiout.get_ports()
    if not ports:
        print("No MIDI output ports found.")
        sys.exit(1)
    print("Available MIDI output ports:")
    for i, name in enumerate(ports):
        print(f"  {i}: {name}")
    return int(input("Select output port number: "))


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <channel 1-16> <program 0-127>")
        sys.exit(1)

    channel = int(sys.argv[1])
    program = int(sys.argv[2])
    if not 1 <= channel <= 16:
        print("Channel must be 1-16 (human-numbered).")
        sys.exit(1)

    channel_nibble = channel - 1
    status_byte = 0xC0 | channel_nibble

    import rtmidi
    midiout = rtmidi.MidiOut()
    port = choose_port(midiout)
    midiout.open_port(port)

    print(f"Sending Program Change {program} on MIDI channel {channel} "
          f"(wire byte {channel_nibble}, status 0x{status_byte:02X})...")
    midiout.send_message([status_byte, program])
    midiout.close_port()
    print("Sent. Check the receiving device for a reaction.")


if __name__ == "__main__":
    main()

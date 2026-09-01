#   Send a single raw Control Change message, for verifying MIDI channel
#   numbering against real hardware (e.g. does the Voodoo Lab Control
#   Switcher react when we send on "channel 1" as encoded by bank_plan.py?)
#
#   Usage: python3 send_test_cc.py <channel 1-16> <controller 0-127> <value 0-127>
#   Example: python3 send_test_cc.py 1 80 0
#       Sends CC80=0 on human-numbered MIDI channel 1 (encoded on the wire
#       as channel nibble 0) - watch for the Voodoo Lab's channel-1 LED/
#       response.
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
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <channel 1-16> <controller 0-127> <value 0-127>")
        sys.exit(1)

    channel = int(sys.argv[1])
    controller = int(sys.argv[2])
    value = int(sys.argv[3])
    if not 1 <= channel <= 16:
        print("Channel must be 1-16 (human-numbered).")
        sys.exit(1)

    channel_nibble = channel - 1
    status_byte = 0xB0 | channel_nibble

    import rtmidi
    midiout = rtmidi.MidiOut()
    port = choose_port(midiout)
    midiout.open_port(port)

    print(f"Sending CC{controller}={value} on MIDI channel {channel} "
          f"(wire byte {channel_nibble}, status 0x{status_byte:02X})...")
    midiout.send_message([status_byte, controller, value])
    midiout.close_port()
    print("Sent. Check the receiving device for a reaction.")


if __name__ == "__main__":
    main()

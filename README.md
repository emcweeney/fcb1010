# fcb1010
A helper for programming a Behringer FCB1010 guitar pedalboard from a
computer, instead of pressing its buttons over and over.

> **This is a copy ("fork") of someone else's project:
> [riban-bw/fcb1010](https://github.com/riban-bw/fcb1010).** It's free to
> use and change (MIT license, see `LICENSE`). The file `scripts/fcb1010.py`
> is their original code, with a few of their bugs fixed (listed below).
> Everything else here is new, built on top of it.

## What is an FCB1010, and what does this code do?

The FCB1010 is a floor pedal with 10 footswitches, split into 10 "banks" (so
100 footswitches total, 10 at a time). Guitarists step on it to send
commands to their amps and effects over MIDI -- a simple language musical
gear uses to talk to each other, like "switch to channel 2" or "turn this
knob to this exact value."

Programming a footswitch by hand means pressing buttons on the pedal itself,
one setting at a time, for every single one of the 100 slots. This project
lets you do it differently: write down what you want in a simple text file,
then send the whole thing to the pedal in one go. Under the hood it works by
having the computer "speak" the same private data format (called SysEx) that
the FCB1010 uses to save and load its own settings -- nobody officially
published this format, so `fcb1010.py`'s author figured it out by
experimenting.

## What's in this folder

- `scripts/` -- all the code:
  - `fcb1010.py` -- reads and writes the FCB1010's data. Works for anyone
    with this pedal.
  - `dump_fcb1010.py` -- pulls the current settings off the pedal and saves
    them to a file.
  - `send_fcb1010.py` -- takes a settings file and sends it to the pedal.
  - `send_test_cc.py` / `send_test_pc.py` -- send one single test message,
    so you can check "does my amp switcher actually listen to this?" before
    trusting a whole file to it.
  - `bank_plan.py` -- **specific to my own setup** (see below), not
    something you can use as-is.
- `dumps/` -- backup files of my pedal's settings.
- `data/` -- the description of my exact setup that `bank_plan.py` reads.

Run everything from this folder, e.g. `python3 scripts/bank_plan.py` --
these scripts find their files no matter where you're standing when you run
them.

## Mistakes we found and fixed

The original code (`fcb1010.py`) had three small bugs:

- **A misspelled setting.** When reading a saved note value back in, the
  code tried to store it under the wrong name, so that value was silently
  thrown away instead of being read.
- **Two settings sharing one slot.** Every preset can hold two separate
  "Control Change" messages. The code was accidentally reading and writing
  the *second* one's data into the *first* one's spot -- so the second
  slot never actually worked at all.
- **Off-by-one counting.** When saving to a file, the code numbered the 10
  banks and 10 footswitches starting from the wrong number, which either
  saved things to the wrong spot or made the saved file impossible to load
  back in correctly.

All three are fixed now.

## Using this for your own FCB1010

If you just want to back up and edit your pedal's settings (any FCB1010,
not just mine), here's the whole process:

1. **Back it up.** Run `python3 scripts/dump_fcb1010.py`. On the pedal
   itself, tell it to send its settings (in its Global Config menu, that's
   footswitch #7). This saves everything to a file.
2. **Edit the file.** Open it in a spreadsheet program, or a plain text
   editor, or write a small script -- whatever's easiest. `bank_plan.py` is
   an example of a script that edits a file like this automatically.
3. **Send it back.** Run `python3 scripts/send_fcb1010.py`, and put the
   pedal into its "receive" mode first so it's ready to listen.

`send_test_cc.py` and `send_test_pc.py` are for troubleshooting: they send
one single message so you can watch what happens on your gear, without
risking your whole setup.

Every footswitch slot on the FCB1010 can hold, at most: 5 "Program Change"
messages, 2 "Control Change" messages, control over its own 2 built-in
switches, 2 expression-pedal settings, and 1 musical note. That's the most
any one footswitch can ever do -- it's a limit of the pedal itself, not
something this code adds.

## My own setup: `bank_plan.py`

I use one FCB1010 to control three guitar amps at once (a Mesa, a Marshall,
and a Peavey), each with its own clean and "dirty"/distorted sound, plus
which amps are actually making noise at any given moment. Programming all of
that by hand, one footswitch at a time, would take forever -- so instead I
wrote down every footswitch's job in a file (`data/fcb1010-patch-data.json`)
and `bank_plan.py` turns that into the settings file the pedal understands.

The full write-up of my amps, cables, and why I chose the settings I did
lives in `data/fcb1010-bank-plan.md`. Short version of what each footswitch
sends:

- One message telling a separate audio-routing box which amps should
  actually be able to make sound.
- One or two messages telling another box to switch one amp's channel
  (and sometimes to mute it).
- Two built-in switches on the FCB1010 itself, wired directly to my other
  two amps' own footswitch jacks -- no MIDI involved for those two at all.

None of the specific numbers here will mean anything on someone else's
setup -- this part is a real example of my own gear, not a generic tool.

## Want to do something like this for your own gear?

You don't need my settings -- you need the idea. It's: **write down what you
want each footswitch to do, as plain data, then have a script turn that data
into the pedal's own file format.** To do that for your own rig:

1. **Figure out what your gear listens for.** For each piece of gear you
   want to control, find out which MIDI "channel" it listens on, and which
   messages make it do what you want. `send_test_cc.py`/`send_test_pc.py`
   are built for exactly this -- try one message, see what happens, before
   writing a whole plan.
2. **Remember the pedal's limit.** Every footswitch can only send 5 Program
   Changes and 2 Control Changes (plus its 2 built-in switches). If your
   plan needs more than that on one footswitch, you'll have to get clever
   about sharing those slots, the same way this project shares its 2
   Control Changes between two different amp functions.
3. **Write your own version of `bank_plan.py`.** Copy its shape, but swap
   out the part that reads my data for a part that reads yours, and have it
   set the pedal's own fields (things like `pc1_enabled`, `cc1_controller`,
   `switch1_enabled`) using your values instead of mine.

Everything else -- backing up, sending, and the general pattern -- works the
same no matter whose gear is on the other end.

## Things we only learned by testing on real hardware

- The pedal stores MIDI channel numbers starting at 0, not 1. So "channel 1"
  is actually saved as the number `0`. We only found this out by sending a
  test message and watching a real device react to it.
- One pair of settings (`switch1_enabled`/`switch2_enabled`) behaves
  opposite to how the similar-looking Program Change/Control Change settings
  work internally -- a quirk only visible if you read the raw code, not if
  you just use it.
- **Don't assume two amps are wired the same way.** One of my amps'
  channel-switching relay turned out to be backwards from what we expected
  -- flipping the switch "on" actually picked the amp's clean sound, not its
  dirty one. The other amp was wired the way we expected. We only found this
  by testing each amp separately, not by assuming they'd match.
- **Some messages need to be sent every single time, not just when you want
  something to happen.** One "mute" message only turns muting on or off when
  you actually send it -- it doesn't reset itself. We were only sending it
  to turn muting *on*, never to turn it back *off*, so an amp could get
  stuck muted after switching away from that footswitch. The fix was to
  send that message on every single footswitch, telling it to un-mute
  everywhere it wasn't specifically supposed to be muted.

---

Everything below this line is the original author's own instructions for
using `fcb1010.py` directly in your own Python code, kept as-is:

Data may be printed out with the `show_config` function. Data may be stored
to and recalled from a comma separated variable (CSV) file using `save` and
`load` functions. The CSV file is in a specific format which allows simple
editing within any spreadsheet application, or by editing the CSV text
directly.

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

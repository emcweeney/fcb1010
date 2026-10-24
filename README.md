# fcb1010

Tooling for bulk-programming a Behringer FCB1010 MIDI foot controller via
SysEx, instead of hand-entering 100 presets through its front panel.

## Fork notice

This is a fork of [riban-bw/fcb1010](https://github.com/riban-bw/fcb1010),
MIT licensed (see `LICENSE`). `scripts/fcb1010.py` is riban-bw's reverse-
engineered SysEx parser/builder, unchanged in structure but with three bugs
fixed (below). Everything else -- the bank-plan compiler, the MIDI test
utilities, the patch data -- is new.

## Thanks

To riban-bw: this project only exists because that reverse-engineering work
was already done and shared. Genuinely appreciated.

## What this actually is

The FCB1010 has no published SysEx spec; riban-bw reverse-engineered the
100-preset dump format (2352 bytes, 7-bit MIDI-packed) and wrote a Python
class that parses it into a CSV and rebuilds it from one. That's the
substrate. On top of it, this repo adds a small compiler: a JSON file
describing what each of a rig's footswitches should do, and a script that
translates that into the CSV riban-bw's class expects, which then gets
sent back to the device as a SysEx dump.

The point is to treat "what should footswitch 4 of bank 3 do" as a data
problem, not a hundred rounds of manual front-panel entry.

## Repository layout

```
scripts/
  fcb1010.py       riban-bw's engine: parse_sysex / get_raw_sysex / load / save
  dump_fcb1010.py  receive a live dump from the device -> CSV
  send_fcb1010.py  CSV -> SysEx dump -> device
  send_test_cc.py  fire one raw Control Change (channel, controller, value)
  send_test_pc.py  fire one raw Program Change (channel, program)
  bank_plan.py     compile data/fcb1010-patch-data.json -> CSV (rig-specific)
  fcb_log.py       log_event(): log each send/dump + save a dated backup (used by send/dump)
  history.py       timeline of git versions + logged events, diff any two
data/
  fcb1010-patch-data.json   the patch dataset bank_plan.py compiles
  fcb1010-bank-plan.md      narrative spec: wiring, routing, relay polarity
  fcb1010-bank-matrix.md    bank x switch reference table (update by hand)
dumps/
  CSV exports/backups, including some pre-dating this rig (Bass Station II note banks)
  fcb1010.log.jsonl         one JSON line per send/dump (see "Config history")
  history/                  dated backup of every send/dump (and extracted git versions)
```

Run everything from repo root; the scripts resolve their own paths.

## Fixes to `fcb1010.py`

- `parse_sysex` wrote incoming note data to `self.preset[i].note` instead of
  `.note_value`, the attribute the class actually defines. Silently dropped
  on every parse.
- `load()`/`save()` both handled CC2 (the second Control Change slot) by
  reading/writing CSV columns 15-17 into the CC1 fields a second time
  instead of the CC2 fields. CC2 was fully inert -- dropped on load,
  clobbered on save.
- `save()`'s preset-index arithmetic (`(bank - 1) * 10 + offset - 1` against
  already-0-indexed loop counters) wrote every preset to the wrong array
  slot and emitted 0-indexed `Bank`/`Preset` columns against a CSV format
  that `load()` expects 1-indexed. Round-tripping through the old `save()`
  didn't survive.

## Using the engine directly

`scripts/fcb1010.py` has no rig-specific assumptions; it's a straight
SysEx<->CSV<->object mapper. Standard loop:

```
python3 scripts/dump_fcb1010.py   # device -> CSV (put the FCB1010 in SysEx-send mode first)
# edit the CSV -- by hand, in a spreadsheet, or generate it -- then
python3 scripts/send_fcb1010.py   # CSV -> device (SysEx-receive mode on the unit)
```

`send_test_cc.py <channel> <controller> <value>` and
`send_test_pc.py <channel> <program>` exist for the step you actually need
before trusting any of this against real gear: confirm what a downstream
device does in response to one specific message, before generating a full
bank plan around an assumption about it.

Per-preset budget, which is a hardware ceiling, not a limitation of this
code: 5 Program Changes, 2 Control Changes, the 2 built-in relay outputs
(`switch1_enabled`/`switch2_enabled`, driven directly, not MIDI), 2
expression-pedal configs, 1 note. Each PC/CC's MIDI channel is a device-wide
setting, not per-preset.

## Config history

The pedal's state matters and nothing on the pedal says when or why it
changed. The history comes from two sources that `history.py` merges:

- **git** holds the *content*: every committed version of the CSVs in `dumps/`,
  chiefly `FCB1010_bank_plan.csv` (generated plan) and `FCB1010_backup.csv`
  (read-back from the pedal), with the commit message as the description.
- **the log**, `dumps/fcb1010.log.jsonl`, holds what git can't know: that a
  config was sent to the pedal, when, and that a later dump confirmed it.

### The flow

```
patch-data.json --bank_plan.py--> FCB1010_bank_plan.csv --send_fcb1010.py--> pedal
                                                                               |
pedal --(trigger dump on unit)--> dump_fcb1010.py --> FCB1010_backup.csv <-----+
         (read-back to confirm the plan landed)
```

Commit the plan and the read-back (with the log) after a session; the commit
message is the config's name and description. `send_fcb1010.py` and
`dump_fcb1010.py` each call `log_event()` (in `fcb_log.py`) when they finish.
If logging fails it prints a warning and the send or dump is unaffected.
Running `bank_plan.py` alone is *not* logged: it only writes a CSV and never
touches the pedal.

### Looking at it

```
python3 scripts/history.py        # the timeline
python3 scripts/history.py 7      # diff entry 7 against the one before it
python3 scripts/history.py 3 9    # diff entry 3 against entry 9
```

Negative numbers count from the end. Each row is a committed version of a CSV
in `dumps/` or a logged `send`/`dump`. The two files the scripts write are
labelled `plan` and `backup`; any other CSV you keep in `dumps/` (e.g. the
Bass Station II note banks) is labelled by its own name, so configs for any rig
show up without code changes. A plan is flagged `sent` if the log
has a send with the same hash, and `read back from pedal` if any read-back has
the same hash (a read-back identical to a plan is the proof it landed).
Diffs are per field with the CSV's 1-based Bank/Preset numbers, e.g.
`Bank 1 Preset 3: pc1_program 1 -> 9`, and print the full commit message.

To put a past config back on the pedal:

```
python3 scripts/history.py load 9
```

It shows what entry 9 would change compared with the pedal's last known state
(the latest send, dump or committed read-back), asks `[y/N]`, then sends it. The
send is logged as a new entry whose hash matches the old one. "Last known" means
what the log and git say, not a live read of the pedal; take a fresh dump first
if the pedal may have been edited by hand. You can also send any dated backup
directly: `python3 scripts/send_fcb1010.py dumps/history/<file>.csv`.

### What the log records

One JSON line per send or dump (JSON Lines, so an append can't corrupt earlier
lines). The log is only about pedal activity and doesn't mention git:

| Field | Meaning |
|---|---|
| `ts` | ISO-8601 time with timezone |
| `action` | `send` or `dump` |
| `sha256` | hash of the 2352 SysEx bytes; equal hash = identical pedal state |
| `source` | file sent or saved (repo-relative) |
| `port` | MIDI port name |
| `backup` | the dated backup of this exact config, under `dumps/history/` |

It is append-only and complete: every send and every dump is a line, repeats
included, and nothing is edited afterward. `history.py` marks an entry
`same as #N` when its hash matches an earlier one (e.g. restoring an old
config), a send `confirmed by a later dump` when a dump with the same hash
follows it, and a dump `differs from last send` when it doesn't match.

### Dated backups

Each send or dump also writes a plain CSV to `dumps/history/`, named by date,
action and the start of its hash, e.g. `2026-10-12_1832_send_1a189f09.csv`
(`-2`, `-3`... if the same minute repeats). They are the same format
`send_fcb1010.py` reads, so any of them can be sent back to the pedal. Versions
that predate the log were extracted from git into the same folder, named with
the commit date and `plan`/`backup` in place of the action. The folder is
tracked in git: it duplicates what git already holds, but keeps every config
one file away from a restore.

The log began on 2026-10-11. Before that, nothing recorded what was sent, so
entries were backfilled. Every committed version of `FCB1010_backup.csv` counts
as a dump (the user's rule), giving four dumps. Two sends were added from
evidence (the Sep 10 plan and the Oct 5 plan, each matched exactly by a later
read-back) and two on the user's word (the Bass Station II note banks,
`bank1_octave` and `multibank`, dated from their file times). All carry `backfilled` and `approx` (and `by_user` for the
rule-based dumps), and their times are the commit or file-write times, not the
real ones. Other plans with no matching read-back appear in the timeline from
git alone, with nothing recording that they were sent. Add an entry by hand only
if you know it happened.

### Not built yet

Saving `fcb1010-patch-data.json` alongside each send so switches can be read as
"Mesa dirty + Peavey clean" instead of raw numbers, and `history.py show N` to
print an entry's switch layout in those words.

## The rig this was built for

**As of 2026-10-24: Mesa Mark V:35 + Peavey Bandit 112.** A Marshall DSL201
was part of the rig until 2026-09-14; the three-amp version of everything is
in git history (commit 380ea49 has the full combo matrix).

`data/fcb1010-patch-data.json` holds one bank (bank 0) of 10 patches, which
`bank_plan.py` compiles. Each patch sets four things:

- **Switch-Track** (MIDI ch. 2, one PC) -- which amps get signal: OUTA =
  Peavey, OUTB = Mesa, using factory presets 1 (A), 3 (B), 5 (A+B) and
  7 (Mute). The PC follows from which amps are audible, and `bank_plan.py`
  checks it.
- **Mesa** (MIDI ch. 1, one PC) -- recalls one of five presets saved on a
  Voodoo Lab Control Switcher (Clean/Dirty x EQ on/off, plus Muted), which
  drives the Mesa's 5-pin DIN jack through a BTPA cable. Each preset bundles
  all four Control Switcher relays (Channel, EQ, Solo1, Solo2) into one
  recall, so no CCs are needed. The presets have to be programmed on the
  Control Switcher's front panel first (hold button 1 + button 4) -- see
  `meta.mesa_presets_pc`.
- **Peavey channel** -- the FCB1010's built-in SWITCH1 relay.
- **Peavey FX loop** -- the built-in SWITCH2 relay. The Bandit's TRS
  footswitch jack (tip = loop, ring = channel) is split onto SWITCH1/SWITCH2
  with a TRS-to-2xTS Y cable. The loop is on whenever the Peavey plays,
  because a Daisy Seed effects unit sits in both amps' FX loops.

Switches 1-4 are both amps (clean to dirty), 6-9 are one amp each, and 5 and
10 mute everything. A muted Peavey is also put on its clean channel with the
loop off; muted on the dirty channel it still isn't quiet. Full table:
`data/fcb1010-bank-matrix.md`; wiring and reasoning:
`data/fcb1010-bank-plan.md`.

## How this got built

I don't have the patience to reverse-engineer a proprietary SysEx dump or
memorize which CC number a MIDI foot controller's manual says maps to which
relay. That's exactly the kind of task I hand to Claude: point it at a
device's manual or product page, have it extract the actual mapping,
implement the translation layer, and -- critically -- verify the result
against the real hardware rather than trusting the documentation. Most of
`bank_plan.py`, the patch JSON, and this README were produced that way, in
a Claude Code session, with me stepping through the actual gear and
reporting back what happened.

That verification step mattered. Two bugs in the current bank plan were
found only by testing against real hardware, not by reading a manual harder:

- **Voodoo Lab's manual says CC80-83 map to switches 1-4 in order** -- that
  part was correct. What it doesn't say is which of *my* amp's functions
  each of those switches is wired to via the BTPA cable. I assumed switch 1
  = channel, switch 3 = Solo based on the cable's own product description,
  then had Claude walk me through pressing each Control Switcher button by
  hand while I listened to the amp. Marshall's channel relay came back
  inverted from what was assumed -- closed selects clean, not dirty.
  Bandit's matched the assumption. One amp being wired backwards from the
  other wasn't something any documentation was going to reveal; it only
  showed up by testing each relay individually against the actual amp.
- **A stateful CC has to be sent on every patch, not just when you want it
  engaged.** The Solo-mute CC only fires when a patch needs Mesa muted;
  every other patch just didn't send it at all, on the assumption that "not
  sent" meant "no change requested." Voodoo Lab's relay doesn't work that
  way -- it holds whatever the last CC set it to, so skipping the message
  left Mesa muted after leaving a muted patch. Once I noticed the symptom
  (Mesa still muted after switching back to a "Mesa clean" patch) the fix
  was mechanical: send an explicit 0 on every patch where Mesa should be
  audible, the same way the channel-select CC always was.

Both are now committed as explicit comments in `bank_plan.py` at the line
that encodes them, not just in this file, so the reasoning survives the
next person (including future-me) reading the code cold.

## Adapting this to a different rig

The reusable part isn't the Mesa/Peavey data, it's the shape:
patch data as JSON, a compiler that maps it onto the FCB1010's fixed
per-preset slots, with the actual CC/PC semantics for your specific
downstream gear established by testing, not assumed from a manual. To do
this for different gear:

1. Get the manual (or product page) for whatever you're driving via MIDI,
   and pull the actual CC/PC assignments out of it -- an LLM reading a PDF
   and producing a structured mapping is a lot faster than doing it by hand.
2. Verify every assignment you're about to depend on with
   `send_test_cc.py`/`send_test_pc.py` before writing a full patch dataset
   around it. Docs describe intent; wiring and relay polarity are physical
   facts that can and do disagree with intent.
3. Write your own patch JSON -- the field names in
   `data/fcb1010-patch-data.json` are specific to this rig, not a schema to
   conform to.
4. Fork `bank_plan.py`'s `apply_patch_data`: same shape (iterate patches,
   write `preset.pc1_enabled`/`pc1_program`, `preset.cc1_*`/`cc2_*`,
   `preset.switch1_enabled`/`switch2_enabled`), different field sources.
   `load_patch_data`, `_clear_preset`, and `PLANNED_BANKS` (limiting which
   banks get touched) carry over unchanged.
5. Set the device-wide MIDI channels (`fcb.pc1_midi_channel`, etc.) to
   whatever your gear listens on -- see the channel-indexing note below.

## Hardware facts that only surfaced through testing

- MIDI channel is stored as a 0-indexed byte: channel 1 is byte value `0`.
  Standard MIDI status-byte convention, but worth confirming rather than
  assuming, since it's the kind of off-by-one that fails silently.
- `switch1_enabled`/`switch2_enabled` are *not* inverted in the raw SysEx
  the way the PC/CC enable flags are (see `parse_sysex`/`get_raw_sysex`) --
  a genuine asymmetry in riban-bw's reverse-engineered format, not a bug.
- Relay polarity is per-device, not a property of "the FCB1010's relay
  output" in general -- see the Marshall/Bandit inversion above.
- A CC that toggles a stateful relay needs to be sent with an explicit
  value on every preset that cares about its state, not only on the presets
  that need to change it -- see the Solo-mute bug above.

---

Everything below is riban-bw's original usage example for `fcb1010.py`,
unchanged:

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

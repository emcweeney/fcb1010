# FCB1010 project notes

Behringer FCB1010 footswitch programming: a JSON patch dataset compiles to a CSV,
which is sent to the pedal as SysEx. Full docs are in `README.md`.

## What is on the pedal / what was sent

For any question about what was sent to the pedal, what it currently holds, or
how a past config differed, run `python3 scripts/history.py` first (add `N` or
`A B` to diff), then read the "Config history" section of `README.md`. History
is git (committed plan/read-back CSVs; the commit message is the description)
merged with the log of sends and dumps. Rules that are easy to get wrong:
git alone does not show that a plan was sent (only the log, or a read-back that
matches the plan, does), the same hash means an identical pedal state, and
`bank_plan.py` alone never touches the pedal. Each send/dump also leaves a dated
backup CSV in `dumps/history/` (tracked in git) that can be sent back to the pedal.

## Working in this repo

- `scripts/fcb1010.py` is riban-bw's SysEx/CSV engine for **stock V2.5 firmware**
  only. Don't modify it for features; build on its API.
- Source of truth for the rig is `data/fcb1010-patch-data.json`; the CSVs in
  `dumps/` are generated or read back from the device.
- Run scripts from the repo root. Send and dump need the pedal and a MIDI port,
  so don't run them as tests.
- `origin` is the user's fork; `upstream` is riban-bw's repo. Only push when asked.
- Commits are authored as the user with no Claude co-author trailer.

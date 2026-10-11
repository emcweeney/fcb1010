#   Show the FCB1010 send/dump log and diff snapshots
#
#   Usage:
#     python3 history.py          List logged events
#     python3 history.py N        Diff event N against the event before it
#     python3 history.py A B      Diff event A against event B
#   Negative indexes count from the end (-1 is the latest event).
#   Bank/Preset numbers match the CSV (both 1-based).

import sys

from fcb1010 import fcb1010
from fcb_log import ROOT, read_log


def list_events(entries):
    if not entries:
        print("No events logged yet.")
        return
    for i, e in enumerate(entries):
        note = ""
        if "matches_last_send" in e:
            note = "  matches last send" if e["matches_last_send"] else "  DIFFERS from last send"
        dirty = "*" if e.get("git_dirty") else ""
        print(f"{i:3}  {e['ts']}  {e['action']:<4}  {e['sha256'][:8]}  "
              f"{e.get('git_commit')}{dirty}  {e.get('description') or e.get('source') or ''}{note}")


def load_snapshot(entry):
    fcb = fcb1010()
    if not fcb.load(str(ROOT / entry["snapshot"])):
        sys.exit(f"Could not load {entry['snapshot']}")
    return fcb


def diff(a, b):
    changes = []
    for name, old in vars(a).items():
        if name != "preset" and old != getattr(b, name):
            changes.append(f"Global: {name} {old} -> {getattr(b, name)}")
    for i, (pa, pb) in enumerate(zip(a.preset, b.preset)):
        for name, old in vars(pa).items():
            new = getattr(pb, name)
            if old != new:
                changes.append(f"Bank {i // 10 + 1} Preset {i % 10 + 1}: {name} {old} -> {new}")
    return changes


def main():
    entries = read_log()
    args = [int(a) for a in sys.argv[1:]]
    if not args:
        list_events(entries)
        return
    try:
        if len(args) == 1:
            i = args[0] % len(entries)
            if i == 0:
                sys.exit("Event 0 has no earlier event to diff against.")
            old, new = entries[i - 1], entries[i]
        else:
            old, new = entries[args[0]], entries[args[1]]
    except (IndexError, ZeroDivisionError):
        sys.exit("No such event; run without arguments to list them.")

    print(f"{old['ts']} {old['action']}  ->  {new['ts']} {new['action']}")
    changes = diff(load_snapshot(old), load_snapshot(new))
    print("\n".join(changes) if changes else "No differences.")


if __name__ == "__main__":
    main()

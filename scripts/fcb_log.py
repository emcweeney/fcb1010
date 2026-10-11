#   Event log for FCB1010 sends and dumps
#
#   Every send or dump that changes what the log knows about the pedal appends
#   one JSON line to dumps/fcb1010.log.jsonl and saves a snapshot of the exact
#   data under dumps/history/, so any two events can be compared later with
#   history.py. A send or dump identical to the latest entry adds no line: a
#   dump just stamps that entry `confirmed_at`, a send is skipped.

import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DUMPS_DIR = ROOT / "dumps"
HISTORY_DIR = DUMPS_DIR / "history"
LOG_FILE = DUMPS_DIR / "fcb1010.log.jsonl"


def sysex_hash(fcb):
    return hashlib.sha256(bytes(fcb.get_raw_sysex())).hexdigest()


def read_log():
    if not LOG_FILE.exists():
        return []
    with open(LOG_FILE) as f:
        return [json.loads(line) for line in f if line.strip()]


def _write_log(entries):
    # Temp file + rename, so an interrupted rewrite can't leave a half-written log
    tmp = LOG_FILE.with_suffix(".jsonl.tmp")
    with open(tmp, "w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")
    tmp.replace(LOG_FILE)


def _is_uncommitted(path):
    try:
        out = subprocess.run(["git", "status", "--porcelain", "--", str(Path(path).resolve())],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout
        return bool(out.strip())
    except (OSError, subprocess.CalledProcessError):
        return False


def _git_state():
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                                capture_output=True, text=True, check=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                                    capture_output=True, text=True, check=True).stdout.strip())
        return commit, dirty
    except (OSError, subprocess.CalledProcessError):
        return None, None


def log_event(action, fcb, source=None, port=None):
    """Record a 'send' or 'dump' of fcb. Never raises: logging must not block a send/dump."""
    try:
        now = datetime.now().astimezone()
        digest = sysex_hash(fcb)
        entries = read_log()
        last_send = next((e for e in reversed(entries) if e["action"] == "send"), None)

        last = entries[-1] if entries else None
        if last and last["sha256"] == digest:
            if action == "send":
                print("Pedal already has this config (identical to the latest log entry); not logged again.")
            elif last["action"] in ("send", "import") and "confirmed_at" not in last:
                last["confirmed_at"] = now.isoformat(timespec="seconds")
                _write_log(entries)
                print(f"Dump matches the latest {last['action']} ({last['ts']}); stamped it confirmed.")
            else:
                print("Dump unchanged since the latest log entry; not logged again.")
            return None

        snapshot = HISTORY_DIR / f"{now.strftime('%Y%m%d-%H%M%S')}_{action}.csv"
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        if not fcb.save(str(snapshot)):
            raise OSError(f"could not write snapshot {snapshot}")

        commit, dirty = _git_state()
        entry = {
            "ts": now.isoformat(timespec="seconds"),
            "action": action,
            "sha256": digest,
            "snapshot": str(snapshot.relative_to(ROOT)),
            "source": source,
            "port": port,
            "git_commit": commit,
            "git_dirty": dirty,
        }
        if action == "dump" and last_send:
            entry["matches_last_send"] = digest == last_send["sha256"]
            entry["last_send_ts"] = last_send["ts"]

        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
        print(f"Logged {action} to {LOG_FILE.relative_to(ROOT)} ({snapshot.name})")
        if source and _is_uncommitted(source):
            print(f"Note: {source} has uncommitted changes. Commit it (the message is this "
                  f"config's description); the snapshot above keeps a copy either way.")
        return entry
    except Exception as e:
        print(f"Warning: failed to log {action}: {e}")
        return None

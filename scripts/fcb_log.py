#   Event log for FCB1010 sends and dumps
#
#   Every send or dump appends one JSON line to dumps/fcb1010.log.jsonl and
#   saves a snapshot of the exact data under dumps/history/, so any two events
#   can be compared later with history.py.

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
        return entry
    except Exception as e:
        print(f"Warning: failed to log {action}: {e}")
        return None

#   Activity log for FCB1010 sends and dumps
#
#   Every send to the pedal and every dump from it appends one JSON line to
#   dumps/fcb1010.log.jsonl and saves a dated backup of that exact config under
#   dumps/history/. Repeats are logged too; nothing is skipped or edited. The
#   same config always gives the same sha256 (a hash of the SysEx bytes).

import hashlib
import json
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


def _backup_path(now, action, digest):
    """Dated, unique name: 2026-10-12_1832_send_1a189f09.csv (-2, -3... if the minute repeats)."""
    base = f"{now.strftime('%Y-%m-%d_%H%M')}_{action}_{digest[:8]}"
    path = HISTORY_DIR / f"{base}.csv"
    n = 2
    while path.exists():
        path = HISTORY_DIR / f"{base}-{n}.csv"
        n += 1
    return path


def _relative(path):
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def log_event(action, fcb, source=None, port=None):
    """Record a 'send' or 'dump' of fcb. Never raises: logging must not block a send/dump."""
    try:
        now = datetime.now().astimezone()
        digest = sysex_hash(fcb)

        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        backup = _backup_path(now, action, digest)
        if not fcb.save(str(backup)):
            raise OSError(f"could not write backup {backup}")

        entry = {
            "ts": now.isoformat(timespec="seconds"),
            "action": action,
            "sha256": digest,
            "source": _relative(source) if source else None,
            "port": port,
            "backup": _relative(backup),
        }
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
        print(f"Logged {action} {digest[:8]}; backup: {entry['backup']}")
        return entry
    except Exception as e:
        print(f"Warning: failed to log {action}: {e}")
        return None

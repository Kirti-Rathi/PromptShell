import os
import json
from datetime import datetime
from .setup import CONFIG_DIR

HISTORY_FILE = os.path.join(CONFIG_DIR, "history.jsonl")
MAX_HISTORY = 100

def append_history(natural_language, shell_command):
    """Append a new entry to the history file, keeping only the last 100 entries."""
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "natural_language": natural_language,
        "shell_command": shell_command
    }
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    history.append(json.loads(line))
                except Exception:
                    continue
    history.append(entry)
    # Keep only the last MAX_HISTORY entries
    history = history[-MAX_HISTORY:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        for item in history:
            f.write(json.dumps(item) + "\n")

def get_last_n_history(n=10):
    """Return the last n entries from the history file (most recent last)."""
    if not os.path.exists(HISTORY_FILE):
        return []
    history = []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                history.append(json.loads(line))
            except Exception:
                continue
    return history[-n:] if n > 0 else history 
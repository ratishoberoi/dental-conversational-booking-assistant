import json
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def log_conversation(user_id: str, history):

    fname = LOG_DIR / f"{user_id}_{datetime.utcnow().timestamp()}.json"

    with open(fname, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

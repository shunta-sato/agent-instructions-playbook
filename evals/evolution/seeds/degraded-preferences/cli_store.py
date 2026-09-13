import json
import os
from pathlib import Path

def path():
    return Path(os.environ["PREFS_FILE"])

def save(value):
    if not isinstance(value, str):
        raise ValueError("value must be a string")
    if not value:
        raise ValueError("value cannot be empty")
    path().write_text(json.dumps({"value": value}), encoding="utf-8")

def load():
    data = json.loads(path().read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("value"), str):
        raise ValueError("invalid stored value")
    return data["value"]

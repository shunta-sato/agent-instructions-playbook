"""Retirement plus preserved external API; semantic ownership still needs review."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from preferences_oracle import verify


def check(root: Path, stage: str) -> None:
    if stage not in {"rehabilitate", "rehab-normalize"}:
        raise ValueError("Unknown rehabilitation stage")
    verify(root, stage)
    retired = root / "unused_compat.py"
    assert not retired.exists() and not retired.is_symlink(), "authorized retirement incomplete"
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "prefs.json"
        path.write_text(json.dumps({"value": " preserved 日本語 "}))
        env = dict(os.environ, PREFS_FILE=str(path), PYTHONDONTWRITEBYTECODE="1")
        output = subprocess.run(
            [sys.executable, "-S", "-c", "from public_v1 import read_value; print(read_value())"],
            cwd=root, env=env, text=True, capture_output=True, timeout=5,
        )
        assert output.returncode == 0 and output.stdout == " preserved 日本語 \n", output
        assert not output.stderr


if __name__ == "__main__":
    check(Path(sys.argv[1]).resolve(), sys.argv[2])

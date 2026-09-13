"""Independent cumulative public-boundary checks; not a code-style/ownership judge."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


if not __debug__:
    raise RuntimeError("The acceptance oracle requires enabled assertions")


def verify(root: Path, stage: str) -> None:
    if stage not in {"cli", "batch", "normalize", "rehabilitate", "rehab-normalize"}:
        raise ValueError("Unknown stage")
    batch = stage != "cli"
    normalize = stage in {"normalize", "rehab-normalize"}
    with tempfile.TemporaryDirectory() as tmp:
        store = Path(tmp) / "prefs.json"
        env = dict(os.environ, PREFS_FILE=str(store), PYTHONDONTWRITEBYTECODE="1")

        def call(entry: str, op: str, value=None, environment=None):
            argv = [sys.executable, "-S", str(root / entry)]
            data = ""
            if entry == "cli.py":
                argv.append(op)
                if value is not None:
                    argv.append(value)
            else:
                request = {"op": op}
                if value is not None:
                    request["value"] = value
                data = json.dumps(request)
            return subprocess.run(argv, input=data, text=True, capture_output=True,
                                  cwd=root, env=env if environment is None else environment, timeout=5)

        def failed(output):
            assert output.returncode != 0 and output.stderr and not output.stdout, output

        entries = ["cli.py", "batch.py"] if batch else ["cli.py"]
        for entry in entries:
            missing = {k: v for k, v in env.items() if k != "PREFS_FILE"}
            failed(call(entry, "get", environment=missing))
            store.unlink(missing_ok=True)
            failed(call(entry, "get"))
        for writer in entries:
            for value in ["hello", "  A  B  ", "\u2003日本語\u2003"]:
                output = call(writer, "set", value)
                assert output.returncode == 0 and not output.stderr, output
                assert output.stdout == "" if writer == "cli.py" else json.loads(output.stdout) == {"ok": True}
                expected = value.strip() if normalize else value
                assert json.loads(store.read_text()) == {"value": expected}
                for reader in entries:
                    output = call(reader, "get")
                    assert output.returncode == 0 and not output.stderr, output
                    actual = output.stdout[:-1] if reader == "cli.py" else json.loads(output.stdout)["value"]
                    assert output.stdout.endswith("\n") and actual == expected, output
            before = store.read_bytes()
            for value in (["", " \t\n"] if normalize else [""]):
                failed(call(writer, "set", value))
                assert store.read_bytes() == before
            failed(call(writer, "unknown"))
            assert store.read_bytes() == before
        for broken in ['not json', '{"value": 42}', '{}', '[]']:
            store.write_text(broken)
            for entry in entries:
                failed(call(entry, "get"))
                assert store.read_text() == broken
        # Normalization is a write rule, not permission to alter legacy stored values on read.
        store.write_text(json.dumps({"value": " old "}))
        for entry in entries:
            output = call(entry, "get")
            assert output.returncode == 0
            assert (output.stdout == " old \n" if entry == "cli.py"
                    else json.loads(output.stdout) == {"value": " old "})
        if batch:
            for request in ['bad', '[]', '{"op":"set","value":3}', '{"op":"set"}']:
                before = store.read_bytes()
                output = subprocess.run([sys.executable, "-S", str(root / "batch.py")], input=request,
                                        text=True, capture_output=True, cwd=root, env=env, timeout=5)
                failed(output)
                assert store.read_bytes() == before


if __name__ == "__main__":
    verify(Path(sys.argv[1]).resolve(), sys.argv[2])

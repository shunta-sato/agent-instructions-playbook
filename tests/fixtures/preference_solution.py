"""Trusted reference implementation for tests only; never supplied to a trial agent."""
from __future__ import annotations

from textwrap import dedent


def solution(normalize: bool = False) -> dict[str, str]:
    store = dedent('''\
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
        ''')
    if normalize:
        store = store.replace('    if not value:\n', '    value = value.strip()\n    if not value:\n')
    return {
        "store.py": store,
        "cli.py": dedent('''\
            import sys
            from store import load, save

            try:
                if len(sys.argv) == 3 and sys.argv[1] == "set":
                    save(sys.argv[2])
                elif sys.argv[1:] == ["get"]:
                    print(load())
                else:
                    raise ValueError("expected set VALUE or get")
            except (OSError, ValueError, KeyError) as error:
                print(str(error), file=sys.stderr)
                raise SystemExit(1)
            '''),
        "batch.py": dedent('''\
            import json
            import sys
            from store import load, save

            try:
                request = json.load(sys.stdin)
                if not isinstance(request, dict):
                    raise ValueError("request must be an object")
                if request.get("op") == "set":
                    save(request["value"])
                    response = {"ok": True}
                elif request.get("op") == "get":
                    response = {"value": load()}
                else:
                    raise ValueError("invalid operation")
                print(json.dumps(response))
            except (OSError, ValueError, KeyError) as error:
                print(str(error), file=sys.stderr)
                raise SystemExit(1)
            '''),
    }

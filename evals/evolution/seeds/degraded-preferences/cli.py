import sys
from cli_store import load, save

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

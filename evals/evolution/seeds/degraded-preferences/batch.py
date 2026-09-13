import json
import sys
from batch_store import load, save

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

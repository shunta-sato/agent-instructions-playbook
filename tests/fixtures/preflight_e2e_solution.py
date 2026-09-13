"""Reference fixture solution for testing the evaluator, never a live-model result."""
import json
from pathlib import Path
import sys


def main():
    config = Path('settings.json')
    if not config.is_file():
        print('ENV_NOT_READY: settings.json missing', file=sys.stderr)
        return 3
    settings = json.loads(config.read_text())
    store = Path(settings['store'])
    command = sys.argv[1] if len(sys.argv) > 1 else ''
    if command == 'health':
        print('ready')
        return 0
    if command == 'set' and len(sys.argv) == 3:
        store.write_text(json.dumps({'value': sys.argv[2]}), encoding='utf-8')
        print('saved')
        return 0
    if command == 'get':
        value = json.loads(store.read_text(encoding='utf-8'))['value'] if store.exists() else ''
        print(value)
        return 0
    print('usage: app.py health|set VALUE|get', file=sys.stderr)
    return 2


if __name__ == '__main__':
    raise SystemExit(main())

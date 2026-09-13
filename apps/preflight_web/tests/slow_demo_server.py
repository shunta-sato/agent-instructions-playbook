"""Deterministic cancellation fixture for browser E2E; never a production provider."""
from __future__ import annotations

import argparse
from pathlib import Path

from apps.preflight_web.providers import DemoProvider, DialogueCancelled
from apps.preflight_web.server import ConsoleServer
from apps.preflight_web.state import SessionStore


class SlowDemoProvider(DemoProvider):
    label = 'デモ・取消し試験用（AI未接続）'

    def respond(self, state, cancelled=None):
        if state['messages'][-1]['text'] == '停止テスト':
            if cancelled is None or not cancelled.wait(20):
                raise TimeoutError('Fixture requires explicit cancellation')
            raise DialogueCancelled()
        return super().respond(state, cancelled)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-dir', type=Path, required=True)
    parser.add_argument('--port', type=int, default=0)
    args = parser.parse_args()
    store = SessionStore(args.state_dir / 'session.sqlite3')
    server = ConsoleServer(store, SlowDemoProvider(), args.port)
    print(f'{server.origin}/#token={server.token}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        store.close()


if __name__ == '__main__':
    main()

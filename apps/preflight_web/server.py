"""Loopback-only local UI. No shell, project-write or approval-forwarding endpoint."""
from __future__ import annotations

import argparse
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import secrets
import threading
from urllib.parse import parse_qs, urlsplit

from .providers import DemoProvider
from .state import Conflict, SessionStore

STATIC = Path(__file__).parent / 'static'
ASSETS = {'/': ('index.html', 'text/html'), '/app.js': ('app.js', 'text/javascript'),
          '/style.css': ('style.css', 'text/css')}
MAX_BODY = 65536


class ConsoleServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False

    def __init__(self, store, provider, port=8765, token=None):
        self.store, self.provider = store, provider
        self.token = token or secrets.token_urlsafe(32)
        self.worker = None
        super().__init__(('127.0.0.1', port), Handler)
        self.origin = f'http://127.0.0.1:{self.server_port}'

    def reply(self, state):
        try:
            self.store.finish_message(self.provider.respond(state))
        except Exception:
            # Keep provider transport errors and credentials out of HTTP responses.
            self.store.fail_message('対話接続に失敗または中断しました。自動再送・自動承認はしていません。接続設定を確認してください。')

    def server_close(self):
        self.provider.close()
        if self.worker:
            self.worker.join(timeout=5)
        super().server_close()


class Handler(BaseHTTPRequestHandler):
    server: ConsoleServer

    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def send(self, status: int, body: bytes | dict, content_type='application/json'):
        if isinstance(body, dict):
            body = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', content_type + '; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; "
                         "connect-src 'self'; img-src 'none'; object-src 'none'; base-uri 'none'; "
                         "frame-ancestors 'none'; form-action 'self'")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass  # A disconnect never mutates the agreement.

    def guard(self, authenticated=True):
        if (self.headers.get('Host') != urlsplit(self.server.origin).netloc
                or self.headers.get('Origin') not in (None, self.server.origin)
                or self.headers.get('Sec-Fetch-Site') == 'cross-site'):
            self.send(403, {'error': '別サイト・不正なホストからのアクセスは拒否しました。'})
            return False
        expected = ('Bearer ' + self.server.token).encode()
        supplied = self.headers.get('Authorization', '').encode()
        if authenticated and not hmac.compare_digest(supplied, expected):
            self.send(401, {'error': '起動時に表示されたURLで接続してください。'})
            return False
        return True

    def state(self):
        return dict(self.server.store.read(), provider=self.server.provider.name,
                    provider_label=self.server.provider.label,
                    verification_status='not-run', execution_authorized=False)

    def do_GET(self):
        path = urlsplit(self.path).path
        if not self.guard(authenticated=path not in ASSETS):
            return
        if path in ASSETS:
            filename, mime = ASSETS[path]
            self.send(200, (STATIC / filename).read_bytes(), mime)
        elif path == '/api/state':
            self.send(200, self.state())
        elif path == '/api/handoff':
            try:
                revisions = parse_qs(urlsplit(self.path).query).get('revision', [])
                if len(revisions) != 1:
                    raise ValueError('表示中のrevisionが必要です。')
                self.send(200, self.server.store.handoff(int(revisions[0])))
            except Conflict as exc:
                self.send(409, {'error': str(exc)})
            except ValueError as exc:
                self.send(400, {'error': str(exc)})
        else:
            self.send(404, {'error': 'その機能はありません。'})

    def do_POST(self):
        if not self.guard():
            return
        if self.headers.get('Transfer-Encoding'):
            self.send(400, {'error': 'Transfer-Encoding is unsupported'}); return
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            self.send(415, {'error': 'JSONのみ受理します。'}); return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= MAX_BODY:
                self.send(413, {'error': '入力サイズが範囲外です。'}); return
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError('JSON object required')
            path = urlsplit(self.path).path
            if path == '/api/messages':
                state = self.server.store.begin_message(data.get('revision'), data.get('text'))
                self.server.worker = threading.Thread(target=self.server.reply, args=(state,), daemon=True)
                self.server.worker.start()
            elif path == '/api/draft':
                self.server.store.edit(data.get('revision'), data.get('fields'))
            elif path == '/api/approve':
                self.server.store.approve(data.get('revision'), data.get('reviewed'))
            else:
                self.send(404, {'error': 'その操作はありません。'}); return
            self.send(200, self.state())
        except Conflict as exc:
            self.send(409, {'error': str(exc)})
        except (ValueError, TypeError, UnicodeError) as exc:
            self.send(400, {'error': str(exc)})

    def log_message(self, *_):
        pass  # Never log chats, tokens, request targets or model output by default.


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-dir', type=Path, default=Path.home() / '.local/state/playbook-preflight')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--provider', choices=('demo', 'codex'), default='demo')
    parser.add_argument('--codex', default='codex', help='Operator-selected Codex binary, never from the browser')
    parser.add_argument('--codex-home', type=Path, help='Dedicated, operator-provisioned login home')
    parser.add_argument('--model', help='Explicit model for the experimental Codex connection')
    parser.add_argument('--live-sandbox-confirmed', action='store_true', help='Operator has confined the live runtime')
    args = parser.parse_args()
    if args.state_dir.is_symlink():
        parser.error('state-dir must not be a symlink')
    args.state_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(args.state_dir, 0o700)
    # POSIX-only MVP: refuse simultaneous servers on the same session database.
    import fcntl
    lock = (args.state_dir / 'server.lock').open('a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        parser.error('This state-dir is already in use')
    if args.provider == 'codex':
        if not args.model or not args.codex_home or not args.live_sandbox_confirmed:
            parser.error('Codex needs --model, dedicated --codex-home and --live-sandbox-confirmed')
        from .codex import CodexProvider
        try:
            provider = CodexProvider(args.codex, args.model, args.codex_home)
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
    else:
        provider = DemoProvider()
    store = SessionStore(args.state_dir / 'session.sqlite3')
    server = ConsoleServer(store, provider, args.port)
    print(f'{server.origin}/#token={server.token}', flush=True)
    print(f'{provider.label} / 合意のみ・実行機能なし / 終了: Ctrl+C', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        store.close()
        lock.close()


if __name__ == '__main__':
    main()

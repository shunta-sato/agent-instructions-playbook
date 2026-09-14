"""Experimental Codex App Server dialogue adapter; live compatibility is unverified.

The operator must separately confine the runtime. Read-only/disabled tools are
requested as defense in depth, not a claim that this Python client is a sandbox.
"""
from __future__ import annotations

from collections import deque
import json
import os
from pathlib import Path
import queue
import shutil
import signal
import subprocess
import tempfile
import threading
import time

from .providers import DialogueCancelled, INSTRUCTIONS, REPLY_SCHEMA, validate_reply

MAX_LINE = 1_000_000


class CodexProvider:
    name = 'codex'

    def __init__(self, executable: str, model: str, home: Path, timeout: float = 180):
        resolved = shutil.which(executable)
        if not resolved:
            raise ValueError('Codex binary is missing; install and verify it explicitly. No fallback to demo.')
        home = home.resolve(strict=True)
        if home == (Path.home() / '.codex').resolve():
            raise ValueError('Use a dedicated Codex login home, not your normal development profile')
        for name in ('config.toml', 'AGENTS.md', 'AGENTS.override.md', 'skills', 'plugins', 'rules'):
            if (home / name).exists() or (home / name).is_symlink():
                raise ValueError(f'Dedicated Codex home must not contain {name}; provision a clean login home')
        if not model.strip():
            raise ValueError('Explicit model required')
        self.executable, self.model, self.home = resolved, model, home
        self.timeout = timeout
        self.env = {key: value for key, value in os.environ.items()
                    if key in ('PATH', 'HOME', 'USER', 'LANG', 'LC_ALL', 'TMPDIR', 'SYSTEMROOT')}
        self.env['CODEX_HOME'] = str(home)
        self.version = subprocess.run([resolved, '--version'], capture_output=True, text=True,
                                      timeout=10, env=self.env, check=True).stdout.strip()
        self.label = f'Codex · {model} · 実験的な対話接続'
        self.scratch = tempfile.TemporaryDirectory(prefix='preflight-dialogue-')
        self.process = None
        self.thread_id = None
        self.serial = 0
        self.events = None
        self.deferred = deque()
        self.cancelled = threading.Event()
        self.reader = None

    def _start(self):
        args = [self.executable, 'app-server', '--listen', 'stdio://']
        for feature in ('shell_tool', 'unified_exec', 'shell_snapshot', 'apps', 'plugins', 'multi_agent'):
            args += ['-c', f'features.{feature}=false']
        args += ['-c', 'web_search="disabled"', '-c', 'mcp_servers={}']
        self.process = subprocess.Popen(args, cwd=self.scratch.name, env=self.env,
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL, text=True,
                                        encoding='utf-8', start_new_session=True)
        self.events = queue.Queue(maxsize=1000)
        self.deferred.clear()
        stream, events = self.process.stdout, self.events

        def read():
            try:
                while True:
                    line = stream.readline(MAX_LINE + 1)
                    if not line:
                        raise RuntimeError('Codex transport ended')
                    if len(line) > MAX_LINE:
                        raise RuntimeError('Codex message exceeds limit')
                    event = json.loads(line)
                    if not isinstance(event, dict):
                        raise ValueError('Codex event is not an object')
                    events.put(event, timeout=2)
            except Exception:
                try:
                    events.put(RuntimeError('Codex transport unavailable'), timeout=1)
                except queue.Full:
                    pass
        self.reader = threading.Thread(target=read, daemon=True)
        self.reader.start()

    def _send(self, payload):
        self.process.stdin.write(json.dumps(payload, ensure_ascii=False) + '\n')
        self.process.stdin.flush()

    def _receive(self, deadline):
        # Poll the cancellation event even when the transport is silent.
        while True:
            if self.cancelled.is_set():
                raise DialogueCancelled()
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('Codex dialogue deadline exceeded')
            try:
                event = self.events.get(timeout=min(remaining, 0.1))
                break
            except queue.Empty:
                continue
        if isinstance(event, Exception):
            raise event
        if 'id' in event and 'method' in event:
            self._send({'id': event['id'], 'error': {'code': -32601,
                        'message': 'Discussion only: no tool approvals, permissions or execution requests are accepted.'}})
            raise RuntimeError('Codex requested an unsupported interactive action; nothing was approved')
        return event

    def _request(self, method, params, deadline):
        if self.cancelled.is_set():
            raise DialogueCancelled()
        self.serial += 1
        identifier = self.serial
        self._send({'id': identifier, 'method': method, 'params': params})
        while True:
            event = self._receive(deadline)
            if event.get('id') == identifier:
                if 'error' in event:
                    raise RuntimeError('Codex rejected the protocol or requested policy; no relaxation attempted')
                return event['result']
            self.deferred.append(event)
            if len(self.deferred) > 1000:
                raise RuntimeError('Excessive protocol notifications')

    def respond(self, state: dict, cancelled: threading.Event | None = None) -> dict:
        self.cancelled = cancelled if cancelled is not None else threading.Event()
        deadline = time.monotonic() + self.timeout
        try:
            if self.cancelled.is_set():
                raise DialogueCancelled()
            new_thread = self.process is None or self.process.poll() is not None
            if new_thread:
                if self.process is not None:
                    self._stop_process()
                self._start()
                self._request('initialize', {'clientInfo': {'name': 'playbook_preflight',
                              'title': 'Preflight Console', 'version': '0.2.0'}}, deadline)
                self._send({'method': 'initialized', 'params': {}})
                result = self._request('thread/start', {'model': self.model,
                    'cwd': self.scratch.name, 'approvalPolicy': 'never', 'sandbox': 'read-only',
                    'developerInstructions': INSTRUCTIONS}, deadline)
                if result.get('model') != self.model:
                    raise RuntimeError('Missing or unexpected resolved model')
                self.thread_id = result['thread']['id']
            context = {'draft': state['draft'], 'confirmation': 'not execution authorization',
                       'messages': state['messages'] if new_thread else state['messages'][-1:]}
            turn = self._request('turn/start', {'threadId': self.thread_id, 'model': self.model,
                'approvalPolicy': 'never', 'sandboxPolicy': {'type': 'readOnly', 'access': {
                    'type': 'restricted', 'includePlatformDefaults': False,
                    'readableRoots': [self.scratch.name]}},
                'input': [{'type': 'text', 'text': json.dumps(context, ensure_ascii=False)}],
                'outputSchema': REPLY_SCHEMA}, deadline)['turn']['id']
            final = None
            while True:
                if self.cancelled.is_set():
                    raise DialogueCancelled()
                event = self.deferred.popleft() if self.deferred else self._receive(deadline)
                params = event.get('params', {})
                if params.get('threadId') not in (None, self.thread_id):
                    continue
                if params.get('turnId') not in (None, turn):
                    continue
                if event.get('method') == 'item/completed' and params.get('item', {}).get('type') == 'agentMessage':
                    final = params['item']['text']
                if event.get('method') == 'turn/completed' and params.get('turn', {}).get('id') == turn:
                    if params['turn']['status'] != 'completed' or final is None:
                        raise RuntimeError('Codex turn did not complete with a response')
                    return validate_reply(json.loads(final))
        except Exception:
            self._stop_process()
            raise

    def _stop_process(self):
        process, self.process = self.process, None
        self.thread_id = None
        if process is None:
            return
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait(timeout=2)
        if self.reader:
            self.reader.join(timeout=3)
        for stream in (process.stdin, process.stdout):
            if stream:
                stream.close()

    def close(self):
        self._stop_process()
        self.scratch.cleanup()

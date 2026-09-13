"""Server-owned, revision-bound agreement state; model output is only a proposal."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import threading

FIELDS = ('outcome', 'non_goals', 'acceptance', 'constraints', 'environment', 'authority')


class Conflict(ValueError):
    """A stale revision or an unfinished turn prevents the requested transition."""


def text(value: object, limit: int = 8000) -> str:
    if not isinstance(value, str) or len(value) > limit or '\x00' in value:
        raise ValueError('文字列が不正、または長すぎます。')
    return value


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SessionStore:
    """One local conversation per database; all mutations are transactional."""

    def __init__(self, path: Path):
        self.lock = threading.RLock()
        if path.is_symlink():
            raise ValueError('Refusing a symlinked session database')
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        os.chmod(path, 0o600)
        self.closed = False
        self.db.execute('CREATE TABLE IF NOT EXISTS session (id INTEGER PRIMARY KEY, body TEXT NOT NULL)')
        initial = {'schema_version': 1, 'revision': 0, 'draft': dict.fromkeys(FIELDS, ''),
                   'messages': [], 'proposals': [], 'approval': None, 'history': [],
                   'busy': False, 'error': None}
        self.db.execute('INSERT OR IGNORE INTO session VALUES (1, ?)', (json.dumps(initial),))
        self.db.commit()
        state = self.read()
        if state['schema_version'] != 1:
            self.close()
            raise ValueError('Unsupported session schema')
        if state['busy']:
            self.fail_message('前回の対話は中断されました。自動再送はしていません。')

    def close(self):
        with self.lock:
            if not self.closed:
                self.db.close()
                self.closed = True

    def read(self) -> dict:
        with self.lock:
            return json.loads(self.db.execute('SELECT body FROM session WHERE id=1').fetchone()[0])

    def _write(self, state: dict, kind: str, actor: str, detail: dict | None = None) -> dict:
        state['revision'] += 1
        state['history'].append({'revision': state['revision'], 'kind': kind, 'actor': actor,
                                 'at': now(), 'detail': detail or {}})
        payload = json.dumps(state, ensure_ascii=False)
        if len(payload.encode()) > 2_000_000:
            raise ValueError('会話の保存上限です。新しいstate-dirで別セッションを開始してください。')
        with self.db:
            self.db.execute('UPDATE session SET body=? WHERE id=1', (payload,))
        return deepcopy(state)

    def _check(self, revision: int) -> dict:
        state = self.read()
        if type(revision) is not int or revision != state['revision']:
            raise Conflict('別の画面または対話で内容が更新されました。最新の差分を確認してください。')
        if state['busy']:
            raise Conflict('応答中です。対話が終わってから内容を確認してください。')
        return state

    def begin_message(self, revision: int, message: str) -> dict:
        message = text(message).strip()
        if not message:
            raise ValueError('質問・説明・希望を入力してください。')
        with self.lock:
            state = self._check(revision)
            if sum(len(m['text']) for m in state['messages']) + len(message) > 100_000:
                raise ValueError('会話が長くなりました。内容を整理して別セッションへ引き継いでください。')
            state['messages'].append({'role': 'user', 'text': message, 'at': now()})
            state.update(busy=True, error=None, approval=None)
            return self._write(state, 'message', 'human')

    def finish_message(self, reply: dict) -> dict:
        # This method has no approval parameter or execution callback.
        from .providers import validate_reply
        reply = validate_reply(reply)
        with self.lock:
            state = self.read()
            if not state['busy']:
                raise Conflict('この応答は既に中断されています。')
            state['messages'].append({'role': 'assistant', 'text': reply['reply'], 'at': now()})
            state['proposals'] = reply['proposals']
            state.update(busy=False, error=None)
            return self._write(state, 'reply', 'assistant', {'proposals': reply['proposals']})

    def fail_message(self, error: str) -> dict:
        with self.lock:
            state = self.read()
            state.update(busy=False, approval=None, error=text(error))
            return self._write(state, 'interrupted', 'system')

    def edit(self, revision: int, fields: dict) -> dict:
        if not isinstance(fields, dict) or not fields or set(fields) - set(FIELDS):
            raise ValueError('不正な合意項目です。')
        values = {key: text(value) for key, value in fields.items()}
        with self.lock:
            state = self._check(revision)
            changes = {key: {'before': state['draft'][key], 'after': value}
                       for key, value in values.items() if state['draft'][key] != value}
            if not changes:
                return state
            state['draft'].update(values)
            state['approval'] = None
            return self._write(state, 'draft-edited', 'human', changes)

    def approve(self, revision: int, reviewed: bool) -> dict:
        with self.lock:
            state = self._check(revision)
            if reviewed is not True or not all(value.strip() for value in state['draft'].values()):
                raise ValueError('全項目を確認してください。未解決条件は本文に明示できます。')
            snapshot = deepcopy(state['draft'])
            digest = hashlib.sha256(json.dumps(snapshot, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            state['approval'] = {'actor': 'local-human', 'at': now(), 'reviewed_revision': revision,
                                 'agreement': snapshot, 'sha256': digest}
            return self._write(state, 'agreement-confirmed', 'human', {'sha256': digest})

    def handoff(self, revision: int | None = None) -> dict:
        with self.lock:
            state = self.read()
            if revision is not None:
                state = self._check(revision)
            if state['busy'] or not state['approval']:
                raise Conflict('最新の合意内容を明示的に確定してから出力してください。')
            return {'schema_version': 1, 'kind': 'preflight-discussion-handoff',
                    'agreement': deepcopy(state['approval']['agreement']),
                    'confirmation': deepcopy(state['approval']),
                    'verification_status': 'not-run', 'execution_authorized': False,
                    'notice': '内容の確認記録です。実行許可・環境準備完了・E2E合格の証拠ではありません。'}

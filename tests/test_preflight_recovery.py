"""Cancellation races over real HTTP and persisted state; no model calls."""
from __future__ import annotations

import http.client
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import time
import unittest

from apps.preflight_web.providers import DemoProvider, DialogueCancelled
from apps.preflight_web.server import ConsoleServer
from apps.preflight_web.state import Conflict, FIELDS, SessionStore

REPLY = {'reply': '遅れて返った提案', 'proposals': [
    {'field': 'authority', 'value': '勝手に変更しない', 'why': '提案にすぎない'}]}


class CancellationStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'session.sqlite3'
        self.store = SessionStore(self.path)
        self.addCleanup(self.store.close)

    def test_cancellation_waits_for_provider_and_preserves_draft(self):
        draft = self.store.edit(0, {key: '維持する条件' for key in FIELDS})
        pending = self.store.begin_message(draft['revision'], '意図を聞きたい')
        stopping = self.store.request_cancel(pending['revision'], pending['active_turn'])
        self.assertTrue(stopping['busy'])
        self.assertTrue(stopping['cancel_requested'])
        for operation in (
            lambda: self.store.begin_message(stopping['revision'], '次の質問'),
            lambda: self.store.approve(stopping['revision'], True),
            lambda: self.store.handoff(stopping['revision']),
        ):
            with self.assertRaises(Conflict):
                operation()
        done = self.store.finish_message(REPLY, turn_id=pending['active_turn'])
        self.assertFalse(done['busy'])
        self.assertEqual(done['draft'], draft['draft'])
        self.assertEqual(done['proposals'], [])
        self.assertEqual(len(done['messages']), 1)
        self.assertEqual(done['messages'][0]['status'], 'interrupted')
        self.assertIsNone(done['approval'])

    def test_late_reply_and_error_cannot_affect_next_turn(self):
        old = self.store.begin_message(0, '古い質問')
        done = self.store.fail_message('中断', turn_id=old['active_turn'])
        new = self.store.begin_message(done['revision'], '新しい質問')
        self.assertEqual(self.store.finish_message(REPLY, turn_id=old['active_turn']), new)
        self.assertEqual(self.store.fail_message('遅延した失敗', turn_id=old['active_turn']), new)
        done = self.store.finish_message({'reply': '新しい回答', 'proposals': []}, turn_id=new['active_turn'])
        self.assertEqual(done['messages'][-1]['text'], '新しい回答')

    def test_stale_cancel_cannot_stop_new_turn(self):
        old = self.store.begin_message(0, '古い質問')
        done = self.store.finish_message(REPLY, turn_id=old['active_turn'])
        new = self.store.begin_message(done['revision'], '新しい質問')
        with self.assertRaises(Conflict):
            self.store.request_cancel(new['revision'], old['active_turn'])
        with self.assertRaises(Conflict):
            self.store.request_cancel(old['revision'], new['active_turn'])
        self.assertEqual(self.store.read(), new)

    def test_new_question_clears_previous_proposals(self):
        pending = self.store.begin_message(0, '質問')
        done = self.store.finish_message(REPLY, turn_id=pending['active_turn'])
        next_state = self.store.begin_message(done['revision'], '前提が違う')
        self.assertEqual(next_state['proposals'], [])

    def test_human_edit_retires_proposals_based_on_old_draft(self):
        pending = self.store.begin_message(0, '質問')
        done = self.store.finish_message(REPLY, turn_id=pending['active_turn'])
        edited = self.store.edit(done['revision'], {'outcome': '人間が前提を修正'})
        self.assertEqual(edited['proposals'], [])
        self.assertIsNone(edited['approval'])

    def test_restart_keeps_session_identity_and_interrupts_pending(self):
        pending = self.store.begin_message(0, '中断する質問')
        self.store.request_cancel(pending['revision'], pending['active_turn'])
        identity = pending['session_id']
        self.store.close()
        restored = SessionStore(self.path)
        self.addCleanup(restored.close)
        state = restored.read()
        self.assertEqual(state['session_id'], identity)
        self.assertFalse(state['busy'])
        self.assertFalse(state['cancel_requested'])
        self.assertEqual(state['messages'][0]['status'], 'interrupted')

    def test_existing_schema_one_state_gets_identity_without_reapproval(self):
        self.store.close()
        legacy = {'schema_version': 1, 'revision': 8, 'draft': dict.fromkeys(FIELDS, '旧案'),
                  'messages': [], 'proposals': [], 'approval': None, 'history': [],
                  'busy': False, 'error': None}
        with sqlite3.connect(self.path) as db:
            db.execute('UPDATE session SET body=? WHERE id=1', (json.dumps(legacy),))
        restored = SessionStore(self.path)
        self.addCleanup(restored.close)
        self.assertEqual(restored.read()['revision'], 8)
        self.assertEqual(restored.read()['draft'], legacy['draft'])
        self.assertIsNone(restored.read()['approval'])
        self.assertTrue(restored.read()['session_id'])


class WaitingProvider(DemoProvider):
    def __init__(self):
        self.started = threading.Event()
        self.cancel_seen = threading.Event()
        self.release = threading.Event()

    def respond(self, state, cancelled=None):
        if state['messages'][-1]['text'] != '停止テスト':
            return super().respond(state, cancelled)
        self.started.set()
        if not cancelled.wait(3):
            raise TimeoutError('Test did not request cancellation')
        self.cancel_seen.set()
        if not self.release.wait(3):
            raise TimeoutError('Test did not release cleanup')
        # Model completed concurrently: the store must still discard the result.
        return REPLY


class CancellationHTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = SessionStore(Path(self.temp.name) / 'state.sqlite3')
        self.provider = WaitingProvider()
        self.server = ConsoleServer(self.store, self.provider, port=0, token='local-test')
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop)

    def stop(self):
        self.provider.release.set()
        self.server.shutdown()
        self.server.server_close()
        self.store.close()

    def request(self, path='/api/state', payload=None, headers=None):
        client = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        default = {'Authorization': 'Bearer local-test', 'Content-Type': 'application/json'}
        default.update(headers or {})
        client.request('GET' if payload is None else 'POST', path,
                       None if payload is None else json.dumps(payload), default)
        response = client.getresponse()
        result = response.status, json.loads(response.read())
        client.close()
        return result

    def test_cancel_cleanup_then_ask_why_over_http(self):
        status, pending = self.request('/api/messages', {'revision': 0, 'text': '停止テスト'})
        self.assertEqual(status, 200)
        self.assertTrue(self.provider.started.wait(2))
        payload = {'revision': pending['revision'], 'turn_id': pending['active_turn']}
        status, stopping = self.request('/api/cancel', payload)
        self.assertEqual(status, 200)
        self.assertTrue(self.provider.cancel_seen.wait(2))
        self.assertTrue(stopping['busy'])
        self.assertEqual(self.request('/api/messages', {'revision': stopping['revision'], 'text': '次'})[0], 409)
        self.provider.release.set()
        self.server.worker.join(timeout=3)
        status, done = self.request()
        self.assertFalse(done['busy'])
        self.assertIsNone(done['approval'])
        self.assertEqual(len(done['messages']), 1)
        status, _ = self.request('/api/messages', {'revision': done['revision'], 'text': 'なぜこの質問が必要？'})
        self.assertEqual(status, 200)
        self.server.worker.join(timeout=3)
        status, done = self.request()
        self.assertIn('聞き返しは選択や承認', done['messages'][-1]['text'])
        self.assertFalse(done['execution_authorized'])
        self.assertEqual(done['verification_status'], 'not-run')
        self.assertEqual(self.request('/api/handoff?revision=' + str(done['revision']))[0], 409)

    def test_restart_can_reuse_loopback_port(self):
        self.assertEqual(self.request()[0], 200)
        port = self.server.server_port
        self.server.shutdown()
        self.server.server_close()
        self.server = ConsoleServer(self.store, DemoProvider(), port=port, token='local-test')
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.assertEqual(self.request()[0], 200)

    def test_cancel_endpoint_requires_auth_origin_and_exact_turn(self):
        _, pending = self.request('/api/messages', {'revision': 0, 'text': '停止テスト'})
        payload = {'revision': pending['revision'], 'turn_id': pending['active_turn']}
        self.assertEqual(self.request('/api/cancel', payload, {'Authorization': ''})[0], 401)
        self.assertEqual(self.request('/api/cancel', payload, {'Origin': 'https://invalid.example'})[0], 403)
        self.assertEqual(self.request('/api/cancel', dict(payload, turn_id='other'))[0], 409)
        self.assertFalse(self.provider.cancel_seen.is_set())


if __name__ == '__main__':
    unittest.main()

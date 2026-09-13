"""Offline contract and HTTP tests; fixtures are not live-model evidence."""
from __future__ import annotations

import http.client
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest

from apps.preflight_web.state import FIELDS, SessionStore, Conflict
from apps.preflight_web.server import ConsoleServer
from apps.preflight_web.providers import DemoProvider, validate_reply


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = SessionStore(Path(self.tmp.name) / 'session.sqlite3')
        self.addCleanup(self.store.close)

    def complete_draft(self):
        return self.store.edit(self.store.read()['revision'], {key: f'人間の条件: {key}' for key in FIELDS})

    def test_all_app_python_sources_compile(self):
        root = Path(__file__).resolve().parents[1] / 'apps/preflight_web'
        for source in root.rglob('*.py'):
            compile(source.read_bytes(), str(source), 'exec')

    def test_chat_cannot_approve(self):
        state = self.store.begin_message(0, 'わかった。その条件でよろしく')
        self.assertIsNone(state['approval'])
        self.assertTrue(state['busy'])

    def test_proposal_is_not_draft_or_approval(self):
        self.store.begin_message(0, '実行環境を相談したい')
        state = self.store.finish_message({'reply': 'CIも候補です', 'proposals': [
            {'field': 'environment', 'value': 'CIでも実行', 'why': '候補・未合意'}]})
        self.assertEqual(state['draft']['environment'], '')
        self.assertEqual(state['proposals'][0]['value'], 'CIでも実行')
        self.assertIsNone(state['approval'])

    def test_confirmation_is_revision_bound(self):
        old = self.complete_draft()
        self.store.edit(old['revision'], {'authority': 'ローカルのみ'})
        with self.assertRaises(Conflict):
            self.store.approve(old['revision'], True)
        self.assertIsNone(self.store.read()['approval'])

    def test_edit_invalidates_confirmation(self):
        state = self.complete_draft()
        approved = self.store.approve(state['revision'], True)
        self.assertIsNotNone(approved['approval'])
        state = self.store.edit(approved['revision'], {'authority': 'ネットワークは禁止'})
        self.assertIsNone(state['approval'])
        self.assertEqual(state['history'][-1]['actor'], 'human')

    def test_new_discussion_invalidates_confirmation(self):
        state = self.complete_draft()
        approved = self.store.approve(state['revision'], True)
        state = self.store.begin_message(approved['revision'], 'その質問はなぜ必要？')
        self.assertIsNone(state['approval'])

    def test_empty_or_unreviewed_cannot_confirm(self):
        with self.assertRaises(ValueError):
            self.store.approve(0, True)
        state = self.complete_draft()
        with self.assertRaises(ValueError):
            self.store.approve(state['revision'], False)

    def test_busy_cannot_confirm_or_edit(self):
        state = self.complete_draft()
        pending = self.store.begin_message(state['revision'], '確認したい')
        with self.assertRaises(Conflict):
            self.store.approve(pending['revision'], True)
        with self.assertRaises(Conflict):
            self.store.edit(pending['revision'], {'authority': 'CI'})

    def test_restore_preserves_messages_without_auto_resume(self):
        self.store.begin_message(0, 'なぜ？')
        self.store.close()
        self.store = SessionStore(Path(self.tmp.name) / 'session.sqlite3')
        self.addCleanup(self.store.close)
        state = self.store.read()
        self.assertFalse(state['busy'])
        self.assertEqual(state['messages'][0]['text'], 'なぜ？')
        self.assertIn('中断', state['error'])
        self.assertIsNone(state['approval'])

    def test_handoff_is_not_execution_permission_or_readiness(self):
        state = self.complete_draft()
        self.store.approve(state['revision'], True)
        result = self.store.handoff()
        self.assertEqual(result['verification_status'], 'not-run')
        self.assertFalse(result['execution_authorized'])
        self.assertEqual(result['agreement']['authority'], '人間の条件: authority')

    def test_missing_confirmation_cannot_export(self):
        with self.assertRaises(Conflict):
            self.store.handoff()

    def test_provider_cannot_inject_approval(self):
        with self.assertRaises(ValueError):
            validate_reply({'reply': 'approved', 'proposals': [], 'approval': True})

    def test_unknown_field_rejected(self):
        with self.assertRaises(ValueError):
            validate_reply({'reply': 'ok', 'proposals': [{'field': 'execute', 'value': 'x', 'why': 'x'}]})
        with self.assertRaises(ValueError):
            self.store.edit(0, {'execute': 'x'})

    def test_failed_provider_preserves_draft_and_reports_error(self):
        prior = self.complete_draft()
        self.store.begin_message(prior['revision'], '説明して')
        state = self.store.fail_message('接続が切れました')
        self.assertFalse(state['busy'])
        self.assertEqual(state['draft'], prior['draft'])
        self.assertIsNone(state['approval'])
        self.assertEqual(state['error'], '接続が切れました')


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = SessionStore(Path(self.tmp.name) / 'state.sqlite3')
        self.server = ConsoleServer(self.store, DemoProvider(), port=0, token='fixture-token')
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop)

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.store.close()

    def request(self, method='GET', path='/api/state', data=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        h = {'Authorization': 'Bearer fixture-token'}
        if data is not None:
            h['Content-Type'] = 'application/json'
        h.update(headers or {})
        connection.request(method, path, json.dumps(data) if data is not None else None, h)
        response = connection.getresponse()
        payload = response.read()
        result = response.status, dict(response.getheaders()), payload
        connection.close()
        return result

    def test_real_http_serves_state_and_assets(self):
        status, _, payload = self.request()
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(payload)['provider'], 'demo')
        status, headers, payload = self.request(path='/')
        self.assertEqual(status, 200)
        self.assertIn(b'Preflight', payload)
        self.assertIn('Content-Security-Policy', headers)

    def test_auth_and_origin_are_required(self):
        self.assertEqual(self.request(headers={'Authorization': ''})[0], 401)
        self.assertEqual(self.request(headers={'Origin': 'https://evil.example'})[0], 403)
        self.assertEqual(self.request(headers={'Host': 'evil.example'})[0], 403)
        self.assertEqual(self.request(headers={'Origin': 'null'})[0], 403)

    def test_no_execution_or_arbitrary_file_endpoint(self):
        self.assertEqual(self.request('POST', '/api/execute', {})[0], 404)
        self.assertEqual(self.request(path='/../../etc/passwd')[0], 404)
        self.assertEqual(self.request(path='/state.sqlite3')[0], 404)

    def test_compare_and_swap_over_http(self):
        self.assertEqual(self.request('POST', '/api/draft', {'revision': 0, 'fields': {'outcome': 'A'}})[0], 200)
        self.assertEqual(self.request('POST', '/api/draft', {'revision': 0, 'fields': {'outcome': 'B'}})[0], 409)
        state = json.loads(self.request()[2])
        self.assertEqual(state['draft']['outcome'], 'A')

    def test_dialogue_to_handoff_through_real_http(self):
        status, _, _ = self.request('POST', '/api/messages', {'revision': 0, 'text': 'なぜこの質問が必要？'})
        self.assertEqual(status, 200)
        deadline = time.monotonic() + 3
        while True:
            state = json.loads(self.request()[2])
            if not state['busy']: break
            self.assertLess(time.monotonic(), deadline)
            time.sleep(.01)
        self.assertIn('聞き返しは選択や承認として扱いません', state['messages'][-1]['text'])
        self.assertIsNone(state['approval'])
        status, _, body = self.request('POST', '/api/draft', {'revision': state['revision'],
                                        'fields': {key: '確認した条件: ' + key for key in FIELDS}})
        self.assertEqual(status, 200)
        state = json.loads(body)
        status, _, body = self.request('POST', '/api/approve', {'revision': state['revision'], 'reviewed': True})
        self.assertEqual(status, 200)
        state = json.loads(body)
        status, _, body = self.request(path='/api/handoff?revision=' + str(state['revision']))
        self.assertEqual(status, 200)
        self.assertFalse(json.loads(body)['execution_authorized'])
        self.assertEqual(json.loads(body)['verification_status'], 'not-run')
        self.assertEqual(self.request(path='/api/handoff?revision=0')[0], 409)

    def test_non_json_rejected(self):
        self.assertEqual(self.request('POST', '/api/draft', {}, {'Content-Type': 'text/plain'})[0], 415)


if __name__ == '__main__':
    unittest.main()

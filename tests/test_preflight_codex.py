"""Codex wire-protocol fixtures, not actual Codex or live model tests."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import threading
import time
import unittest

from apps.preflight_web.codex import CodexProvider
from apps.preflight_web.providers import DialogueCancelled

FIXTURE = '''#!/usr/bin/env python3
import json, sys, time
from pathlib import Path
if '--version' in sys.argv:
    print('codex-fixture 0.0-test'); raise SystemExit(0)
log = Path(__file__).with_suffix('.jsonl')
count = 0
for line in sys.stdin:
    req = json.loads(line)
    with log.open('a') as f: f.write(json.dumps(req)+'\\n')
    method = req.get('method')
    result = {}
    if method == 'initialized': continue
    if method == 'thread/start':
        result = {'thread': {'id': 'thread-1'}, 'model': 'fixture-model'}
        if Path(__file__).with_suffix('.no-model').exists(): result.pop('model')
    if method == 'turn/start':
        count += 1
        result = {'turn': {'id': 'turn-'+str(count)}}
    print(json.dumps({'id': req['id'], 'result': result}), flush=True)
    if method == 'turn/start':
        if Path(__file__).with_suffix('.hang').exists():
            Path(__file__).with_suffix('.ready').touch()
            time.sleep(60)
        if Path(__file__).with_suffix('.deny').exists():
            print(json.dumps({'id': 900, 'method': 'item/commandExecution/requestApproval', 'params': {}}), flush=True)
            denied = json.loads(sys.stdin.readline())
            with log.open('a') as f: f.write(json.dumps(denied)+'\\n')
            continue
        print(json.dumps({'method': 'item/completed', 'params': {'threadId': 'thread-1', 'turnId': result['turn']['id'],
            'item': {'type': 'agentMessage', 'text': json.dumps({'reply': '説明を続けます', 'proposals': []})}}}), flush=True)
        print(json.dumps({'method': 'turn/completed', 'params': {'threadId': 'thread-1',
            'turn': {'id': result['turn']['id'], 'status': 'completed'}}}), flush=True)
'''


class CodexWireTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.binary = self.root / 'codex-fixture'
        self.binary.write_text(FIXTURE)
        self.binary.chmod(0o700)
        self.home = self.root / 'clean-home'
        self.home.mkdir()

    def provider(self):
        result = CodexProvider(str(self.binary), 'fixture-model', self.home, timeout=3)
        self.addCleanup(result.close)
        return result

    def test_same_thread_dialogue_and_restrictive_policy(self):
        provider = self.provider()
        self.assertEqual(provider.respond({'draft': {}, 'messages': [{'role': 'user', 'text': 'なぜ？'}]})['reply'], '説明を続けます')
        provider.respond({'draft': {}, 'messages': [{'role': 'user', 'text': '前提が違う'}]})
        events = [json.loads(line) for line in self.binary.with_suffix('.jsonl').read_text().splitlines()]
        self.assertEqual(sum(e.get('method') == 'thread/start' for e in events), 1)
        turns = [e['params'] for e in events if e.get('method') == 'turn/start']
        self.assertEqual(len(turns), 2)
        for turn in turns:
            self.assertEqual(turn['threadId'], 'thread-1')
            self.assertEqual(turn['approvalPolicy'], 'never')
            self.assertEqual(turn['sandboxPolicy']['type'], 'readOnly')
            self.assertEqual(turn['sandboxPolicy']['access']['type'], 'restricted')

    def test_tool_approval_request_fails_closed(self):
        self.binary.with_suffix('.deny').touch()
        provider = self.provider()
        with self.assertRaises(RuntimeError):
            provider.respond({'draft': {}, 'messages': [{'role': 'user', 'text': 'よろしく'}]})
        self.assertIsNone(provider.process)

    def test_dirty_profile_rejected_without_changing_it(self):
        config = self.home / 'config.toml'
        config.write_text('mcp_servers = {}\n')
        with self.assertRaises(ValueError):
            self.provider()
        self.assertEqual(config.read_text(), 'mcp_servers = {}\n')

    def test_missing_binary_does_not_switch_provider(self):
        with self.assertRaises(ValueError):
            CodexProvider('/nonexistent/codex', 'fixture-model', self.home)

    def test_missing_model_identity_does_not_count_as_match(self):
        self.binary.with_suffix('.no-model').touch()
        provider = self.provider()
        with self.assertRaisesRegex(RuntimeError, 'resolved model'):
            provider.respond({'draft': {}, 'messages': [{'role': 'user', 'text': 'なぜ？'}]})
        self.assertIsNone(provider.process)

    def test_cancel_before_launch_starts_no_process(self):
        provider = self.provider()
        cancel = threading.Event()
        cancel.set()
        with self.assertRaises(DialogueCancelled):
            provider.respond({'draft': {}, 'messages': []}, cancel)
        self.assertFalse(self.binary.with_suffix('.jsonl').exists())

    def test_silent_transport_can_cancel_then_rebuild_context(self):
        self.binary.with_suffix('.hang').touch()
        provider = self.provider()
        cancel = threading.Event()
        failures = []
        context = {'draft': {'authority': '対話のみ'},
                   'messages': [{'role': 'user', 'text': '前の質問', 'status': 'interrupted'}]}

        def respond():
            try:
                provider.respond(context, cancel)
            except Exception as exc:
                failures.append(exc)

        worker = threading.Thread(target=respond)
        worker.start()
        try:
            deadline = time.monotonic() + 2
            while not self.binary.with_suffix('.ready').exists():
                self.assertLess(time.monotonic(), deadline)
                time.sleep(.01)
            child = provider.process
        finally:
            cancel.set()
            worker.join(timeout=3)
        self.assertFalse(worker.is_alive())
        self.assertIsNotNone(child.poll())
        self.assertEqual(len(failures), 1)
        self.assertIsInstance(failures[0], DialogueCancelled)
        self.assertIsNone(provider.process)
        self.binary.with_suffix('.hang').unlink()
        context['messages'].append({'role': 'user', 'text': '意図を説明して'})
        self.assertEqual(provider.respond(context)['reply'], '説明を続けます')
        events = [json.loads(line) for line in self.binary.with_suffix('.jsonl').read_text().splitlines()]
        self.assertEqual(sum(e.get('method') == 'thread/start' for e in events), 2)
        turns = [e for e in events if e.get('method') == 'turn/start']
        supplied = json.loads(turns[-1]['params']['input'][0]['text'])
        self.assertEqual(supplied['messages'], context['messages'])
        self.assertEqual(supplied['draft'], context['draft'])
        self.assertFalse(any(e.get('method') in ('thread/resume', 'command/exec') for e in events))


if __name__ == '__main__':
    unittest.main()

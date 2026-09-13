"""Codex wire-protocol fixtures, not actual Codex or live model tests."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from apps.preflight_web.codex import CodexProvider

FIXTURE = '''#!/usr/bin/env python3
import json, sys
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
    if method == 'thread/start': result = {'thread': {'id': 'thread-1'}, 'model': 'fixture-model'}
    if method == 'turn/start':
        count += 1
        result = {'turn': {'id': 'turn-'+str(count)}}
    print(json.dumps({'id': req['id'], 'result': result}), flush=True)
    if method == 'turn/start':
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
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.binary = self.root / 'codex-fixture'
        self.binary.write_text(FIXTURE); self.binary.chmod(0o700)
        self.home = self.root / 'clean-home'; self.home.mkdir()

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
        config = self.home / 'config.toml'; config.write_text('mcp_servers = {}\n')
        with self.assertRaises(ValueError):
            self.provider()
        self.assertEqual(config.read_text(), 'mcp_servers = {}\n')

    def test_missing_binary_does_not_switch_provider(self):
        with self.assertRaises(ValueError):
            CodexProvider('/nonexistent/codex', 'fixture-model', self.home)


if __name__ == '__main__':
    unittest.main()

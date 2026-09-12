#!/usr/bin/env python3
"""Run opt-in, matched instruction-arm trials through an explicitly supplied adapter.

This runner creates isolated workspaces, NOT an OS security sandbox. The operator
must supply a sandboxed adapter and review the oracle commands before execution.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
ARMS = ('baseline', 'minimal', 'selective')


def run_process(argv: list[str], cwd: Path, payload: dict | None, timeout: float) -> dict:
    start = time.monotonic()
    try:
        process = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, start_new_session=True)
    except OSError as exc:
        return {'exit_code': None, 'status': 'launch-failed', 'stdout': '', 'stderr': str(exc), 'seconds': 0}
    try:
        out, err = process.communicate(json.dumps(payload) if payload is not None else '', timeout=timeout)
        status = 'exited'
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        out, err = process.communicate()
        status = 'timeout'
    return {'exit_code': process.returncode, 'status': status, 'stdout': out, 'stderr': err,
            'seconds': time.monotonic() - start}


def prepare(case: dict, arm: str, workspace: Path, baseline: Path | None) -> None:
    workspace.mkdir(parents=True)
    if arm == 'baseline':
        if baseline is None or not (baseline / 'AGENTS.md').is_file():
            raise ValueError('baseline arm requires a pinned historical source checkout')
        # Reproduce the old active instruction/tool surface, not its historical run logs.
        for name in ('AGENTS.md', 'PLANS.md', 'REFERENCES.md'):
            if (baseline / name).is_file():
                shutil.copy2(baseline / name, workspace / name)
        for name in ('.agents/skills', '.agents/model-routing', 'scripts'):
            if (baseline / name).is_dir():
                shutil.copytree(baseline / name, workspace / name, symlinks=False)
        policy = baseline / '.agents/project-policy.yml'
        if policy.is_file():
            shutil.copy2(policy, workspace / '.agents/project-policy.yml')
    else:
        shutil.copy2(ROOT / 'templates/AGENTS.md', workspace / 'AGENTS.md')
        if arm == 'selective':
            for name in case['skills']:
                shutil.copytree(ROOT / '.agents/skills' / name, workspace / '.agents/skills' / name)
    for relative, content in case.get('files', {}).items():
        rel = Path(relative)
        if rel.is_absolute() or '..' in rel.parts or relative in ('AGENTS.md', 'COMMANDS.md') or relative.startswith(('.agents/', '.git/')):
            raise ValueError(f'Invalid fixture path: {relative}')
        path = workspace / rel; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content)
    (workspace / 'COMMANDS.md').write_text('# Fixture command contract\n\n' + case['commands'] + '\n')
    subprocess.run(['git', 'init', '-q', str(workspace)], check=True, capture_output=True)
    subprocess.run(['git', '-C', str(workspace), 'add', '.'], check=True, capture_output=True)
    subprocess.run(['git', '-C', str(workspace), '-c', 'user.name=Eval Fixture', '-c',
                    'user.email=fixture@example.invalid', '-c', 'commit.gpgsign=false',
                    'commit', '-qm', 'Matched trial starting state'], check=True, capture_output=True)


def run_trial(case: dict, arm: str, destination: Path, adapter: list[str], model: str,
              harness: str, baseline: Path | None, timeout: float) -> dict:
    workspace = destination / 'workspace'
    prepare(case, arm, workspace, baseline)
    payload = {'protocol': 1, 'workspace': str(workspace), 'task': case['prompt'],
               'requested_model': model, 'requested_harness': harness,
               'trace_path': str(destination / 'trace.jsonl'),
               'metadata_path': str(destination / 'metadata.json')}
    invocation = run_process(adapter, workspace, payload, timeout)
    (destination / 'adapter.json').write_text(json.dumps(invocation, indent=2))
    result = {'schema_version': 1, 'case': case['id'], 'arm': arm,
              'fixture_sha256': hashlib.sha256(json.dumps(case, sort_keys=True).encode()).hexdigest(),
              'requested_model': model, 'requested_harness': harness,
              'agent_status': invocation['status'], 'agent_exit_code': invocation['exit_code'],
              'agent_seconds': invocation['seconds'], 'functional': 'not-evaluated',
              'behavior_review': 'pending', 'status': 'incomplete'}
    try:
        metadata = json.loads((destination / 'metadata.json').read_text())
        trace = destination / 'trace.jsonl'
        if metadata.get('resolved_model') != model or metadata.get('harness') != harness or not metadata.get('harness_version'):
            raise ValueError('resolved model/harness mismatch or missing harness version')
        if not trace.is_file() or not trace.stat().st_size:
            raise ValueError('missing execution trace')
        for line in trace.read_text().splitlines():
            if not isinstance(json.loads(line), dict):
                raise ValueError('trace events must be JSON objects')
        result['metadata'] = metadata
        result['trace_sha256'] = hashlib.sha256(trace.read_bytes()).hexdigest()
    except (OSError, ValueError, AttributeError) as exc:
        result['limit'] = str(exc)
    else:
        if invocation['status'] == 'exited' and invocation['exit_code'] == 0:
            if case.get('oracle'):
                # Oracle code stays outside the agent's workspace. This is defense in
                # depth only: filesystem access must be constrained by the adapter.
                oracle = ROOT / 'evals/oracles' / case['oracle']
                proof = run_process([sys.executable, str(oracle), str(workspace)], destination, None, timeout)
                (destination / 'oracle.json').write_text(json.dumps(proof, indent=2))
                result['functional'] = 'pass' if proof['status'] == 'exited' and proof['exit_code'] == 0 else 'fail'
            result['status'] = 'needs-behavior-review' if result['functional'] != 'fail' else 'functional-failure'
    (destination / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adapter-json', required=True, help='JSON argv array; no shell interpolation')
    parser.add_argument('--model', required=True, help='Exact expected resolved model, not an unverified alias')
    parser.add_argument('--harness', required=True)
    parser.add_argument('--baseline', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--arm', choices=ARMS, action='append')
    parser.add_argument('--case', action='append')
    parser.add_argument('--repeats', type=int, default=1)
    parser.add_argument('--timeout', type=float, default=600)
    parser.add_argument('--sandbox-confirmed', action='store_true')
    args = parser.parse_args()
    try:
        if not args.sandbox_confirmed:
            raise ValueError('Supply and authorize a sandboxed adapter, then pass --sandbox-confirmed')
        adapter = json.loads(args.adapter_json)
        if not isinstance(adapter, list) or not adapter or not all(isinstance(x, str) and x for x in adapter):
            raise ValueError('--adapter-json must be a nonempty argv array')
        if args.repeats < 1 or args.timeout <= 0:
            raise ValueError('repeats and timeout must be positive')
        cases = json.loads((ROOT / 'evals/cases.json').read_text())['cases']
        selected = [c for c in cases if not args.case or c['id'] in args.case]
        if args.case and set(args.case) - {c['id'] for c in cases}:
            raise ValueError('unknown evaluation case')
        arms = list(dict.fromkeys(args.arm or ARMS))
        if 'baseline' in arms and (args.baseline is None or not args.baseline.is_dir()):
            raise ValueError('--baseline is required for a matched historical arm')
        output = args.output.resolve()
        if output.exists():
            raise ValueError('output must be a new directory; do not overwrite trials')
        output.mkdir(parents=True)
        outcomes = []
        for repeat in range(args.repeats):
            # Rotate order to reduce systematic first/last-arm effects; trials remain independent.
            ordered = arms[repeat % len(arms):] + arms[:repeat % len(arms)]
            for case in selected:
                for arm in ordered:
                    outcomes.append(run_trial(case, arm, output / f'{case["id"]}-{arm}-{repeat+1}',
                                              adapter, args.model, args.harness,
                                              args.baseline.resolve() if args.baseline else None, args.timeout))
        (output / 'summary.json').write_text(json.dumps({'status': 'behavior-review-required', 'trials': outcomes}, indent=2))
        print(f'{len(outcomes)} trials recorded; behavioral grading is pending, not an overall pass.')
        return 1 if any(x['status'] in ('incomplete', 'functional-failure') for x in outcomes) else 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f'task-evals: {exc}', file=sys.stderr); return 2


if __name__ == '__main__':
    raise SystemExit(main())

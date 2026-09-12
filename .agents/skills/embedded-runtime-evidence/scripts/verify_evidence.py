#!/usr/bin/env python3
"""Check evidence linkage/digests, not measurement truth or method adequacy."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

IDENTITY_FIELDS = ('candidate', 'target', 'workload', 'configuration', 'method')


def verify(contract: dict, evidence: dict, root: Path) -> list[str]:
    errors: list[str] = []
    root = root.resolve()
    if contract.get('schema_version') != 1 or evidence.get('schema_version') != 1:
        return ['unsupported schema_version']
    requirements, results = contract.get('requirements'), evidence.get('results')
    if not isinstance(requirements, list) or not requirements or not isinstance(results, list):
        return ['requirements must be nonempty and results must be a list']
    indexed: dict[str, dict] = {}
    for result in results:
        if not isinstance(result, dict) or not isinstance(result.get('id'), str) or not result['id']:
            errors.append('invalid result identity')
            continue
        if result['id'] in indexed:
            errors.append(f'duplicate result: {result["id"]}')
        indexed[result['id']] = result
    seen: set[str] = set()
    for req in requirements:
        if not isinstance(req, dict) or not isinstance(req.get('id'), str) or not req['id']:
            errors.append('invalid requirement identity')
            continue
        name = req['id']
        if name in seen:
            errors.append(f'duplicate requirement: {name}')
        seen.add(name)
        obligation = req.get('obligation')
        if obligation not in ('required', 'target'):
            errors.append(f'{name}: invalid obligation')
        for key in ('criterion', 'source') + IDENTITY_FIELDS:
            if not isinstance(req.get(key), str) or not req[key].strip():
                errors.append(f'{name}: missing contract {key}')
        result = indexed.get(name)
        if result is None:
            if obligation == 'required':
                errors.append(f'{name}: required evidence missing')
            continue
        status = result.get('status')
        if status not in ('pass', 'fail', 'not-measured'):
            errors.append(f'{name}: invalid evidence status')
        if obligation == 'required' and status != 'pass':
            errors.append(f'{name}: required condition is {status}, not pass')
        for key in IDENTITY_FIELDS:
            if result.get(key) != req.get(key):
                errors.append(f'{name}: {key} mismatch')
        artifacts = result.get('artifacts', [])
        if not isinstance(artifacts, list):
            errors.append(f'{name}: invalid artifacts')
            continue
        if status == 'pass' and not artifacts:
            errors.append(f'{name}: pass without an evidence artifact')
        for artifact in artifacts:
            if not isinstance(artifact, dict) or not isinstance(artifact.get('path'), str):
                errors.append(f'{name}: invalid artifact entry')
                continue
            relative = Path(artifact['path']); path = root / relative
            if relative.is_absolute() or '..' in relative.parts or path.resolve() == root or not path.resolve().is_relative_to(root):
                errors.append(f'{name}: artifact escapes evidence root')
                continue
            if path.is_symlink() or any(p.is_symlink() for p in path.parents if p != root and p.is_relative_to(root)):
                errors.append(f'{name}: symlinked evidence artifact')
                continue
            try:
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError:
                errors.append(f'{name}: artifact unreadable: {relative}')
                continue
            if artifact.get('sha256') != digest:
                errors.append(f'{name}: artifact digest mismatch: {relative}')
    for name in indexed.keys() - seen:
        errors.append(f'unexpected result: {name}')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contract', required=True, type=Path)
    parser.add_argument('--evidence', required=True, type=Path)
    parser.add_argument('--root', required=True, type=Path)
    args = parser.parse_args()
    try:
        errors = verify(json.loads(args.contract.read_text()), json.loads(args.evidence.read_text()), args.root)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        print(f'evidence: invalid input: {exc}', file=sys.stderr)
        return 2
    if errors:
        print('\n'.join(errors)); return 1
    print('Evidence manifest linkage and digests are consistent; measurement truth and method adequacy are not certified.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

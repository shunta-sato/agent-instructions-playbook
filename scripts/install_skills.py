#!/usr/bin/env python3
"""Install a selected native skill set without overwriting project-owned files."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = '.playbook-install.json'
NAME = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


def selection(root: Path, profiles: list[str], skills: list[str]) -> list[str]:
    catalog = json.loads((root / 'profiles.json').read_text())
    chosen = set(skills)
    for profile in profiles or ([] if skills else catalog['default_profiles']):
        if profile not in catalog['profiles']:
            raise ValueError(f'Unknown profile: {profile}')
        chosen.update(catalog['profiles'][profile])
    for name in chosen:
        if not NAME.fullmatch(name) or not (root / '.agents/skills' / name / 'SKILL.md').is_file():
            raise ValueError(f'Unknown skill: {name}')
    return sorted(chosen)


def validate_parents(target: Path, relative: str) -> Path:
    """Reject legacy whole-directory links and paths outside the selected worktree."""
    path = target / relative
    if path == target or not path.is_relative_to(target):
        raise ValueError(f'Invalid destination: {relative}')
    for parent in path.parents:
        if parent == target:
            break
        if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
            raise ValueError(f'Unmanaged/legacy parent {parent}; remove or relocate it explicitly first')
    return path


def install(target: Path, source: Path, names: list[str], client: str, dry_run: bool = False) -> dict:
    if client not in ('codex', 'claude', 'both') or any(not NAME.fullmatch(n) for n in names):
        raise ValueError('Invalid client or skill name')
    target, source = target.resolve(), source.resolve()
    if target == source:
        raise ValueError('Do not install into the playbook source itself')
    check = subprocess.run(['git', '-C', str(target), 'rev-parse', '--show-toplevel'],
                           text=True, capture_output=True)
    if check.returncode or Path(check.stdout.strip()).resolve() != target:
        raise ValueError('Target must be the root of an existing Git worktree')
    manifest = target / MANIFEST
    if manifest.is_symlink():
        raise ValueError('Refusing a symlinked installation manifest')
    old = json.loads(manifest.read_text()) if manifest.exists() else {'schema_version': 2, 'links': {}}
    if not isinstance(old, dict) or old.get('schema_version') != 2 or not isinstance(old.get('links'), dict):
        raise ValueError('Unrecognized installation manifest; explicit migration is required')
    prefix = ['.agents/skills'] if client == 'codex' else ['.claude/skills']
    if client == 'both':
        prefix = ['.agents/skills', '.claude/skills']
    wanted = {f'{p}/{name}': str(source / '.agents/skills' / name) for p in prefix for name in names}
    previous = old['links']
    # Fully validate both old ownership and the desired set before changing anything.
    for rel, dest in previous.items():
        parts = rel.split('/')
        if len(parts) != 3 or parts[0] not in ('.agents', '.claude') or parts[1] != 'skills' or not NAME.fullmatch(parts[2]):
            raise ValueError(f'Invalid owned path in manifest: {rel}')
        if not isinstance(dest, str) or not Path(dest).is_absolute():
            raise ValueError(f'Invalid recorded link target: {rel}')
        path = validate_parents(target, rel)
        if path.is_symlink():
            if os.readlink(path) != dest:
                raise ValueError(f'User-modified link is not replaceable: {path}')
        elif path.exists():
            raise ValueError(f'User-owned replacement is not replaceable: {path}')
    for rel, dest in wanted.items():
        path = validate_parents(target, rel)
        if rel not in previous and (path.exists() or path.is_symlink()):
            raise ValueError(f'Unmanaged destination already exists: {path}')
        if not (Path(dest) / 'SKILL.md').is_file():
            raise ValueError(f'Missing source skill: {dest}')
    result = {'schema_version': 2, 'source': str(source), 'client': client, 'links': wanted}
    if dry_run:
        return result
    snapshot = {rel: os.readlink(target / rel) if (target / rel).is_symlink() else None
                for rel in set(previous) | set(wanted)}
    temporary = manifest.with_name(MANIFEST + '.tmp')
    if temporary.exists() or temporary.is_symlink():
        raise ValueError(f'Temporary manifest collision: {temporary}')
    try:
        for rel in sorted(set(previous) | set(wanted)):
            path = target / rel
            desired = wanted.get(rel)
            if path.is_symlink() and os.readlink(path) == desired:
                continue
            if path.is_symlink():
                path.unlink()
            if desired is not None:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.symlink_to(desired, target_is_directory=True)
        temporary.write_text(json.dumps(result, indent=2) + '\n')
        temporary.replace(manifest)
    except OSError:
        for rel, destination in snapshot.items():
            path = target / rel
            if path.is_symlink():
                path.unlink()
            if destination is not None:
                path.symlink_to(destination, target_is_directory=True)
        temporary.unlink(missing_ok=True)
        raise
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target', nargs='?', type=Path)
    parser.add_argument('--profile', action='append', default=[])
    parser.add_argument('--skill', action='append', default=[])
    parser.add_argument('--client', choices=['codex', 'claude', 'both'], default='codex')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--list', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.list:
            print((ROOT / 'profiles.json').read_text(), end='')
            return 0
        if args.target is None:
            parser.error('target is required unless --list is used')
        names = selection(ROOT, args.profile, args.skill)
        result = install(args.target, ROOT, names, args.client, args.dry_run)
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(f'install-skills: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

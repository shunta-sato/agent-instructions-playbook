#!/usr/bin/env python3
"""Validate current discoverability, bundled resources and executable source syntax."""
from __future__ import annotations
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    catalog = json.loads((root / 'profiles.json').read_text())
    names: set[str] = set()
    for skill in sorted((root / '.agents/skills').glob('*/SKILL.md')):
        text = skill.read_text()
        match = re.match(r'---\nname: ([a-z0-9-]+)\ndescription: ("[^\n]+")\n---\n', text)
        if not match:
            errors.append(f'{skill.relative_to(root)}: invalid supported frontmatter')
            continue
        name, raw = match.groups()
        try:
            description = json.loads(raw)
            if not description.strip():
                raise ValueError('empty description')
        except ValueError:
            errors.append(f'{name}: invalid description')
        if name != skill.parent.name or name in names:
            errors.append(f'{name}: duplicate name or directory mismatch')
        names.add(name)
        for ref in re.findall(r'`((?:references|assets|scripts|templates)/[^`\s]+)', text):
            if not (skill.parent / ref).exists() and not (root / ref).exists():
                errors.append(f'{name}: missing bundled resource: {ref}')
        mirror = root / '.claude/skills' / name
        if not mirror.is_symlink() or mirror.resolve() != skill.parent.resolve():
            errors.append(f'{name}: incorrect native discovery mirror')
    for name in (root / '.claude/skills').iterdir():
        if name.name not in names:
            errors.append(f'unknown mirror: {name.name}')
    selected = set()
    for profile, entries in catalog['profiles'].items():
        if not isinstance(entries, list) or len(entries) != len(set(entries)):
            errors.append(f'{profile}: invalid/duplicate profile entries'); continue
        selected.update(entries)
        for name in entries:
            if name not in names:
                errors.append(f'{profile}: unknown skill {name}')
    if selected != names:
        errors.append('some specialist skills have no install profile')
    for default in catalog['default_profiles']:
        if default not in catalog['profiles']:
            errors.append(f'unknown default profile: {default}')
    if (root / '.agents/model-routing').exists():
        errors.append('retired model-routing configuration is active')
    if 'AGENT_INDEX_V1' in (root / 'AGENTS.md').read_text():
        errors.append('retired always-on skill index is active')
    template = root / 'templates/AGENTS.md'
    if template.read_bytes() != (root / '.agents/skills/repo-onboarding/templates/AGENTS.md').read_bytes():
        errors.append('consumer template and onboarding asset differ')
    mapping = json.loads((root / 'docs/skill-disposition.json').read_text())['skills']
    old_names = [item['old'] for item in mapping]
    if len(old_names) != len(set(old_names)):
        errors.append('duplicate migration disposition')
    for item in mapping:
        if item['destination'] not in names | {'working-contract', 'task-brief'}:
            errors.append(f'unknown migration destination: {item}')
        if item['old'] in names and item['disposition'] != 'rewritten':
            errors.append(f'old name unexpectedly active: {item["old"]}')
    cases = json.loads((root / 'evals/cases.json').read_text())['cases']
    ids = set()
    for case in cases:
        if case['id'] in ids:
            errors.append(f'duplicate eval case: {case["id"]}')
        ids.add(case['id'])
        for name in case['skills']:
            if name not in names:
                errors.append(f'eval {case["id"]}: unknown skill {name}')
        oracle = case.get('oracle')
        if oracle and (Path(oracle).name != oracle or not (root / 'evals/oracles' / oracle).is_file()):
            errors.append(f'eval {case["id"]}: invalid oracle path')
        if not case.get('review', {}).get('required'):
            errors.append(f'eval {case["id"]}: missing behavioral criteria')
    for directory in ('scripts', 'tests', '.agents/skills', 'evals/oracles'):
        for path in (root / directory).rglob('*.py'):
            try:
                compile(path.read_bytes(), str(path), 'exec')
            except (SyntaxError, ValueError) as exc:
                errors.append(f'{path.relative_to(root)}: {exc}')
    # Static resource links must survive the UI asset move. Fragment/external links are excluded.
    for path in (root / '.agents/skills/ui-design/assets').rglob('*.html'):
        for ref in re.findall(r'(?:src|href)=["\']([^"\']+)["\']', path.read_text()):
            if ref.startswith(('#', 'https:', 'http:', 'data:')):
                continue
            local = ref.split('?', 1)[0].split('#', 1)[0]
            if not (path.parent / local).exists():
                errors.append(f'{path.relative_to(root)}: missing resource {local}')
    return errors


def main() -> int:
    try:
        errors = validate()
    except (OSError, ValueError, TypeError, KeyError) as exc:
        errors = [str(exc)]
    if errors:
        print('\n'.join(errors), file=sys.stderr); return 1
    print('Current skill profiles, resources, mirrors, evaluation fixtures and Python syntax are valid.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""Detect drift between Makefile lint validators and README's Validation section.

Parses every `lint*` Makefile target (tolerating the in-progress lint-static/
lint-diff split) plus the scripts/*.py commands reachable through `verify`'s
prerequisite chain (so validators run only via `analysis`/`test-integration`,
like report_skill_inventory.py and generate_agent_index.py, still count as
"known"). Flags scripts/*.py commands make runs but README's Validation
section omits, and README-listed scripts that no longer exist on disk.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MAKEFILE_PATH = REPO_ROOT / "Makefile"
README_PATH = REPO_ROOT / "README.md"

TARGET_HEADER_RE = re.compile(r"^([A-Za-z0-9_.-]+):\s*(.*)$")
LINT_TARGET_RE = re.compile(r"^lint(-[\w-]+)?$")
COMMAND_RE = re.compile(r"scripts/[A-Za-z0-9_./-]+\.py(?:\s+[^\s#]+)*")
PYTHON_VAR_RE = re.compile(r"^\$\(PYTHON\)\s+")
README_SECTION_RE = re.compile(r"^## Validation\n(.*?)(?:\n## |\Z)", re.S | re.M)
README_LINE_RE = re.compile(r"^-\s*`(.+)`\s*$")


def parse_makefile_targets(text: str) -> dict[str, tuple[list[str], list[str]]]:
    """Return {target name: (prerequisites, recipe lines)}."""
    targets: dict[str, tuple[list[str], list[str]]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("\t"):
            if current is not None:
                targets[current][1].append(line[1:])
            continue
        match = TARGET_HEADER_RE.match(line)
        if match and not line.startswith("."):
            name = match.group(1)
            targets[name] = (match.group(2).split(), [])
            current = name
        else:
            current = None
    return targets


def extract_commands(recipe_lines: list[str]) -> list[str]:
    commands: list[str] = []
    for line in recipe_lines:
        stripped = PYTHON_VAR_RE.sub("", line.strip())
        commands.extend(match.group(0).strip() for match in COMMAND_RE.finditer(stripped))
    return commands


def collect_make_lint_commands(targets: dict[str, tuple[list[str], list[str]]]) -> list[str]:
    """Union of scripts/*.py commands from lint* targets and verify's direct
    prerequisite chain (build-debug/lint/analysis/test-unit/test-integration),
    deduped, order-preserving."""
    names_to_scan = {name for name in targets if LINT_TARGET_RE.match(name)}
    verify_prereqs, _ = targets.get("verify", ([], []))
    names_to_scan.update(name for name in verify_prereqs if name in targets)

    seen: dict[str, None] = {}
    for name in sorted(names_to_scan):
        _, recipe = targets[name]
        for command in extract_commands(recipe):
            seen.setdefault(command, None)
    return list(seen.keys())


def extract_readme_commands(text: str) -> list[str]:
    section_match = README_SECTION_RE.search(text)
    if not section_match:
        return []
    commands = []
    for line in section_match.group(1).splitlines():
        line_match = README_LINE_RE.match(line.strip())
        if not line_match:
            continue
        commands.append(re.sub(r"^python3?\s+", "", line_match.group(1)))
    return commands


def script_identity(command: str) -> str:
    return command.split()[0]


def find_drift(
    make_commands: list[str], readme_commands: list[str]
) -> tuple[list[str], list[str], list[str]]:
    """(missing_from_readme, stale_readme_entries, unwired_readme_entries):
    commands make lint runs that README never mentions (by script path),
    README commands whose script file no longer exists in the tree, and
    README commands whose script exists but no make target runs it."""
    readme_scripts = {script_identity(cmd) for cmd in readme_commands}
    make_scripts = {script_identity(cmd) for cmd in make_commands}
    missing_from_readme = [
        cmd for cmd in make_commands if script_identity(cmd) not in readme_scripts
    ]

    stale_readme = [
        cmd for cmd in readme_commands if not (REPO_ROOT / script_identity(cmd)).is_file()
    ]

    unwired_readme = [
        cmd
        for cmd in readme_commands
        if (REPO_ROOT / script_identity(cmd)).is_file()
        and script_identity(cmd) not in make_scripts
    ]

    return missing_from_readme, stale_readme, unwired_readme


def main() -> int:
    makefile_text = MAKEFILE_PATH.read_text(encoding="utf-8")
    readme_text = README_PATH.read_text(encoding="utf-8")

    targets = parse_makefile_targets(makefile_text)
    make_commands = collect_make_lint_commands(targets)
    readme_commands = extract_readme_commands(readme_text)

    missing_from_readme, stale_readme, unwired_readme = find_drift(
        make_commands, readme_commands
    )

    if not missing_from_readme and not stale_readme and not unwired_readme:
        print("lint_command_docs: pass (README Validation section matches make lint)")
        return 0

    print("lint_command_docs: DRIFT DETECTED")
    if missing_from_readme:
        print("\nRun by make lint but missing from README's Validation section:")
        for command in missing_from_readme:
            print(f"  - {command}")
    if stale_readme:
        print("\nIn README's Validation section but the script no longer exists:")
        for command in stale_readme:
            print(f"  - {command}")
    if unwired_readme:
        print("\nIn README's Validation section but no make target runs it:")
        for command in unwired_readme:
            print(f"  - {command}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

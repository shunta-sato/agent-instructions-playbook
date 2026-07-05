#!/usr/bin/env python3
"""Generate and verify the `metadata.requires` manifest in SKILL.md frontmatter.

Each skill's `metadata.requires` lists every file under its `references/`,
`templates/`, and `scripts/` subdirectories. Agents must load all listed
files before executing the skill (see AGENTS.md "Playbook bootstrap"), so
partial loading — reading SKILL.md and skipping its references — becomes a
detectable contract violation instead of a silent quality loss.

Usage:
    python scripts/update_skill_requires.py --write   # rewrite manifests
    python scripts/update_skill_requires.py --check   # fail if stale (CI)

Only Python stdlib is used.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REQUIRED_SUBDIRS = ("references", "templates", "scripts")
FRONTMATTER_DELIM = "---"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate metadata.requires manifests for repo skills."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="Rewrite stale manifests.")
    mode.add_argument("--check", action="store_true", help="Exit 1 if any manifest is stale.")
    parser.add_argument(
        "--skills-dir",
        default=".agents/skills",
        help="Skills directory relative to repo root.",
    )
    return parser.parse_args()


def required_files(skill_dir: Path) -> list[str]:
    files: list[str] = []
    for sub in REQUIRED_SUBDIRS:
        subdir = skill_dir / sub
        if not subdir.is_dir():
            continue
        for path in sorted(subdir.rglob("*")):
            if path.is_file():
                files.append(path.relative_to(skill_dir).as_posix())
    return files


def split_frontmatter(text: str, path: Path) -> tuple[list[str], str]:
    """Return (frontmatter lines without delimiters, body text)."""
    if not text.startswith(FRONTMATTER_DELIM + "\n"):
        raise ValueError(f"{path}: missing frontmatter opening marker")
    parts = text.split(FRONTMATTER_DELIM, 2)
    if len(parts) != 3:
        raise ValueError(f"{path}: missing frontmatter closing marker")
    return parts[1].strip("\n").splitlines(), parts[2]


def strip_existing_requires(lines: list[str]) -> list[str]:
    """Remove an existing `requires:` block nested under `metadata:`."""
    result: list[str] = []
    skipping = False
    for line in lines:
        if line.strip() == "requires:" and line.startswith("  "):
            skipping = True
            continue
        if skipping:
            if line.startswith("    - "):
                continue
            skipping = False
        result.append(line)
    return result


def build_frontmatter(lines: list[str], requires: list[str], path: Path) -> list[str]:
    """Insert a fresh requires block at the end of the metadata block."""
    lines = strip_existing_requires(lines)
    if not requires:
        return lines

    try:
        meta_idx = next(i for i, line in enumerate(lines) if line.rstrip() == "metadata:")
    except StopIteration:
        raise ValueError(f"{path}: frontmatter has no metadata block")

    end = meta_idx + 1
    while end < len(lines) and (lines[end].startswith("  ") or not lines[end].strip()):
        end += 1

    block = ["  requires:"] + [f"    - {item}" for item in requires]
    return lines[:end] + block + lines[end:]


def render(frontmatter: list[str], body: str) -> str:
    return FRONTMATTER_DELIM + "\n" + "\n".join(frontmatter) + "\n" + FRONTMATTER_DELIM + body


def process_skill(skill_md: Path) -> tuple[str, str]:
    """Return (current text, expected text) for one SKILL.md."""
    text = skill_md.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(text, skill_md)
    requires = required_files(skill_md.parent)
    expected = render(build_frontmatter(frontmatter, requires, skill_md), body)
    return text, expected


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    skills_dir = repo_root / args.skills_dir
    if not skills_dir.is_dir():
        print(f"error: {skills_dir} is not a directory", file=sys.stderr)
        return 2

    stale: list[Path] = []
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        try:
            current, expected = process_skill(skill_md)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        if current == expected:
            continue
        stale.append(skill_md)
        if args.write:
            skill_md.write_text(expected, encoding="utf-8")

    rel = [p.relative_to(repo_root).as_posix() for p in stale]
    if args.check:
        if stale:
            print("Stale metadata.requires manifests (run --write):")
            for name in rel:
                print(f"- {name}")
            return 1
        print("All metadata.requires manifests are current.")
        return 0

    if stale:
        print(f"Updated {len(stale)} manifest(s):")
        for name in rel:
            print(f"- {name}")
    else:
        print("All metadata.requires manifests already current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

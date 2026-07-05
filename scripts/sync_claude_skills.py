#!/usr/bin/env python3
"""Keep `.claude/skills/` in sync with `.agents/skills/` via symlinks.

`.agents/skills/` is the single source of truth for skill content. Claude
Code discovers repo skills under `.claude/skills/<name>/SKILL.md`, so each
skill directory is exposed there as a relative symlink. Symlinks cannot go
stale the way copied mirrors can; this script only creates or removes links
when skills are added, renamed, or deleted.

Usage:
    python scripts/sync_claude_skills.py --write   # create/remove links
    python scripts/sync_claude_skills.py --check   # fail if out of sync (CI)

Only Python stdlib is used.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SOURCE_DIR = Path(".agents/skills")
TARGET_DIR = Path(".claude/skills")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync .claude/skills symlinks from .agents/skills."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="Create/remove symlinks.")
    mode.add_argument("--check", action="store_true", help="Exit 1 if out of sync.")
    parser.add_argument("--repo-root", default="", help="Repository root override.")
    return parser.parse_args()


def repo_root_from_args(explicit_root: str) -> Path:
    if explicit_root:
        return Path(explicit_root).resolve()
    return Path(__file__).resolve().parent.parent


def expected_link_target(name: str) -> Path:
    return Path("..") / ".." / SOURCE_DIR / name


def sync_state(repo_root: Path) -> tuple[list[str], list[str], list[str]]:
    """Return (missing, wrong_target, orphaned) skill link names."""
    source = repo_root / SOURCE_DIR
    target = repo_root / TARGET_DIR
    skill_names = sorted(p.parent.name for p in source.glob("*/SKILL.md"))

    missing: list[str] = []
    wrong: list[str] = []
    for name in skill_names:
        link = target / name
        if not link.is_symlink():
            missing.append(name)
        elif Path(str(link.readlink())) != expected_link_target(name):
            wrong.append(name)

    orphaned: list[str] = []
    if target.is_dir():
        for entry in sorted(target.iterdir()):
            if entry.name not in skill_names and entry.is_symlink():
                orphaned.append(entry.name)
    return missing, wrong, orphaned


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_args(args.repo_root)
    if not (repo_root / SOURCE_DIR).is_dir():
        print(f"error: {SOURCE_DIR} not found", file=sys.stderr)
        return 2

    missing, wrong, orphaned = sync_state(repo_root)

    if args.check:
        problems = (
            [f"missing link: {TARGET_DIR}/{n}" for n in missing]
            + [f"wrong target: {TARGET_DIR}/{n}" for n in wrong]
            + [f"orphaned link: {TARGET_DIR}/{n}" for n in orphaned]
        )
        if problems:
            print("Claude skills mirror is out of sync (run --write):")
            for problem in problems:
                print(f"- {problem}")
            return 1
        print("Claude skills mirror is in sync.")
        return 0

    target = repo_root / TARGET_DIR
    target.mkdir(parents=True, exist_ok=True)
    for name in orphaned + wrong:
        (target / name).unlink()
    for name in missing + wrong:
        (target / name).symlink_to(expected_link_target(name))
    changed = len(missing) + len(wrong) + len(orphaned)
    if changed:
        print(f"Synced {changed} link(s) under {TARGET_DIR}.")
    else:
        print("Claude skills mirror already in sync.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

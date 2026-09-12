#!/usr/bin/env python3
"""Install explicitly selected skills without replacing user-owned paths."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def select_skills(root: Path, packs: list[str], skills: list[str]) -> list[str]:
    catalog = json.loads((root / "packs.json").read_text())["packs"]
    selected = set(skills)
    for pack in packs:
        if pack not in catalog:
            raise ValueError(f"unknown pack: {pack}")
        selected.update(catalog[pack])
    for name in selected:
        if not NAME.fullmatch(name):
            raise ValueError(f"invalid skill name: {name}")
        source = root / "skills" / name
        if source.is_symlink() or not (source / "SKILL.md").is_file():
            raise ValueError(f"missing or linked skill source: {name}")
    return sorted(selected)


def check_parents(target: Path, path: Path) -> None:
    current = target
    for part in path.relative_to(target).parts[:-1]:
        current /= part
        if current.is_symlink() or (current.exists() and not current.is_dir()):
            raise ValueError(f"refusing non-directory or symlink parent: {current}")


def install(root: Path, target: Path, names: list[str], *, init_contract: bool = False,
            dry_run: bool = False) -> list[str]:
    root, target = root.resolve(), target.resolve(strict=True)
    result = subprocess.run(["git", "-C", str(target), "rev-parse", "--show-toplevel"],
                            text=True, capture_output=True)
    if result.returncode or Path(result.stdout.strip()).resolve() != target:
        raise ValueError("target must be a Git worktree root")
    if target == root:
        raise ValueError("do not install the distribution into its own source tree")
    operations: list[tuple[Path, Path | None]] = []
    for name in names:
        if not NAME.fullmatch(name):
            raise ValueError(f"invalid skill name: {name}")
        source = root / "skills" / name
        if source.is_symlink() or not (source / "SKILL.md").is_file():
            raise ValueError(f"missing or linked skill source: {name}")
        dest = target / ".agents" / "skills" / name
        check_parents(target, dest)
        if dest.is_symlink() and dest.resolve() == source.resolve():
            continue
        if dest.exists() or dest.is_symlink():
            raise ValueError(f"refusing to replace existing path: {dest}")
        operations.append((dest, source))
    if init_contract:
        dest = target / "AGENTS.md"
        if dest.exists() or dest.is_symlink():
            raise ValueError("AGENTS.md already exists; integrate the contract explicitly")
        operations.append((dest, None))
    descriptions = [f"{'link' if src else 'create'} {dst}" for dst, src in operations]
    if dry_run:
        return descriptions
    created: list[Path] = []
    try:
        for dest, source in operations:
            check_parents(target, dest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            if source is None:
                with dest.open("x", encoding="utf-8") as out:
                    created.append(dest)
                    out.write((root / "templates" / "AGENTS.md").read_text(encoding="utf-8"))
            else:
                dest.symlink_to(source, target_is_directory=True)
                created.append(dest)
    except (OSError, ValueError):
        # Remove only paths this invocation created; never delete the user's data.
        for path in reversed(created):
            path.unlink(missing_ok=True)
        raise
    return descriptions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workdir", type=Path)
    parser.add_argument("--pack", action="append", default=[])
    parser.add_argument("--skill", action="append", default=[])
    parser.add_argument("--init-contract", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        if not (args.pack or args.skill or args.init_contract):
            raise ValueError("select --pack, --skill or --init-contract; no implicit all-skills install")
        names = select_skills(ROOT, args.pack, args.skill)
        for line in install(ROOT, args.workdir, names, init_contract=args.init_contract,
                            dry_run=args.dry_run):
            print(line)
        print(f"Selected {len(names)} skills. Existing instructions and client settings were not modified.")
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

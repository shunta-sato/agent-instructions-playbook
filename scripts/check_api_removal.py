#!/usr/bin/env python3
"""Verify that removed symbols are actually gone from the codebase.

This is the mechanical half of the quality-gate refactoring exit check.
When a refactor runs under compat-mode `break-allowed`, the old API must
be deleted, not deprecated — this sweep turns "the old symbol is gone"
from a self-reported claim into tool-verified state, the same pattern as
`check_structure.py` for the structure budget.

Usage:
    python scripts/check_api_removal.py --symbol old_name [--symbol ...] [paths]

- Symbols are matched on word boundaries, so `build_record` does not match
  `build_records`.
- Default search set: git-tracked files in the current directory, minus
  history/ledger locations where old names legitimately remain
  (CHANGELOG.md, plans/, reports/, .agents/design-ledger/). Add more
  exemptions with --allow-path.

Exit code 0 when no symbol survives, 1 when hits exist, 2 on usage errors.
Only Python stdlib is used.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

DEFAULT_ALLOWED_PREFIXES = (
    "CHANGELOG.md",
    "plans/",
    "reports/",
    ".agents/design-ledger/",
    # Build artifacts are stale copies, not living code.
    "target/",
    "node_modules/",
    "build/",
    "dist/",
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fail if any removed symbol still appears in the codebase."
    )
    parser.add_argument(
        "--symbol",
        action="append",
        required=True,
        help="Removed symbol name (repeatable).",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files or directories to sweep (default: git-tracked files).",
    )
    parser.add_argument(
        "--allow-path",
        action="append",
        default=[],
        help="Path prefix where hits are permitted (repeatable).",
    )
    return parser.parse_args(argv)


def git_tracked_files(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [root / line.strip() for line in result.stdout.splitlines() if line.strip()]


def collect_files(paths: list[str]) -> list[Path]:
    if not paths:
        return [p for p in git_tracked_files(Path.cwd()) if p.is_file()]
    files: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            files.extend(p for p in sorted(path.rglob("*")) if p.is_file())
        elif path.is_file():
            files.append(path)
    return files


def is_allowed(path: Path, allowed_prefixes: tuple[str, ...]) -> bool:
    rel = path.as_posix()
    for prefix in allowed_prefixes:
        if prefix and prefix in rel:
            return True
    return False


def sweep(
    files: list[Path], symbols: list[str], allowed_prefixes: tuple[str, ...]
) -> list[tuple[str, str, int, str]]:
    patterns = {name: re.compile(rf"\b{re.escape(name)}\b") for name in symbols}
    hits: list[tuple[str, str, int, str]] = []
    for path in files:
        if is_allowed(path, allowed_prefixes):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for name, pattern in patterns.items():
                if pattern.search(line):
                    hits.append((name, path.as_posix(), lineno, line.strip()))
    return hits


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    allowed = tuple(DEFAULT_ALLOWED_PREFIXES) + tuple(args.allow_path)
    files = collect_files(args.paths)
    hits = sweep(files, args.symbol, allowed)

    if hits:
        for name, path, lineno, line in hits:
            print(f"SURVIVING {name} {path}:{lineno}: {line}")
        print(f"api-removal: {len(hits)} surviving reference(s) to removed symbols")
        return 1
    print(
        f"api-removal: pass — {len(args.symbol)} removed symbol(s) absent "
        f"from {len(files)} files"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

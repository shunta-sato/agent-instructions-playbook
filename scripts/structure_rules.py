#!/usr/bin/env python3
"""Source-rule collection and per-file structure-budget analysis.

This module owns *what files to check* and *whether a single file breaches
one of the three canonical structure-budget rules*. It has no knowledge of
the structure-debt baseline (see ``structure_baseline.py``) or of the CLI
(see ``check_structure.py``, which wires this module and the baseline
module together).

Canonical rules (defaults, overridable by the caller's ``argparse.Namespace``):

- ``source-file-lines``: any source file over ``max_source_lines`` total
  lines.
- ``entrypoint-logic-lines``: entrypoint files (``main.rs``, ``src/bin/*.rs``,
  ``main.py``, ``__main__.py``, ``main.go``, ``main.c/cc/cpp``) over
  ``max_entrypoint_lines`` of logic (non-blank, non-comment, excluding Rust
  inline-test blocks).
- ``inline-test-lines``: Rust ``#[cfg(test)]`` module blocks over
  ``max_inline_test_lines`` in a single file; move tests to ``tests/``
  instead.
"""

from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MAX_SOURCE_LINES = 400
DEFAULT_MAX_ENTRYPOINT_LINES = 150
DEFAULT_MAX_INLINE_TEST_LINES = 200

SOURCE_EXTENSIONS = {
    ".rs",
    ".py",
    ".go",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
    ".java",
    ".kt",
    ".swift",
}

LINE_COMMENT_PREFIXES = {
    ".rs": ("//",),
    ".go": ("//",),
    ".ts": ("//",),
    ".tsx": ("//",),
    ".js": ("//",),
    ".jsx": ("//",),
    ".c": ("//",),
    ".cc": ("//",),
    ".cpp": ("//",),
    ".h": ("//",),
    ".hpp": ("//",),
    ".java": ("//",),
    ".kt": ("//",),
    ".swift": ("//",),
    ".py": ("#",),
}

ENTRYPOINT_BASENAMES = {
    "main.rs",
    "main.py",
    "__main__.py",
    "main.go",
    "main.c",
    "main.cc",
    "main.cpp",
}


@dataclass(frozen=True)
class Finding:
    """A single structure-budget breach for one file and one rule."""

    rule: str
    path: str
    value: int
    limit: int
    action: str


def git_tracked_source_files(root: Path) -> list[Path]:
    """Return git-tracked source files under ``root`` (default scan)."""
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []

    files = []
    for line in result.stdout.splitlines():
        path = root / line.strip()
        if path.suffix in SOURCE_EXTENSIONS and path.is_file():
            files.append(path)
    return files


def collect_files(paths: list[str]) -> list[Path]:
    """Resolve CLI path arguments into a concrete list of source files.

    With no explicit paths, falls back to the git-tracked scan of the
    current working directory.
    """
    if not paths:
        return git_tracked_source_files(Path.cwd())

    files: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            files.extend(
                p
                for p in sorted(path.rglob("*"))
                if p.suffix in SOURCE_EXTENSIONS and p.is_file()
            )
        elif path.is_file() and path.suffix in SOURCE_EXTENSIONS:
            files.append(path)
    return files


def is_entrypoint(path: Path) -> bool:
    """Return whether ``path`` is treated as a wiring-only entrypoint file."""
    if path.name in ENTRYPOINT_BASENAMES:
        return True
    return path.suffix == ".rs" and "bin" in path.parts[:-1]


def rust_inline_test_line_indices(lines: list[str]) -> set[int]:
    """Return indices of lines inside ``#[cfg(test)]``-attributed blocks."""
    indices: set[int] = set()
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("#[cfg(test)]"):
            block_start = i
            # Find the first opening brace at or after the attribute, then
            # track brace depth until the block closes.
            depth = 0
            opened = False
            j = i
            while j < len(lines):
                for char in lines[j]:
                    if char == "{":
                        depth += 1
                        opened = True
                    elif char == "}":
                        depth -= 1
                if opened and depth <= 0:
                    break
                j += 1
            end = min(j, len(lines) - 1)
            indices.update(range(block_start, end + 1))
            i = end + 1
        else:
            i += 1
    return indices


def logic_line_count(path: Path, lines: list[str], excluded: set[int]) -> int:
    """Count non-blank, non-comment lines, skipping ``excluded`` indices."""
    prefixes = LINE_COMMENT_PREFIXES.get(path.suffix, ())
    count = 0
    for idx, line in enumerate(lines):
        if idx in excluded:
            continue
        stripped = line.strip()
        if not stripped:
            continue
        if prefixes and stripped.startswith(prefixes):
            continue
        count += 1
    return count


def _finding(rule: str, path: str, value: int, limit: int, action: str) -> Finding:
    """Build a ``Finding`` without repeating five keyword arguments per call site."""
    return Finding(rule=rule, path=path, value=value, limit=limit, action=action)


def check_file(path: Path, args: argparse.Namespace) -> list[Finding]:
    """Check one file against all three canonical structure-budget rules."""
    findings: list[Finding] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        raise SystemExit(f"cannot read {path}: {exc}")
    display = path.as_posix()

    total = len(lines)
    if total > args.max_source_lines:
        findings.append(
            _finding(
                "source-file-lines",
                display,
                total,
                args.max_source_lines,
                "split into modules; record the split decision via "
                "design-balance or function-boundary-governor",
            )
        )

    inline_test_indices: set[int] = set()
    if path.suffix == ".rs":
        inline_test_indices = rust_inline_test_line_indices(lines)
        inline_test_count = len(inline_test_indices)
        if inline_test_count > args.max_inline_test_lines:
            findings.append(
                _finding(
                    "inline-test-lines",
                    display,
                    inline_test_count,
                    args.max_inline_test_lines,
                    "move tests to a sibling test module or tests/ "
                    "integration tests (see project-structure)",
                )
            )

    if is_entrypoint(path):
        logic = logic_line_count(path, lines, inline_test_indices)
        if logic > args.max_entrypoint_lines:
            findings.append(
                _finding(
                    "entrypoint-logic-lines",
                    display,
                    logic,
                    args.max_entrypoint_lines,
                    "move domain logic out of the entrypoint into library "
                    "modules (Rust: lib.rs; see project-structure)",
                )
            )
    return findings

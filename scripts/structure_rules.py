#!/usr/bin/env python3
"""Source-file structure metrics and advisory/hard finding classification."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MAX_SOURCE_LINES = 400  # Backward-compatible context-unit constant.
DEFAULT_ADVISORY_SOURCE_LINES = 600
DEFAULT_MAX_ENTRYPOINT_LINES = 150
DEFAULT_MAX_INLINE_TEST_LINES = 300
DEFAULT_HARD_SOURCE_LINES = 1500
DEFAULT_HARD_ENTRYPOINT_LINES = 400
DEFAULT_HARD_INLINE_TEST_LINES = 800
DEFAULT_MAX_PREEXISTING_HARD_GROWTH = 50

SOURCE_EXTENSIONS = {
    ".rs", ".py", ".go", ".ts", ".tsx", ".js", ".jsx", ".c", ".cc",
    ".cpp", ".h", ".hpp", ".java", ".kt", ".swift",
}
LINE_COMMENT_PREFIXES = {
    ".rs": ("//",), ".go": ("//",), ".ts": ("//",),
    ".tsx": ("//",), ".js": ("//",), ".jsx": ("//",),
    ".c": ("//",), ".cc": ("//",), ".cpp": ("//",),
    ".h": ("//",), ".hpp": ("//",), ".java": ("//",),
    ".kt": ("//",), ".swift": ("//",), ".py": ("#",),
}
ENTRYPOINT_BASENAMES = {
    "main.rs", "main.py", "__main__.py", "main.go", "main.c", "main.cc", "main.cpp",
}


@dataclass(frozen=True)
class Finding:
    rule: str
    path: str
    value: int
    limit: int
    severity: str
    action: str


def is_entrypoint(path: Path) -> bool:
    return path.name in ENTRYPOINT_BASENAMES or (
        path.suffix == ".rs" and "bin" in path.parts[:-1]
    )


def rust_inline_test_line_indices(lines: list[str]) -> set[int]:
    indices: set[int] = set()
    i = 0
    while i < len(lines):
        if not lines[i].strip().startswith("#[cfg(test)]"):
            i += 1
            continue
        block_start = i
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
    return indices


def logic_line_count(path: Path, lines: list[str], excluded: set[int]) -> int:
    prefixes = LINE_COMMENT_PREFIXES.get(path.suffix, ())
    return sum(
        1 for idx, line in enumerate(lines)
        if idx not in excluded
        and line.strip()
        and not (prefixes and line.strip().startswith(prefixes))
    )


def metric_values(path: Path, lines: list[str]) -> dict[str, int]:
    inline = rust_inline_test_line_indices(lines) if path.suffix == ".rs" else set()
    values = {"source-file-lines": len(lines)}
    if path.suffix == ".rs":
        values["inline-test-lines"] = len(inline)
    if is_entrypoint(path):
        values["entrypoint-logic-lines"] = logic_line_count(path, lines, inline)
    return values


def _metric_finding(
    *, rule: str, path: Path, value: int, advisory_limit: int,
    hard_limit: int, mode: str, advisory_action: str, hard_action: str,
) -> Finding | None:
    if mode == "strict" and value > advisory_limit:
        return Finding(rule, path.as_posix(), value, advisory_limit, "blocking", hard_action)
    if mode == "feature" and value > hard_limit:
        return Finding(rule, path.as_posix(), value, hard_limit, "blocking", hard_action)
    if mode == "feature" and value > advisory_limit:
        return Finding(rule, path.as_posix(), value, advisory_limit, "advisory", advisory_action)
    return None


def check_file(path: Path, args: argparse.Namespace) -> list[Finding]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    mode = getattr(args, "mode", "strict")
    hard_source = getattr(args, "hard_source_lines", args.max_source_lines)
    hard_entry = getattr(args, "hard_entrypoint_lines", args.max_entrypoint_lines)
    hard_tests = getattr(args, "hard_inline_test_lines", args.max_inline_test_lines)
    values = metric_values(path, lines)
    specs = [
        (
            "source-file-lines", args.max_source_lines, hard_source,
            "check responsibility; avoid adding a distinct new responsibility",
            "split the current responsibility seam or record a bounded waiver",
        ),
    ]
    if "inline-test-lines" in values:
        specs.append((
            "inline-test-lines", args.max_inline_test_lines, hard_tests,
            "consider a sibling test module when adding more cases",
            "move the current test responsibility to a sibling or integration test module",
        ))
    if "entrypoint-logic-lines" in values:
        specs.append((
            "entrypoint-logic-lines", args.max_entrypoint_lines, hard_entry,
            "keep new domain responsibilities outside the entrypoint",
            "move the current domain responsibility into a library module",
        ))
    findings = []
    for rule, advisory, hard, advisory_action, hard_action in specs:
        finding = _metric_finding(
            rule=rule, path=path, value=values[rule], advisory_limit=advisory,
            hard_limit=hard, mode=mode, advisory_action=advisory_action,
            hard_action=hard_action,
        )
        if finding:
            findings.append(finding)
    return findings

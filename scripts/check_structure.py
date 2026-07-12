#!/usr/bin/env python3
"""Check source files against the canonical structure budget.

This is the mechanical half of the `project-structure` skill and the
structural exit criteria in `quality-gate`. It is state-based: it inspects
what files currently look like, not what a change proposed. That is what
makes it able to catch slow accretion (for example a `main.rs` that grows
by small, individually low-risk appends).

Rules (defaults, overridable by flags):

- source-file-lines: any source file over --max-source-lines total lines.
- entrypoint-logic-lines: entrypoint files (``main.rs``, ``src/bin/*.rs``,
  ``main.py``, ``__main__.py``, ``main.go``, ``main.c/cc/cpp``) over
  --max-entrypoint-lines of logic (non-blank, non-comment, excluding Rust
  inline-test blocks). Entrypoints are wiring, not homes for domain logic.
- inline-test-lines: Rust ``#[cfg(test)]`` module blocks over
  --max-inline-test-lines in a single file. Beyond that, tests belong in a
  sibling test module or ``tests/`` integration tests.

Exit code 0 when clean, 1 when findings exist, 2 on usage errors.
Only Python stdlib is used.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
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
    rule: str
    path: str
    value: int
    limit: int
    action: str


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check source files against the structure budget."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files or directories to check (default: git-tracked source files).",
    )
    parser.add_argument("--max-source-lines", type=int, default=DEFAULT_MAX_SOURCE_LINES)
    parser.add_argument(
        "--max-entrypoint-lines", type=int, default=DEFAULT_MAX_ENTRYPOINT_LINES
    )
    parser.add_argument(
        "--max-inline-test-lines", type=int, default=DEFAULT_MAX_INLINE_TEST_LINES
    )
    parser.add_argument("--json", action="store_true", help="Emit findings as JSON.")
    return parser.parse_args(argv)


def git_tracked_source_files(root: Path) -> list[Path]:
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
    if not paths:
        return git_tracked_source_files(Path.cwd())
    files: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            files.extend(
                p for p in sorted(path.rglob("*")) if p.suffix in SOURCE_EXTENSIONS and p.is_file()
            )
        elif path.is_file() and path.suffix in SOURCE_EXTENSIONS:
            files.append(path)
    return files


def is_entrypoint(path: Path) -> bool:
    if path.name in ENTRYPOINT_BASENAMES:
        return True
    if path.suffix == ".rs" and "bin" in path.parts[:-1]:
        return True
    return False


def rust_inline_test_line_indices(lines: list[str]) -> set[int]:
    """Return indices of lines inside #[cfg(test)]-attributed blocks."""
    indices: set[int] = set()
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("#[cfg(test)]"):
            block_start = i
            # Find the first opening brace at or after the attribute.
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


def check_file(path: Path, args: argparse.Namespace) -> list[Finding]:
    findings: list[Finding] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        raise SystemExit(f"cannot read {path}: {exc}")
    display = path.as_posix()

    total = len(lines)
    if total > args.max_source_lines:
        findings.append(
            Finding(
                rule="source-file-lines",
                path=display,
                value=total,
                limit=args.max_source_lines,
                action=(
                    "split into modules; record the split decision via "
                    "design-balance or function-boundary-governor"
                ),
            )
        )

    inline_test_indices: set[int] = set()
    if path.suffix == ".rs":
        inline_test_indices = rust_inline_test_line_indices(lines)
        inline_test_count = len(inline_test_indices)
        if inline_test_count > args.max_inline_test_lines:
            findings.append(
                Finding(
                    rule="inline-test-lines",
                    path=display,
                    value=inline_test_count,
                    limit=args.max_inline_test_lines,
                    action=(
                        "move tests to a sibling test module or tests/ "
                        "integration tests (see project-structure)"
                    ),
                )
            )

    if is_entrypoint(path):
        logic = logic_line_count(path, lines, inline_test_indices)
        if logic > args.max_entrypoint_lines:
            findings.append(
                Finding(
                    rule="entrypoint-logic-lines",
                    path=display,
                    value=logic,
                    limit=args.max_entrypoint_lines,
                    action=(
                        "move domain logic out of the entrypoint into library "
                        "modules (Rust: lib.rs; see project-structure)"
                    ),
                )
            )
    return findings


def load_structure_waivers(root: Path) -> list[tuple[str, str]]:
    """Load structure_waivers from `.agents/project-policy.yml` at `root`.

    Returns an empty list when the policy file is absent or unreadable, so
    current behavior is unchanged for repos without a policy file.
    """
    policy_path = root / ".agents" / "project-policy.yml"
    if not policy_path.is_file():
        return []
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    waivers: list[tuple[str, str]] = []
    for entry in policy.get("structure_waivers", []):
        if not isinstance(entry, dict):
            continue
        path = entry.get("path")
        reason = entry.get("reason", "")
        if isinstance(path, str) and path:
            waivers.append((path, reason))
    return waivers


def relative_display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def partition_waived_findings(
    findings: list[Finding], root: Path, waivers: list[tuple[str, str]]
) -> tuple[list[Finding], list[tuple[str, str]]]:
    """Split findings into (kept, waived) by repo-relative path prefix match."""
    if not waivers:
        return findings, []
    kept: list[Finding] = []
    waived: list[tuple[str, str]] = []
    for finding in findings:
        rel = relative_display_path(Path(finding.path), root)
        reason = next((r for prefix, r in waivers if rel.startswith(prefix)), None)
        if reason is not None:
            waived.append((rel, reason))
        else:
            kept.append(finding)
    return kept, waived


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    files = collect_files(args.paths)
    if not files:
        print("structure-budget: pass (0 source files checked)")
        return 0

    findings: list[Finding] = []
    for path in files:
        findings.extend(check_file(path, args))

    root = Path.cwd()
    waivers = load_structure_waivers(root)
    findings, waived = partition_waived_findings(findings, root, waivers)

    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2))
    else:
        for finding in findings:
            print(
                f"FINDING {finding.rule} {finding.path}: "
                f"{finding.value} > {finding.limit} — {finding.action}"
            )
        for rel, reason in waived:
            print(f"waived {rel} ({reason})")
        waived_suffix = f", {len(waived)} waived" if waived else ""
        if not findings:
            print(
                f"structure-budget: pass ({len(files)} source files checked{waived_suffix})"
            )
        else:
            print(
                f"structure-budget: {len(findings)} finding(s) in {len(files)} "
                f"files{waived_suffix}"
            )
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

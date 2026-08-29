#!/usr/bin/env python3
"""Check source files against advisory and hard structure guardrails.

Feature mode reports advisory debt but exits non-zero only for hard findings.
Strict mode treats the advisory thresholds as blocking; it is intended for
refactor/structure-hardening work or stricter project policy.

Selection modes:
- explicit paths or default tracked-file scan: strict by default;
- --working-tree or --diff-range: feature by default.

Only Python stdlib is used.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict
from pathlib import Path

try:
    from scripts.structure_rules import (
        DEFAULT_HARD_ENTRYPOINT_LINES,
        DEFAULT_HARD_INLINE_TEST_LINES,
        DEFAULT_HARD_SOURCE_LINES,
        DEFAULT_ADVISORY_SOURCE_LINES,
        DEFAULT_MAX_ENTRYPOINT_LINES,
        DEFAULT_MAX_INLINE_TEST_LINES,
        DEFAULT_MAX_PREEXISTING_HARD_GROWTH,
        DEFAULT_MAX_SOURCE_LINES,
        Finding,
        SOURCE_EXTENSIONS,
        check_file,
        is_entrypoint,
        logic_line_count,
        metric_values,
        rust_inline_test_line_indices,
    )
except ImportError:  # direct execution places scripts/ on sys.path
    from structure_rules import (
        DEFAULT_HARD_ENTRYPOINT_LINES,
        DEFAULT_HARD_INLINE_TEST_LINES,
        DEFAULT_HARD_SOURCE_LINES,
        DEFAULT_ADVISORY_SOURCE_LINES,
        DEFAULT_MAX_ENTRYPOINT_LINES,
        DEFAULT_MAX_INLINE_TEST_LINES,
        DEFAULT_MAX_PREEXISTING_HARD_GROWTH,
        DEFAULT_MAX_SOURCE_LINES,
        Finding,
        SOURCE_EXTENSIONS,
        check_file,
        is_entrypoint,
        logic_line_count,
        metric_values,
        rust_inline_test_line_indices,
    )

__all__ = [
    "DEFAULT_MAX_SOURCE_LINES",
    "Finding",
    "check_file",
    "is_entrypoint",
    "logic_line_count",
    "rust_inline_test_line_indices",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check source-file structure guardrails.")
    parser.add_argument("paths", nargs="*", help="Files/directories (default: tracked sources).")
    parser.add_argument("--mode", choices=("feature", "strict"), default="")
    parser.add_argument("--max-source-lines", type=int, default=DEFAULT_ADVISORY_SOURCE_LINES)
    parser.add_argument("--max-entrypoint-lines", type=int, default=DEFAULT_MAX_ENTRYPOINT_LINES)
    parser.add_argument("--max-inline-test-lines", type=int, default=DEFAULT_MAX_INLINE_TEST_LINES)
    parser.add_argument("--hard-source-lines", type=int, default=DEFAULT_HARD_SOURCE_LINES)
    parser.add_argument("--hard-entrypoint-lines", type=int, default=DEFAULT_HARD_ENTRYPOINT_LINES)
    parser.add_argument("--hard-inline-test-lines", type=int, default=DEFAULT_HARD_INLINE_TEST_LINES)
    parser.add_argument(
        "--max-preexisting-hard-growth",
        type=int,
        default=DEFAULT_MAX_PREEXISTING_HARD_GROWTH,
        help=(
            "In feature mode, allow this many net metric lines when the base "
            "file already exceeded the hard guardrail; larger growth blocks."
        ),
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--working-tree", action="store_true")
    parser.add_argument("--diff-range", metavar="A..B", default="")
    args = parser.parse_args(argv)
    if sum([bool(args.paths), args.working_tree, bool(args.diff_range)]) > 1:
        parser.error("paths, --working-tree, and --diff-range are mutually exclusive")
    for soft_name, hard_name in (
        ("max_source_lines", "hard_source_lines"),
        ("max_entrypoint_lines", "hard_entrypoint_lines"),
        ("max_inline_test_lines", "hard_inline_test_lines"),
    ):
        if getattr(args, hard_name) < getattr(args, soft_name):
            parser.error(f"--{hard_name.replace('_', '-')} must be >= --{soft_name.replace('_', '-')}")
    if args.max_preexisting_hard_growth < 0:
        parser.error("--max-preexisting-hard-growth must be >= 0")
    if not args.mode:
        args.mode = "feature" if args.working_tree or args.diff_range else "strict"
    return args


def repo_root_from_args(explicit_root: str) -> Path:
    return Path(explicit_root).resolve() if explicit_root else Path.cwd()


def git_tracked_source_files(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"], cwd=root, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        return []
    return [
        root / rel for rel in result.stdout.splitlines()
        if (root / rel).suffix in SOURCE_EXTENSIONS and (root / rel).is_file()
    ]


def collect_files(paths: list[str], root: Path | None = None) -> list[Path]:
    if not paths:
        return git_tracked_source_files(root or Path.cwd())
    files: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            files.extend(
                p for p in sorted(path.rglob("*"))
                if p.suffix in SOURCE_EXTENSIONS and p.is_file()
            )
        elif path.is_file() and path.suffix in SOURCE_EXTENSIONS:
            files.append(path)
    return files


def _git_output_z(root: Path, *args: str) -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(root), "-c", "core.quotepath=false", *args],
        capture_output=True, check=True,
    ).stdout
    return [p.decode("utf-8", "surrogateescape") for p in out.split(b"\0") if p]


def changed_paths_from_working_tree(root: Path) -> list[str]:
    paths: list[str] = []
    skip_next = False
    for token in _git_output_z(root, "status", "--porcelain", "-z", "--untracked-files=all"):
        if skip_next:
            paths.append(token)
            skip_next = False
            continue
        status, path = token[:2], token[3:]
        paths.append(path)
        skip_next = "R" in status or "C" in status
    return paths


def changed_paths_from_range(root: Path, diff_range: str) -> list[str]:
    return _git_output_z(root, "diff", "--no-renames", "--name-only", "-z", diff_range)


def existing_source_files(root: Path, rel_paths: list[str]) -> list[Path]:
    candidates = {root / p for p in rel_paths}
    return sorted(
        (p for p in candidates if p.suffix in SOURCE_EXTENSIONS and p.is_file()),
        key=lambda p: p.as_posix(),
    )


def base_ref_from_diff_range(diff_range: str) -> str:
    """Return the left ref from the supported ``A..B``/``A...B`` forms."""
    separator = "..." if "..." in diff_range else ".."
    return diff_range.split(separator, 1)[0]


def git_file_lines(root: Path, ref: str, relpath: str) -> list[str] | None:
    """Read ``relpath`` at ``ref``; ``None`` means the file did not exist."""
    result = subprocess.run(
        ["git", "-C", str(root), "show", f"{ref}:{relpath}"],
        capture_output=True, check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8", "replace").splitlines()


def calibrate_preexisting_hard_debt(
    findings: list[Finding],
    root: Path,
    base_ref: str,
    max_growth: int,
) -> list[Finding]:
    """Apply feature-mode no-material-worsening semantics.

    A file that was already beyond a hard guardrail may still receive a small
    bug fix or modification inside its existing responsibility. Crossing a hard
    guardrail, creating an oversized file, or materially growing existing hard
    debt remains blocking. Responsibility changes still require human/agent
    judgment; line deltas are only the mechanical backstop.
    """
    calibrated: list[Finding] = []
    base_cache: dict[str, dict[str, int] | None] = {}
    for finding in findings:
        if finding.severity != "blocking":
            calibrated.append(finding)
            continue

        relpath = relative_display_path(Path(finding.path), root)
        if relpath not in base_cache:
            lines = git_file_lines(root, base_ref, relpath)
            base_cache[relpath] = (
                metric_values(root / relpath, lines) if lines is not None else None
            )
        base_metrics = base_cache[relpath]
        base_value = base_metrics.get(finding.rule, 0) if base_metrics else 0
        if base_value <= finding.limit:
            calibrated.append(finding)
            continue

        delta = finding.value - base_value
        if delta <= max_growth:
            calibrated.append(
                Finding(
                    rule=finding.rule,
                    path=finding.path,
                    value=finding.value,
                    limit=finding.limit,
                    severity="advisory",
                    action=(
                        "pre-existing hard debt; confirm the diff adds no distinct "
                        f"new responsibility (base={base_value}, delta={delta:+d})"
                    ),
                )
            )
        else:
            calibrated.append(
                Finding(
                    rule=finding.rule,
                    path=finding.path,
                    value=finding.value,
                    limit=finding.limit,
                    severity="blocking",
                    action=(
                        f"pre-existing hard debt grew materially (base={base_value}, "
                        f"delta={delta:+d}, allowed={max_growth}); extract the current seam"
                    ),
                )
            )
    return calibrated


def load_structure_waivers(root: Path) -> list[tuple[str, str]]:
    policy_path = root / ".agents" / "project-policy.yml"
    if not policy_path.is_file():
        return []
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    waivers: list[tuple[str, str]] = []
    for entry in policy.get("structure_waivers", []):
        if isinstance(entry, dict) and isinstance(entry.get("path"), str) and entry["path"]:
            waivers.append((entry["path"], str(entry.get("reason", ""))))
    return waivers


def relative_display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def partition_waived_findings(
    findings: list[Finding], root: Path, waivers: list[tuple[str, str]]
) -> tuple[list[Finding], list[tuple[str, str]]]:
    if not waivers:
        return findings, []
    kept: list[Finding] = []
    waived: list[tuple[str, str]] = []
    for finding in findings:
        rel = relative_display_path(Path(finding.path), root)
        reason = next((r for prefix, r in waivers if rel.startswith(prefix)), None)
        if reason is None:
            kept.append(finding)
        else:
            waived.append((rel, reason))
    return kept, waived


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = repo_root_from_args(args.repo_root)
    if args.working_tree:
        files = existing_source_files(root, changed_paths_from_working_tree(root))
    elif args.diff_range:
        files = existing_source_files(root, changed_paths_from_range(root, args.diff_range))
    else:
        files = collect_files(args.paths, root)
    if not files:
        print(f"structure-budget: pass (mode={args.mode}, 0 source files checked)")
        return 0

    findings = [finding for path in files for finding in check_file(path, args)]
    if args.mode == "feature" and (args.working_tree or args.diff_range):
        base_ref = "HEAD" if args.working_tree else base_ref_from_diff_range(args.diff_range)
        findings = calibrate_preexisting_hard_debt(
            findings, root, base_ref, args.max_preexisting_hard_growth
        )
    findings, waived = partition_waived_findings(findings, root, load_structure_waivers(root))
    blocking = [finding for finding in findings if finding.severity == "blocking"]
    advisories = [finding for finding in findings if finding.severity == "advisory"]

    if args.json:
        print(json.dumps([asdict(finding) for finding in findings], indent=2))
    else:
        for finding in blocking:
            print(
                f"FINDING {finding.rule} {finding.path}: {finding.value} > {finding.limit} — {finding.action}"
            )
        for finding in advisories:
            print(
                f"ADVISORY {finding.rule} {finding.path}: {finding.value} > {finding.limit} — {finding.action}"
            )
        for rel, reason in waived:
            print(f"waived {rel} ({reason})")
        suffix = f", {len(waived)} waived" if waived else ""
        if blocking:
            print(
                f"structure-budget: {len(blocking)} blocking finding(s), "
                f"{len(advisories)} advisory in {len(files)} files (mode={args.mode}{suffix})"
            )
        else:
            print(
                f"structure-budget: pass ({len(advisories)} advisory, "
                f"{len(files)} source files checked, mode={args.mode}{suffix})"
            )
    return 1 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())

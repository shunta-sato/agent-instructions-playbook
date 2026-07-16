#!/usr/bin/env python3
"""CLI entrypoint for the canonical structure budget.

This module is wiring only: it parses arguments, decides whether a
structure-debt baseline applies, collects files, and prints the result. The
per-file rule analysis lives in ``structure_rules.py`` and the optional
baseline schema/reconciliation lives in ``structure_baseline.py`` — see those
modules' docstrings for the rule and baseline contracts, and
``.agents/skills/project-structure/SKILL.md`` for the generative guidance
this check enforces mechanically.

Exit code 0 when clean (including "clean except for accepted debt"), 1 when
findings or baseline errors exist, 2 on a CLI usage error. Only the Python
standard library is used.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

# Whether this file is imported as ``scripts.check_structure`` (package-
# qualified, as tests do) or run directly as a script determines which
# import form resolves the sibling modules; branching on ``__package__``
# is explicit and deterministic, unlike a try/except import guess.
if __package__:
    from scripts.structure_rules import (
        DEFAULT_MAX_ENTRYPOINT_LINES,
        DEFAULT_MAX_INLINE_TEST_LINES,
        DEFAULT_MAX_SOURCE_LINES,
        Finding,
        check_file,
        collect_files,
        is_entrypoint,
        rust_inline_test_line_indices,
    )
    from scripts.structure_baseline import (
        DEFAULT_BASELINE_PATH,
        load_baseline_entries,
        reconcile_baseline,
        resolve_baseline_path,
        to_repo_relpath,
        validate_baseline_entries,
    )
else:
    from structure_rules import (
        DEFAULT_MAX_ENTRYPOINT_LINES,
        DEFAULT_MAX_INLINE_TEST_LINES,
        DEFAULT_MAX_SOURCE_LINES,
        Finding,
        check_file,
        collect_files,
        is_entrypoint,
        rust_inline_test_line_indices,
    )
    from structure_baseline import (
        DEFAULT_BASELINE_PATH,
        load_baseline_entries,
        reconcile_baseline,
        resolve_baseline_path,
        to_repo_relpath,
        validate_baseline_entries,
    )

# Re-exported so existing callers (including tests/test_check_structure.py)
# can keep importing rule-level helpers from this module without change.
__all__ = [
    "check_file",
    "is_entrypoint",
    "rust_inline_test_line_indices",
    "parse_args",
    "main",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check source files against the structure budget."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files or directories to check (default: git-tracked source files).",
    )
    parser.add_argument(
        "--max-source-lines", type=int, default=DEFAULT_MAX_SOURCE_LINES
    )
    parser.add_argument(
        "--max-entrypoint-lines", type=int, default=DEFAULT_MAX_ENTRYPOINT_LINES
    )
    parser.add_argument(
        "--max-inline-test-lines", type=int, default=DEFAULT_MAX_INLINE_TEST_LINES
    )
    parser.add_argument("--json", action="store_true", help="Emit findings as JSON.")
    parser.add_argument(
        "--baseline",
        default=None,
        metavar="PATH",
        help=(
            f"Structure-debt baseline JSON file (default: {DEFAULT_BASELINE_PATH} "
            "if present); a missing --baseline path is a usage error."
        ),
    )
    return parser.parse_args(argv)


def _print_finding(finding: Finding) -> None:
    print(
        f"FINDING {finding.rule} {finding.path}: {finding.value} > "
        f"{finding.limit} — {finding.action}"
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    baseline_path, explicit = resolve_baseline_path(args)
    if baseline_path is not None and explicit and not baseline_path.is_file():
        print(
            f"structure-budget: usage error: --baseline path not found: "
            f"{baseline_path.as_posix()}",
            file=sys.stderr,
        )
        return 2

    files = collect_files(args.paths)
    findings: list[Finding] = []
    for path in files:
        findings.extend(check_file(path, args))

    if baseline_path is None:
        # Unbaselined behavior is unchanged from before the baseline feature (AC2).
        if not files:
            print("structure-budget: pass (0 source files checked)")
            return 0
        if args.json:
            print(json.dumps([asdict(f) for f in findings], indent=2))
        else:
            for finding in findings:
                _print_finding(finding)
            if findings:
                print(
                    f"structure-budget: {len(findings)} finding(s) in "
                    f"{len(files)} files"
                )
            else:
                print(f"structure-budget: pass ({len(files)} source files checked)")
        return 1 if findings else 0

    # Baseline active: reconcile findings against recorded debt, failing
    # closed on any schema, drift, or regression problem. ``scanned_paths``
    # is this invocation's scope, so an untouched baselined file elsewhere
    # in the repo is left neutral rather than misreported as stale.
    entries, schema_issues = load_baseline_entries(baseline_path)
    usable, validation_issues = validate_baseline_entries(entries, args, baseline_path)
    scanned_paths = frozenset(to_repo_relpath(str(path)) for path in files)
    blocking, accepted, reconciliation_issues = reconcile_baseline(
        findings, usable, baseline_path, scanned_paths
    )
    baseline_issues = schema_issues + validation_issues + reconciliation_issues
    baseline_issues.sort(key=lambda i: (i.kind, i.path, i.rule))
    blocking.sort(key=lambda f: (f.path, f.rule))
    accepted.sort(key=lambda f: (f.path, f.rule))

    disp = baseline_path.as_posix()
    if args.json:
        payload = {
            "findings": [asdict(f) for f in blocking],
            "accepted_debt": [asdict(f) for f in accepted],
            "baseline_errors": [asdict(i) for i in baseline_issues],
            "baseline_path": disp,
        }
        print(json.dumps(payload, indent=2))
    else:
        for finding in blocking:
            _print_finding(finding)
        for issue in baseline_issues:
            print(f"BASELINE-ERROR {issue.kind} {issue.path}: {issue.detail}")
        for finding in accepted:
            print(
                f"ACCEPTED-DEBT {finding.rule} {finding.path}: "
                f"{finding.value} > {finding.limit} (baseline {disp})"
            )
        if blocking or baseline_issues:
            print(
                f"structure-budget: {len(blocking)} finding(s), "
                f"{len(baseline_issues)} baseline error(s) in {len(files)} "
                f"files (baseline {disp})"
            )
        elif accepted:
            plural = "y" if len(accepted) == 1 else "ies"
            print(
                f"structure-budget: {len(accepted)} accepted-debt entr{plural} "
                f"in {len(files)} files (baseline {disp}) — accepted debt is "
                "not clean; it must not worsen"
            )
        else:
            print(
                f"structure-budget: pass ({len(files)} source files checked, "
                f"baseline {disp})"
            )
    return 1 if (blocking or baseline_issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())

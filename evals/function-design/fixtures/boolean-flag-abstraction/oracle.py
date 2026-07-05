#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from oracle_common import Check, assert_checks, bool_flag_count, contains_any, function_names, ledger_text, production_text, run_unittest  # noqa: E402


FORBIDDEN_FLAGS = (
    r"include_?tax",
    r"include_?notes",
    r"dry_?run",
    r"\blegacy\b",
    r"\bmode\b",
    r"skip_?\w+",
)


def main() -> int:
    workspace = Path(sys.argv[1]).resolve()
    tests_ok, test_output = run_unittest(workspace)
    names = function_names(workspace)
    text = production_text(workspace)
    ledger = ledger_text(workspace).lower()
    forbidden = contains_any(text, FORBIDDEN_FLAGS)

    checks = [
        Check("behavior tests pass", tests_ok, test_output),
        Check("boolean flag count is zero", bool_flag_count(workspace) == 0, f"count={bool_flag_count(workspace)}"),
        Check("forbidden flag names absent", not forbidden, ", ".join(forbidden)),
        Check("old flag-based payload function removed", "build_invoice_payload" not in names),
        Check("summary concept function exists", "build_invoice_summary" in names),
        Check("tax concept function exists", "build_tax_invoice_payload" in names),
        Check("audit concept function exists", "build_invoice_audit_record" in names),
        Check(
            "call sites use concept functions",
            all(
                name in (workspace / "src" / "jobs.py").read_text(encoding="utf-8")
                for name in ("build_invoice_summary", "build_tax_invoice_payload", "build_invoice_audit_record")
            ),
        ),
        Check("ledger records replaced abstraction", "replaced abstraction" in ledger),
        Check("ledger records flag smell", "include_tax" in ledger or "boolean" in ledger),
    ]
    return assert_checks(checks)


if __name__ == "__main__":
    raise SystemExit(main())

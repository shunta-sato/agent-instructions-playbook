#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from oracle_common import Check, assert_checks, function_names, ledger_text, production_text, run_unittest  # noqa: E402


OLD_HELPERS = {
    "format_invoice_total",
    "format_refund_total",
    "format_credit_total",
    "format_subscription_total",
}
VAGUE_NAME_RE = re.compile(r"\bdef\s+\w*(?:common|helper|handle|process|util)\w*\s*\(", re.I)


def main() -> int:
    workspace = Path(sys.argv[1]).resolve()
    tests_ok, test_output = run_unittest(workspace)
    names = function_names(workspace)
    text = production_text(workspace)
    ledger = ledger_text(workspace).lower()
    old_helpers_present = sorted(OLD_HELPERS & names)

    checks = [
        Check("behavior tests pass", tests_ok, test_output),
        Check("domain money formatter exists", "format_money" in names),
        Check("sibling total helpers are gone", not old_helpers_present, ", ".join(old_helpers_present)),
        Check("no vague helper names", not VAGUE_NAME_RE.search(text)),
        Check(
            "billing call sites use the new abstraction",
            "format_money" in (workspace / "src" / "billing.py").read_text(encoding="utf-8"),
        ),
        Check("ledger records merge or replacement", "merge" in ledger or "replaced abstraction" in ledger),
        Check("ledger records old helpers", "format_invoice_total" in ledger and "format_refund_total" in ledger),
        Check("ledger records new abstraction", "format_money" in ledger),
    ]
    return assert_checks(checks)


if __name__ == "__main__":
    raise SystemExit(main())

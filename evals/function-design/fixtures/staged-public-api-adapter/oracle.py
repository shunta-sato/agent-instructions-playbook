#!/usr/bin/env python3
from __future__ import annotations

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from oracle_common import Check, assert_checks, contains_any, find_function, function_names, ledger_text, production_text, run_unittest  # noqa: E402


BROAD_COMPAT = (
    r"compat(?:ibility)?_layer",
    r"legacy_account_record_adapter",
    r"shim_registry",
)


def function_calls(node: ast.AST, name: str) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id == name:
            return True
    return False


def main() -> int:
    workspace = Path(sys.argv[1]).resolve()
    tests_ok, test_output = run_unittest(workspace)
    names = function_names(workspace)
    service_text = (workspace / "src" / "service.py").read_text(encoding="utf-8")
    text = production_text(workspace)
    ledger = ledger_text(workspace).lower()
    adapter = find_function(workspace / "src" / "accounts.py", "build_account_record")
    broad = contains_any(text, BROAD_COMPAT)

    checks = [
        Check("behavior tests pass", tests_ok, test_output),
        Check("new internal abstraction exists", "build_customer_profile" in names),
        Check("public adapter still exists for compatibility", "build_account_record" in names),
        Check("internal service migrated to new abstraction", "build_account_record" not in service_text),
        Check("internal service uses customer profile", "build_customer_profile" in service_text),
        Check("public adapter is thin", adapter is not None and len(adapter.body) <= 4),
        Check("public adapter delegates to new abstraction", adapter is not None and function_calls(adapter, "build_customer_profile")),
        Check("no broad compatibility layer", not broad, ", ".join(broad)),
        Check("ledger records staged adapter", "staged adapter" in ledger),
        Check("ledger records removal condition", "removal condition" in ledger),
        Check("ledger names adapter", "build_account_record" in ledger),
        Check("ledger names new abstraction", "build_customer_profile" in ledger),
    ]
    return assert_checks(checks)


if __name__ == "__main__":
    raise SystemExit(main())

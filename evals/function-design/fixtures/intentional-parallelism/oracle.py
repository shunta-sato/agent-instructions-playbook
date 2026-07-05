#!/usr/bin/env python3
from __future__ import annotations

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from oracle_common import Check, assert_checks, function_names, ledger_text, parse_source, run_unittest, source_files  # noqa: E402


FORBIDDEN_HELPERS = {"parse_int", "_parse_int", "coerce_int", "_coerce_int", "parse_value", "_parse_value"}
FORBIDDEN_FLAG_ARGS = {"required", "optional", "strict", "mode"}


def flag_args(workspace: Path) -> list[str]:
    found: list[str] = []
    for path in source_files(workspace):
        tree = parse_source(path)
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            for arg in list(node.args.args) + list(node.args.kwonlyargs):
                if arg.arg in FORBIDDEN_FLAG_ARGS:
                    found.append(f"{node.name}.{arg.arg}")
    return found


def main() -> int:
    workspace = Path(sys.argv[1]).resolve()
    tests_ok, test_output = run_unittest(workspace)
    names = function_names(workspace)
    ledger = ledger_text(workspace).lower()
    helpers = sorted(FORBIDDEN_HELPERS & names)
    flags = flag_args(workspace)

    checks = [
        Check("behavior tests pass", tests_ok, test_output),
        Check("strict parser remains", "parse_required_int" in names),
        Check("optional parser remains", "parse_optional_int" in names),
        Check("no generic shared parse helper", not helpers, ", ".join(helpers)),
        Check("no mode/required flag argument", not flags, ", ".join(flags)),
        Check("ledger records intentional duplication", "intentional duplication" in ledger or "keep parallel" in ledger),
        Check("ledger cites error behavior", "error behavior" in ledger),
        Check("ledger cites future divergence", "future divergence" in ledger),
    ]
    return assert_checks(checks)


if __name__ == "__main__":
    raise SystemExit(main())

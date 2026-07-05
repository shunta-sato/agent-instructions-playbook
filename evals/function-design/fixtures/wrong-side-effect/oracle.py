#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from oracle_common import (  # noqa: E402
    Check,
    assert_checks,
    bool_flag_count,
    contains_any,
    function_names,
    ledger_text,
    production_reference_count,
    production_text,
    run_unittest,
)


FORBIDDEN = (
    r"without[_a-z]*side[_a-z]*effects?",
    r"withoutSideEffects?",
    r"dry_?run",
    r"skip_?persist",
    r"skipPersist",
    r"normalize_and_save_user2",
    r"new_?normalize",
)


def main() -> int:
    workspace = Path(sys.argv[1]).resolve()
    tests_ok, test_output = run_unittest(workspace)
    names = function_names(workspace)
    text = production_text(workspace)
    ledger = ledger_text(workspace).lower()
    old_refs = production_reference_count(workspace, "normalize_and_save_user")
    forbidden_found = contains_any(text, FORBIDDEN)

    checks = [
        Check("behavior tests pass", tests_ok, test_output),
        Check("old mixed abstraction has zero production references", old_refs == 0, f"refs={old_refs}"),
        Check("pure normalizer exists", "normalize_user" in names),
        Check("effectful persistence boundary exists", "save_normalized_user" in names),
        Check("no boolean persistence suppression flag", bool_flag_count(workspace) == 0),
        Check("no forbidden compatibility sibling pattern", not forbidden_found, ", ".join(forbidden_found)),
        Check(
            "import call site migrated to effectful boundary",
            "save_normalized_user" in (workspace / "src" / "importer.py").read_text(encoding="utf-8"),
        ),
        Check(
            "preview call site uses pure normalizer",
            "normalize_user" in (workspace / "src" / "preview.py").read_text(encoding="utf-8"),
        ),
        Check("ledger records replaced abstraction", "replaced abstraction" in ledger),
        Check("ledger names old abstraction", "normalize_and_save_user" in ledger),
        Check("ledger names new abstractions", "normalize_user" in ledger and "save_normalized_user" in ledger),
    ]
    return assert_checks(checks)


if __name__ == "__main__":
    raise SystemExit(main())

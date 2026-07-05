#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from oracle_common import Check, assert_checks, function_names, ledger_text, run_unittest  # noqa: E402


VAGUE_HELPER_RE = re.compile(r"(?:common|helper|util|fixture)", re.I)


def src_snapshot(path: Path) -> dict[str, str]:
    src_dir = path / "src"
    return {
        item.relative_to(src_dir).as_posix(): item.read_text(encoding="utf-8")
        for item in sorted(src_dir.rglob("*.py"))
        if item.is_file()
    }


def main() -> int:
    workspace = Path(sys.argv[1]).resolve()
    fixture_root = Path(__file__).resolve().parent
    tests_ok, test_output = run_unittest(workspace)
    baseline_snapshot = src_snapshot(fixture_root)
    workspace_snapshot = src_snapshot(workspace)
    names = function_names(workspace)
    ledger = ledger_text(workspace).lower()
    vague_names = sorted(name for name in names if VAGUE_HELPER_RE.search(name))
    extra_files = sorted(set(workspace_snapshot) - set(baseline_snapshot))

    checks = [
        Check("behavior tests pass", tests_ok, test_output),
        Check("production source files unchanged", workspace_snapshot == baseline_snapshot),
        Check("no extra production helper files", not extra_files, ", ".join(extra_files)),
        Check("no vague helper functions", not vague_names, ", ".join(vague_names)),
        Check("ledger/report records no-op or keep parallel", "no-op" in ledger or "keep parallel" in ledger),
        Check("ledger cites test fixture duplication", "test fixture" in ledger or "fixture data" in ledger),
    ]
    return assert_checks(checks)


if __name__ == "__main__":
    raise SystemExit(main())

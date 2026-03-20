#!/usr/bin/env python3
"""Smoke checks for skill artifact helper entrypoints."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def assert_ok(proc: subprocess.CompletedProcess[str], context: str) -> None:
    if proc.returncode != 0:
        raise RuntimeError(f"{context} failed\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}")


def assert_fails(proc: subprocess.CompletedProcess[str], context: str) -> None:
    if proc.returncode == 0:
        raise RuntimeError(f"{context} unexpectedly succeeded\nstdout:\n{proc.stdout}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="skill-helper-smoke-") as temp_dir:
        root = Path(temp_dir)

        execplan = run(
            ["python", str(REPO_ROOT / "scripts/init_execplan.py"), "--slug", "sample-plan", "--output", str(root / "plans" / "sample-plan.md")],
            cwd=REPO_ROOT,
        )
        assert_ok(execplan, "init_execplan first run")

        bug = run(
            ["python", str(REPO_ROOT / "scripts/init_bug_report.py"), "--slug", "sample-bug", "--output", str(root / "reports" / "bug-reports" / "sample-bug.md")],
            cwd=REPO_ROOT,
        )
        assert_ok(bug, "init_bug_report first run")

        matrix = run(
            [
                "python",
                str(REPO_ROOT / "scripts/init_concurrency_matrix.py"),
                "--slug",
                "sample-concurrency",
                "--output",
                str(root / "reports" / "concurrency" / "sample-concurrency.md"),
            ],
            cwd=REPO_ROOT,
        )
        assert_ok(matrix, "init_concurrency_matrix first run")

        overwrite_blocked = run(
            ["python", str(REPO_ROOT / "scripts/init_execplan.py"), "--slug", "sample-plan", "--output", str(root / "plans" / "sample-plan.md")],
            cwd=REPO_ROOT,
        )
        assert_fails(overwrite_blocked, "overwrite without --force")

        overwrite_allowed = run(
            [
                "python",
                str(REPO_ROOT / "scripts/init_execplan.py"),
                "--slug",
                "sample-plan",
                "--output",
                str(root / "plans" / "sample-plan.md"),
                "--force",
            ],
            cwd=REPO_ROOT,
        )
        assert_ok(overwrite_allowed, "overwrite with --force")

    print("skill helper smoke checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

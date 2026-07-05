"""Shared helpers for function-design behavioral fixture oracles."""

from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str = ""


def source_files(workspace: Path) -> list[Path]:
    src_dir = workspace / "src"
    if not src_dir.is_dir():
        return []
    return sorted(path for path in src_dir.rglob("*.py") if path.is_file())


def production_text(workspace: Path) -> str:
    parts = []
    for path in source_files(workspace):
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def all_text(workspace: Path) -> str:
    parts = []
    for path in sorted(workspace.rglob("*")):
        if path.is_file() and path.suffix in {".py", ".md", ".txt", ".json"}:
            parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def ledger_text(workspace: Path) -> str:
    path = workspace / ".agents" / "design-ledger" / "function-boundaries.md"
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def parse_source(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def function_names(workspace: Path) -> set[str]:
    names: set[str] = set()
    for path in source_files(workspace):
        tree = parse_source(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                names.add(node.name)
    return names


def find_function(path: Path, name: str) -> ast.FunctionDef | None:
    if not path.is_file():
        return None
    tree = parse_source(path)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def production_reference_count(workspace: Path, name: str) -> int:
    pattern = re.compile(rf"\b{re.escape(name)}\b")
    return sum(len(pattern.findall(path.read_text(encoding="utf-8"))) for path in source_files(workspace))


def contains_any(text: str, patterns: Iterable[str]) -> list[str]:
    found: list[str] = []
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            found.append(pattern)
    return found


def run_unittest(workspace: Path) -> tuple[bool, str]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(workspace) if not existing else f"{workspace}{os.pathsep}{existing}"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=workspace,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.returncode == 0, completed.stdout.strip()


def bool_flag_count(workspace: Path) -> int:
    count = 0
    for path in source_files(workspace):
        tree = parse_source(path)
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            defaults = list(node.args.defaults) + list(node.args.kw_defaults)
            for default in defaults:
                if isinstance(default, ast.Constant) and isinstance(default.value, bool):
                    count += 1
    return count


def assert_checks(checks: list[Check]) -> int:
    failed = [check for check in checks if not check.passed]
    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        suffix = f" - {check.detail}" if check.detail else ""
        print(f"{status}: {check.name}{suffix}")
    return 0 if not failed else 1

#!/usr/bin/env python3
"""Read-only, scoped Python diagnostics. No score, semantic verdict or automatic repair."""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

VERSION = "1"


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-c", "core.fsmonitor=false", "-C", str(root), *args],
        text=True, stderr=subprocess.PIPE, timeout=15,
    ).strip()


def safe_path(root: Path, name: str) -> Path:
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts or ".git" in relative.parts:
        raise ValueError(f"Not a literal repository-relative path: {name}")
    path = root / relative
    for candidate in [path, *path.parents]:
        if candidate == root:
            break
        if candidate.is_symlink():
            raise ValueError(f"Symlink is not analyzed: {name}")
    if not path.exists():
        raise ValueError(f"Missing selected path: {name}")
    return path


def function_nodes(node: ast.AST):
    """Count a function's own statements, excluding separately owned nested bodies."""
    yield node
    for child in ast.iter_child_nodes(node):
        if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            yield from function_nodes(child)


def inspect(root: Path, paths: list[str], kind: str) -> dict:
    root = root.resolve()
    if kind not in {"product", "test", "generated"} or not paths:
        raise ValueError("Explicit paths and one source category are required")
    if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise ValueError("root must be the repository worktree root")
    for name in paths:
        safe_path(root, name)
    # --literal-pathspecs prevents pathspec magic from widening the requested scope.
    output = subprocess.check_output(
        ["git", "-c", "core.fsmonitor=false", "--literal-pathspecs", "-C", str(root),
         "ls-files", "--cached", "-z", "--", *paths], timeout=15,
    )
    names = sorted({s.decode("utf-8") for s in output.split(b"\0") if s})
    report = {
        "schema_version": 1, "status": "diagnostic-only", "kind": kind,
        "analyzer_version": VERSION, "analyzer_sha256": sha256(Path(__file__).read_bytes()),
        "python_version": sys.version.split()[0], "head": git(root, "rev-parse", "HEAD"),
        "scope": paths, "files": [], "exact_clone_candidates": [], "errors": [],
    }
    clones: dict[str, list] = {}
    for name in names:
        if not name.endswith(".py"):
            continue
        try:
            path = safe_path(root, name)
            data = path.read_bytes()
            tree = ast.parse(data, filename=name)
            functions = []
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                fingerprint = copy.deepcopy(node)
                fingerprint.name = "FUNCTION_NAME"
                key = sha256(ast.dump(fingerprint, include_attributes=False).encode())
                location = {"path": name, "name": node.name, "line": node.lineno}
                clones.setdefault(key, []).append(location)
                functions.append({
                    **location, "line_span": node.end_lineno - node.lineno + 1,
                    "branch_statements": sum(isinstance(n, (ast.If, ast.For, ast.AsyncFor,
                        ast.While, ast.Try, ast.Match)) for n in function_nodes(node)),
                })
            report["files"].append({"path": name, "sha256": sha256(data),
                                    "physical_lines": len(data.splitlines()), "functions": functions})
        except (OSError, SyntaxError, ValueError) as error:
            report["errors"].append({"path": name, "error": str(error)})
    report["exact_clone_candidates"] = [
        {"ast_sha256": key, "locations": entries}
        for key, entries in sorted(clones.items()) if len(entries) > 1
    ]
    if not report["files"]:
        report["errors"].append({"error": "No tracked Python files analyzed"})
    if report["errors"]:
        report["status"] = "incomplete"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--path", required=True, action="append")
    parser.add_argument("--kind", required=True, choices=["product", "test", "generated"])
    args = parser.parse_args()
    try:
        report = inspect(args.root, args.path, args.kind)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(json.dumps({"status": "incomplete", "errors": [str(error)]}))
        return 1
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

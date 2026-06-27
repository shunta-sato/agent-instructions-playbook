#!/usr/bin/env python3
"""Estimate Agent context file sizes without relying on a tokenizer."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
from fnmatch import fnmatch
from pathlib import Path
from typing import Any


SECRET_PATTERNS = (
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*secret*",
    "*credential*",
    "*token*",
    "id_rsa",
    "id_ed25519",
)
HIDDEN_ALLOWLIST = {".agent", ".agents", ".github"}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__"}
VOLATILE_RE = re.compile(
    r"(\b20\d{2}-\d{2}-\d{2}\b|\b\d{2}:\d{2}:\d{2}\b|"
    r"\b[0-9a-f]{7,40}\b|test output|grep output|stack trace|"
    r"temporary plan|issue log|request id|worker-specific)",
    re.I,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Estimate AGENTS/.agent context size.")
    parser.add_argument("--root", default=".", help="Repository root to inspect.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--markdown", action="store_true", help="Emit Markdown output.")
    parser.add_argument("--include-hidden", action="store_true", help="Include hidden paths.")
    return parser.parse_args()


def rel_path(path: Path, root: Path) -> str:
    return "." if path == root else path.relative_to(root).as_posix()


def is_secret_like(path: Path) -> bool:
    lowered_parts = [part.lower() for part in path.parts]
    lowered_path = path.as_posix().lower()
    for pattern in SECRET_PATTERNS:
        pattern_lower = pattern.lower()
        if any(fnmatch(part, pattern_lower) for part in lowered_parts):
            return True
        if fnmatch(lowered_path, pattern_lower) or pattern_lower.strip("*") in lowered_path:
            return True
    return False


def should_skip(path: Path, root: Path, include_hidden: bool) -> bool:
    if path == root:
        return False
    if is_secret_like(path):
        return True
    parts = path.relative_to(root).parts
    if not parts:
        return False
    if include_hidden:
        return False
    if parts[0] in HIDDEN_ALLOWLIST:
        return False
    return any(part.startswith(".") for part in parts)


def walk_candidate_files(root: Path, include_hidden: bool) -> list[Path]:
    candidates: list[Path] = []
    for current, dirnames, filenames in os.walk(root):
        current_path = Path(current)
        kept_dirs: list[str] = []
        for dirname in sorted(dirnames):
            dirpath = current_path / dirname
            if dirname in SKIP_DIRS or should_skip(dirpath, root, include_hidden):
                continue
            kept_dirs.append(dirname)
        dirnames[:] = kept_dirs

        for filename in sorted(filenames):
            path = current_path / filename
            if should_skip(path, root, include_hidden):
                continue
            rel = rel_path(path, root)
            if filename == "AGENTS.md" or rel.startswith(".agent/ctx/") or rel.startswith(".agent/maps/"):
                candidates.append(path)
    return candidates


def classify(path: Path, root: Path) -> tuple[str, bool]:
    rel = rel_path(path, root)
    if path.name == "AGENTS.md":
        return "agents", True
    if rel.startswith(".agent/ctx/"):
        return "agent_ctx", True
    if rel.startswith(".agent/maps/"):
        return "agent_map", True
    return "other", False


def file_stats(path: Path, root: Path) -> dict[str, Any]:
    data = path.read_bytes()
    text = data.decode("utf-8", errors="replace")
    kind, stable_candidate = classify(path, root)
    return {
        "file": rel_path(path, root),
        "kind": kind,
        "bytes": len(data),
        "lines": 0 if not text else len(text.splitlines()),
        "rough_token_estimate": math.ceil(len(data) / 4),
        "stable_prefix_candidate": stable_candidate,
        "volatile_looking": bool(VOLATILE_RE.search(text)),
    }


def estimate(root: Path, include_hidden: bool) -> dict[str, Any]:
    root = root.resolve()
    files = [file_stats(path, root) for path in walk_candidate_files(root, include_hidden)]
    warnings: list[str] = []

    agents_files = [item for item in files if item["kind"] == "agents"]
    combined_agents_bytes = sum(item["bytes"] for item in agents_files)
    for item in files:
        if item["file"] == "AGENTS.md" and item["bytes"] > 8 * 1024:
            warnings.append(f"root AGENTS.md is {item['bytes']} bytes; keep under 8 KiB when possible")
        if item["kind"] == "agent_ctx" and item["bytes"] > 12 * 1024:
            warnings.append(f"{item['file']} is {item['bytes']} bytes; keep .agent/ctx files under 12 KiB")
        if item["file"] == ".agent/maps/skills.md" and item["bytes"] > 8 * 1024:
            warnings.append(".agent/maps/skills.md is over 8 KiB; split or compress routing")
        if item["stable_prefix_candidate"] and item["volatile_looking"]:
            warnings.append(f"{item['file']} contains volatile-looking text; keep repo-stable docs stable")
    if combined_agents_bytes > 32 * 1024:
        warnings.append(
            f"combined AGENTS.md chain is {combined_agents_bytes} bytes; keep under 32 KiB when possible"
        )

    return {"root": ".", "files": sorted(files, key=lambda item: item["file"]), "warnings": warnings}


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "## Context size estimate",
        "",
        "| File | Bytes | Lines | Rough token estimate | Stable prefix candidate |",
        "|---|---:|---:|---:|---:|",
    ]
    for item in result["files"]:
        stable = "yes" if item["stable_prefix_candidate"] else "no"
        lines.append(
            f"| `{item['file']}` | {item['bytes']} | {item['lines']} | "
            f"{item['rough_token_estimate']} | {stable} |"
        )
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {warning}" for warning in result["warnings"]] or ["- none"])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    emit_markdown = args.markdown or not args.json
    result = estimate(Path(args.root), include_hidden=args.include_hidden)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    if emit_markdown:
        if args.json:
            print()
        print(render_markdown(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

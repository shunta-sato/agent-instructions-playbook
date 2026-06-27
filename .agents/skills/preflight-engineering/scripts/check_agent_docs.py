#!/usr/bin/env python3
"""Check AGENTS.md and .agent context structure for preflight readiness."""

from __future__ import annotations

import argparse
import json
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
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__"}
VOLATILE_RE = re.compile(
    r"(\b20\d{2}-\d{2}-\d{2}\b|\b\d{2}:\d{2}:\d{2}\b|"
    r"\b[0-9a-f]{7,40}\b|test output|grep output|stack trace|"
    r"temporary plan|issue log|request id|worker-specific)",
    re.I,
)
SKILL_BODY_RE = re.compile(r"(?ms)^---\s*\nname:\s*[a-z0-9-]+.*?\n---\s*\n## ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Agent docs preflight structure.")
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
    if path == root or include_hidden:
        return False
    parts = path.relative_to(root).parts
    if parts and parts[0] in {".agent", ".agents", ".github"}:
        return False
    return any(part.startswith(".") for part in parts)


def safe_read(path: Path, root: Path, include_hidden: bool) -> str | None:
    if is_secret_like(path) or should_skip(path, root, include_hidden):
        return None
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def walk_files(root: Path, include_hidden: bool) -> list[Path]:
    files: list[Path] = []
    for current, dirnames, filenames in os.walk(root):
        current_path = Path(current)
        kept_dirs: list[str] = []
        for dirname in sorted(dirnames):
            dirpath = current_path / dirname
            if dirname in SKIP_DIRS or is_secret_like(dirpath) or should_skip(dirpath, root, include_hidden):
                continue
            kept_dirs.append(dirname)
        dirnames[:] = kept_dirs
        for filename in sorted(filenames):
            path = current_path / filename
            if is_secret_like(path) or should_skip(path, root, include_hidden):
                continue
            files.append(path)
    return files


def count_top_level_files(files: list[Path], root: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in files:
        parts = path.relative_to(root).parts
        if len(parts) > 1:
            counts[parts[0]] = counts.get(parts[0], 0) + 1
    return counts


def check(root: Path, include_hidden: bool) -> dict[str, Any]:
    root = root.resolve()
    files = walk_files(root, include_hidden)
    root_agents = root / "AGENTS.md"
    agent_ctx = [path for path in files if rel_path(path, root).startswith(".agent/ctx/")]
    agent_maps = [path for path in files if rel_path(path, root).startswith(".agent/maps/")]
    nested_agents = [
        path for path in files if path.name == "AGENTS.md" and rel_path(path, root) != "AGENTS.md"
    ]

    passes: list[str] = []
    warnings: list[str] = []
    decisions: list[str] = []

    root_text = safe_read(root_agents, root, include_hidden) if root_agents.exists() else None
    if root_text is None:
        warnings.append("root AGENTS.md is missing or could not be read")
        decisions.append("Create or confirm root AGENTS.md before long-running preflight work")
    else:
        passes.append("root AGENTS.md exists")
        if VOLATILE_RE.search(root_text):
            warnings.append("root AGENTS.md contains volatile-looking text")
        else:
            passes.append("root AGENTS.md has no obvious volatile data")
        if SKILL_BODY_RE.search(root_text):
            warnings.append("root AGENTS.md appears to contain pasted skill body frontmatter")
        else:
            passes.append("root AGENTS.md does not appear to paste skill bodies")
        if agent_ctx or agent_maps:
            if ".agent/ctx" in root_text or ".agent/maps" in root_text:
                passes.append("root AGENTS.md references .agent context/map paths")
            else:
                warnings.append(".agent context/maps exist but root AGENTS.md does not reference them")

    counts = count_top_level_files(files, root)
    large_without_nested = []
    for dirname, count in sorted(counts.items()):
        if dirname in {".agents", "reports", "evals"}:
            continue
        nested_path = root / dirname / "AGENTS.md"
        if count >= 40 and nested_path not in nested_agents:
            large_without_nested.append(f"{dirname}/ ({count} files)")
    if large_without_nested:
        warnings.append(
            "large top-level domains may need nested AGENTS.md: "
            + ", ".join(large_without_nested)
        )
        decisions.append("Confirm whether large domains need nested AGENTS.md rules")
    else:
        passes.append("no large top-level domain requires an obvious nested AGENTS.md candidate")

    for path in agent_ctx + agent_maps:
        rel = rel_path(path, root)
        if len(rel) > 96 or not re.match(r"^[A-Za-z0-9_./-]+$", rel):
            warnings.append(f"agent context path is not short/readable: {rel}")
    if agent_ctx or agent_maps:
        passes.append(".agent context/map paths are short and readable")

    passes.append("secret-like paths are path-only candidates and were not opened")
    return {"root": ".", "pass": passes, "warnings": warnings, "human_decisions_required": decisions}


def render_markdown(result: dict[str, Any]) -> str:
    lines = ["# Agent docs check", "", "## Pass", ""]
    lines.extend([f"- {item}" for item in result["pass"]] or ["- none"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {item}" for item in result["warnings"]] or ["- none"])
    lines.extend(["", "## Human decisions required", ""])
    lines.extend([f"- {item}" for item in result["human_decisions_required"]] or ["- none"])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    emit_markdown = args.markdown or not args.json
    result = check(Path(args.root), include_hidden=args.include_hidden)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    if emit_markdown:
        if args.json:
            print()
        print(render_markdown(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

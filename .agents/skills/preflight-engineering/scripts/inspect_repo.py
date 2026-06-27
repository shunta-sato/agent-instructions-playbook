#!/usr/bin/env python3
"""Collect read-only repository preflight facts for preflight-engineering."""

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
HIDDEN_ALLOWLIST = {".agent", ".agents", ".github"}
SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}
PACKAGE_FILES = {
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "poetry.lock",
    "uv.lock",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "bun.lockb",
    "Cargo.toml",
    "Cargo.lock",
    "go.mod",
    "go.sum",
    "Gemfile",
    "Gemfile.lock",
    "composer.json",
    "composer.lock",
    "pom.xml",
}
LOCKFILES = {
    "poetry.lock",
    "uv.lock",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "bun.lockb",
    "Cargo.lock",
    "go.sum",
    "Gemfile.lock",
    "composer.lock",
}
COMMAND_FILES = {"COMMANDS.md", "Makefile", "makefile", "justfile", "Justfile", "Taskfile.yml"}
TEST_CONFIG_NAMES = {
    "pytest.ini",
    "tox.ini",
    "jest.config.js",
    "jest.config.ts",
    "vitest.config.ts",
    "playwright.config.ts",
    "cypress.config.ts",
}
COMMAND_PREFIXES = (
    "make ",
    "python ",
    "python3 ",
    "pytest",
    "npm ",
    "pnpm ",
    "yarn ",
    "bun ",
    "cargo ",
    "go ",
    "mvn ",
    "gradle ",
    "./",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read-only preflight repository inspection collector."
    )
    parser.add_argument("--root", default=".", help="Repository root to inspect.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--markdown", action="store_true", help="Emit Markdown output.")
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden paths beyond .agent/.agents/.github.",
    )
    parser.add_argument("--max-depth", type=int, default=5, help="Maximum walk depth.")
    return parser.parse_args()


def rel_path(path: Path, root: Path) -> str:
    if path == root:
        return "."
    return path.relative_to(root).as_posix()


def is_hidden(path: Path, root: Path) -> bool:
    if path == root:
        return False
    return any(part.startswith(".") for part in path.relative_to(root).parts)


def hidden_allowed(path: Path, root: Path) -> bool:
    if path == root:
        return True
    parts = path.relative_to(root).parts
    return bool(parts) and parts[0] in HIDDEN_ALLOWLIST


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


def should_skip_hidden(path: Path, root: Path, include_hidden: bool) -> bool:
    return is_hidden(path, root) and not include_hidden and not hidden_allowed(path, root)


def safe_read_text(path: Path, root: Path, include_hidden: bool) -> str | None:
    if is_secret_like(path) or should_skip_hidden(path, root, include_hidden):
        return None
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def walk_paths(root: Path, include_hidden: bool, max_depth: int) -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    secret_like: set[str] = set()

    for current, dirnames, filenames in os.walk(root):
        current_path = Path(current)
        rel_parts = () if current_path == root else current_path.relative_to(root).parts
        if len(rel_parts) >= max_depth:
            dirnames[:] = []

        kept_dirs: list[str] = []
        for dirname in sorted(dirnames):
            dirpath = current_path / dirname
            if dirname in SKIP_DIRS:
                continue
            if is_secret_like(dirpath):
                secret_like.add(rel_path(dirpath, root))
                continue
            if should_skip_hidden(dirpath, root, include_hidden):
                continue
            kept_dirs.append(dirname)
        dirnames[:] = kept_dirs

        for filename in sorted(filenames):
            path = current_path / filename
            if is_secret_like(path):
                secret_like.add(rel_path(path, root))
                continue
            if should_skip_hidden(path, root, include_hidden):
                continue
            files.append(path)

    return files, sorted(secret_like)


def add_path(bucket: list[str], path: Path, root: Path) -> None:
    value = rel_path(path, root)
    if value not in bucket:
        bucket.append(value)


def collect_make_targets(path: Path, root: Path, include_hidden: bool) -> list[str]:
    text = safe_read_text(path, root, include_hidden)
    if text is None:
        return []
    targets: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^([A-Za-z0-9_.-]+):(?:\s|$)", line)
        if match and not match.group(1).startswith("."):
            targets.append(f"make {match.group(1)}")
    return targets


def collect_commands_md(path: Path, root: Path, include_hidden: bool) -> list[str]:
    text = safe_read_text(path, root, include_hidden)
    if text is None:
        return []
    commands: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("- ") and ":" in line:
            command = line.split(":", maxsplit=1)[1].strip()
            if command and command != "<fill>" and command.startswith(COMMAND_PREFIXES):
                commands.append(command)
    return commands


def collect_package_scripts(path: Path, root: Path, include_hidden: bool) -> list[str]:
    if path.name != "package.json":
        return []
    text = safe_read_text(path, root, include_hidden)
    if text is None:
        return []
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return []
    scripts = payload.get("scripts")
    if not isinstance(scripts, dict):
        return []
    return [f"npm run {name}" for name in sorted(scripts) if isinstance(name, str)]


def risk_key_for(path: Path) -> str | None:
    lowered = path.as_posix().lower()
    checks = (
        ("billing", ("billing", "payment", "stripe", "invoice", "subscription")),
        ("auth", ("auth", "oauth", "session", "jwt", "cookie", "csrf", "login")),
        ("api", ("openapi", "swagger", "graphql", "proto", "api", "client")),
        ("db", ("migration", "migrations", "schema", "prisma", "alembic", "orm", "db")),
        ("security", ("security", "secret", "credential", "token", "csrf", "ssrf")),
        ("infra", ("infra", "deploy", "terraform", "helm", "k8s", "docker", "workflow")),
    )
    for key, needles in checks:
        if any(needle in lowered for needle in needles):
            return key
    return None


def infer_package_managers(paths: list[Path]) -> list[str]:
    names = {path.name for path in paths}
    inferred: list[str] = []
    if {"pnpm-lock.yaml", "package.json"} <= names:
        inferred.append("package manager candidate: pnpm")
    elif {"yarn.lock", "package.json"} <= names:
        inferred.append("package manager candidate: yarn")
    elif {"package-lock.json", "package.json"} <= names:
        inferred.append("package manager candidate: npm")
    elif "package.json" in names:
        inferred.append("package manager candidate: npm-compatible")
    if "uv.lock" in names or "pyproject.toml" in names:
        inferred.append("Python project candidate: pyproject/uv")
    if "poetry.lock" in names:
        inferred.append("Python project candidate: Poetry")
    if "go.mod" in names:
        inferred.append("Go project candidate")
    if "Cargo.toml" in names:
        inferred.append("Rust project candidate")
    return inferred


def inspect(root: Path, include_hidden: bool, max_depth: int) -> dict[str, Any]:
    root = root.resolve()
    files, secret_like_paths = walk_paths(root, include_hidden, max_depth)
    result: dict[str, Any] = {
        "root": ".",
        "instruction_files": [],
        "agent_context": [],
        "skills": [],
        "docs": [],
        "package_manager_files": [],
        "lockfiles": [],
        "tooling_files": [],
        "test_config": [],
        "commands": {"confirmed": [], "inferred": [], "unknown": []},
        "risk_surfaces": {
            "auth": [],
            "api": [],
            "db": [],
            "security": [],
            "infra": [],
            "billing": [],
        },
        "generated_paths": [],
        "migration_paths": [],
        "secret_like_paths": secret_like_paths,
        "human_decisions_required": [],
    }

    for path in files:
        relative = rel_path(path, root)
        parts = path.relative_to(root).parts
        name = path.name
        lowered = relative.lower()

        if name == "AGENTS.md":
            add_path(result["instruction_files"], path, root)
        if parts and parts[0] == ".agent":
            add_path(result["agent_context"], path, root)
        if len(parts) >= 4 and parts[0:3] == (".agents", "skills", parts[2]) and name == "SKILL.md":
            add_path(result["skills"], path, root)
        if name.startswith("README") or name.startswith("CONTRIBUTING") or (parts and parts[0] == "docs"):
            add_path(result["docs"], path, root)
        if name in PACKAGE_FILES:
            add_path(result["package_manager_files"], path, root)
        if name in LOCKFILES:
            add_path(result["lockfiles"], path, root)
        if name in COMMAND_FILES:
            add_path(result["tooling_files"], path, root)
        if name in TEST_CONFIG_NAMES or "test" in lowered and name.endswith((".toml", ".ini", ".yml", ".yaml", ".json")):
            add_path(result["test_config"], path, root)
        if "generated" in lowered or "__generated__" in lowered or "/gen/" in lowered:
            add_path(result["generated_paths"], path, root)
        if "migration" in lowered or "migrations" in lowered or "alembic/versions" in lowered:
            add_path(result["migration_paths"], path, root)

        risk_key = risk_key_for(path)
        if risk_key is not None:
            add_path(result["risk_surfaces"][risk_key], path, root)

        if name == "COMMANDS.md":
            result["commands"]["confirmed"].extend(collect_commands_md(path, root, include_hidden))
        if name in {"Makefile", "makefile"}:
            result["commands"]["confirmed"].extend(collect_make_targets(path, root, include_hidden))
        if name == "package.json":
            result["commands"]["confirmed"].extend(collect_package_scripts(path, root, include_hidden))

    result["commands"]["confirmed"] = sorted(set(result["commands"]["confirmed"]))
    result["commands"]["inferred"] = infer_package_managers(files)

    root_agents = root / "AGENTS.md"
    if "AGENTS.md" not in result["instruction_files"]:
        result["commands"]["unknown"].append("root AGENTS.md is missing")
        result["human_decisions_required"].append("Decide root AGENTS.md placement and scope.")
    if not result["agent_context"]:
        result["commands"]["unknown"].append(".agent context maps were not found")
    if not result["test_config"] and not any("test" in cmd for cmd in result["commands"]["confirmed"]):
        result["commands"]["unknown"].append("targeted test routing is unknown")
        result["human_decisions_required"].append("Confirm canonical targeted test commands.")
    if not root_agents.exists():
        result["human_decisions_required"].append("Create or confirm root AGENTS.md before long-running work.")

    for key in result["risk_surfaces"]:
        result["risk_surfaces"][key] = sorted(result["risk_surfaces"][key])
    for key in (
        "instruction_files",
        "agent_context",
        "skills",
        "docs",
        "package_manager_files",
        "lockfiles",
        "tooling_files",
        "test_config",
        "generated_paths",
        "migration_paths",
        "human_decisions_required",
    ):
        result[key] = sorted(set(result[key]))

    return result


def render_markdown(result: dict[str, Any]) -> str:
    lines = ["# Repo inspection result", "", f"- Root: `{result['root']}`", ""]
    sections = (
        ("Instruction files", "instruction_files"),
        ("Agent context", "agent_context"),
        ("Skills", "skills"),
        ("Docs", "docs"),
        ("Package manager files", "package_manager_files"),
        ("Lockfiles", "lockfiles"),
        ("Tooling files", "tooling_files"),
        ("Test config", "test_config"),
        ("Generated paths", "generated_paths"),
        ("Migration paths", "migration_paths"),
        ("Secret-like paths (path only, contents not read)", "secret_like_paths"),
    )
    for title, key in sections:
        lines.extend([f"## {title}", ""])
        values = result.get(key, [])
        lines.extend([f"- `{value}`" for value in values] or ["- unknown"])
        lines.append("")

    lines.extend(["## Commands", ""])
    for fact_kind in ("confirmed", "inferred", "unknown"):
        lines.append(f"### {fact_kind}")
        values = result["commands"][fact_kind]
        lines.extend([f"- `{value}`" for value in values] or ["- none"])
        lines.append("")

    lines.extend(["## Risk surfaces", ""])
    for key, values in result["risk_surfaces"].items():
        lines.append(f"### {key}")
        lines.extend([f"- `{value}`" for value in values] or ["- none found"])
        lines.append("")

    lines.extend(["## Human decisions required", ""])
    lines.extend([f"- {value}" for value in result["human_decisions_required"]] or ["- none"])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    emit_json = args.json or not args.markdown
    result = inspect(
        root=Path(args.root),
        include_hidden=args.include_hidden,
        max_depth=args.max_depth,
    )
    if emit_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    if args.markdown:
        if emit_json:
            print()
        print(render_markdown(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

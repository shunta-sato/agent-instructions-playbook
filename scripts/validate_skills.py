#!/usr/bin/env python3
"""Validate repository-local Agent Skills metadata and layout."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
TOP_LEVEL_FIELD_RE = re.compile(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$")
ALLOWED_TOP_LEVEL_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}


@dataclass(frozen=True)
class SkillDoc:
    path: Path
    body: str
    fields: dict[str, str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate .agents/skills SKILL.md files against Agent Skills constraints."
    )
    parser.add_argument(
        "--repo-root",
        default="",
        help="Repository root (default: inferred from this script location).",
    )
    parser.add_argument(
        "--skills-dir",
        default=".agents/skills",
        help="Skills directory relative to repo root.",
    )
    return parser.parse_args()


def repo_root_from_args(explicit_root: str) -> Path:
    if explicit_root:
        return Path(explicit_root).resolve()
    return Path(__file__).resolve().parent.parent


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1].strip()
    return value


def parse_skill_doc(path: Path) -> SkillDoc:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter opening marker")

    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ValueError("missing YAML frontmatter closing marker")

    frontmatter = parts[1]
    body = parts[2].strip()
    fields: dict[str, str] = {}

    for line_no, raw_line in enumerate(frontmatter.splitlines(), start=2):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line[0].isspace():
            continue

        match = TOP_LEVEL_FIELD_RE.match(raw_line)
        if not match:
            raise ValueError(f"invalid top-level frontmatter line {line_no}: {raw_line}")

        key = match.group(1)
        value = strip_quotes(match.group(2) or "")
        if key in fields:
            raise ValueError(f"duplicate frontmatter field: {key}")
        fields[key] = value

    return SkillDoc(path=path, body=body, fields=fields)


def validate_skill(doc: SkillDoc, repo_root: Path) -> list[str]:
    errors: list[str] = []
    relpath = doc.path.relative_to(repo_root).as_posix()
    dirname = doc.path.parent.name

    unknown_fields = sorted(set(doc.fields) - ALLOWED_TOP_LEVEL_FIELDS)
    if unknown_fields:
        errors.append(f"{relpath}: unknown frontmatter fields: {', '.join(unknown_fields)}")

    name = doc.fields.get("name", "")
    if not name:
        errors.append(f"{relpath}: missing required field: name")
    elif not NAME_RE.match(name) or "--" in name:
        errors.append(
            f"{relpath}: invalid name '{name}' "
            "(use lowercase letters, numbers, single hyphens, max 64 chars)"
        )
    elif name != dirname:
        errors.append(f"{relpath}: name '{name}' must match parent directory '{dirname}'")

    description = doc.fields.get("description", "")
    if not description:
        errors.append(f"{relpath}: missing required field: description")
    elif len(description) > 1024:
        errors.append(f"{relpath}: description is {len(description)} chars; max is 1024")

    compatibility = doc.fields.get("compatibility")
    if compatibility is not None and (not compatibility or len(compatibility) > 500):
        errors.append(f"{relpath}: compatibility must be 1-500 chars when present")

    license_value = doc.fields.get("license")
    if license_value is not None and not license_value:
        errors.append(f"{relpath}: license must be non-empty when present")

    if not doc.body:
        errors.append(f"{relpath}: SKILL.md body must be non-empty")

    line_count = len(doc.path.read_text(encoding="utf-8").splitlines())
    if line_count > 500:
        errors.append(f"{relpath}: SKILL.md has {line_count} lines; keep under 500")

    return errors


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_args(args.repo_root)
    skills_dir = repo_root / args.skills_dir
    github_skills_dir = repo_root / ".github" / "skills"
    errors: list[str] = []

    if not skills_dir.is_dir():
        errors.append(f"{skills_dir.relative_to(repo_root).as_posix()}: directory is missing")
    if github_skills_dir.exists():
        errors.append(
            ".github/skills: remove the duplicate mirror; "
            ".agents/skills is the single repo skill source"
        )

    docs: list[SkillDoc] = []
    if skills_dir.is_dir():
        for path in sorted(skills_dir.glob("*/SKILL.md")):
            try:
                docs.append(parse_skill_doc(path))
            except ValueError as exc:
                errors.append(f"{path.relative_to(repo_root).as_posix()}: {exc}")

        names: dict[str, Path] = {}
        for doc in docs:
            name = doc.fields.get("name", "")
            if name and name in names:
                errors.append(
                    f"{doc.path.relative_to(repo_root).as_posix()}: duplicate skill name "
                    f"also used by {names[name].relative_to(repo_root).as_posix()}"
                )
            elif name:
                names[name] = doc.path

        for doc in docs:
            errors.extend(validate_skill(doc, repo_root=repo_root))

    if errors:
        print("Skill validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print(f"Validated {len(docs)} skills under {skills_dir.relative_to(repo_root).as_posix()}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

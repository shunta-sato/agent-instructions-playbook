#!/usr/bin/env python3
"""Validate repository-local Agent Skills metadata and layout."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from skill_description_style import (
    DESCRIPTION_RECOMMENDED_MAX_CHARS,
    description_trigger_only_flags,
)


NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
TOP_LEVEL_FIELD_RE = re.compile(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$")
OUTPUT_EXPECTATION_RE = re.compile(r"^## Output expectation$", re.MULTILINE)
ALLOWED_TOP_LEVEL_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
# Must stay in sync by hand with TIER_FIELDS in update_skill_requires.py and
# the visibility handling in generate_agent_index.py — no shared constant
# exists across these three scripts.
ALLOWED_METADATA_FIELDS = {
    "short-description",
    "requires",
    "resources",
    "commands",
    "templates",
    "visibility",
}
ALLOWED_VISIBILITY_VALUES = {"default", "explicit-only", "template"}


@dataclass(frozen=True)
class SkillDoc:
    path: Path
    body: str
    fields: dict[str, str]
    metadata_fields: dict[str, str]


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


def parse_metadata_fields(frontmatter: str) -> dict[str, str]:
    """Return keys nested directly under `metadata:`, mapped to their inline
    scalar value (empty string for keys that introduce a nested list block,
    e.g. `requires:`)."""
    fields: dict[str, str] = {}
    in_metadata = False
    for raw_line in frontmatter.splitlines():
        if raw_line.rstrip() == "metadata:":
            in_metadata = True
            continue
        if not in_metadata:
            continue
        if raw_line.startswith("  ") and not raw_line.startswith("    "):
            stripped = raw_line.strip()
            key, _, value = stripped.partition(":")
            fields[key.strip()] = strip_quotes(value)
        elif raw_line.strip() == "" or raw_line.startswith("    "):
            continue
        else:
            in_metadata = False
    return fields


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

    metadata_fields = parse_metadata_fields(frontmatter) if "metadata" in fields else {}
    return SkillDoc(path=path, body=body, fields=fields, metadata_fields=metadata_fields)


def validate_skill(doc: SkillDoc, repo_root: Path) -> list[str]:
    errors: list[str] = []
    relpath = doc.path.relative_to(repo_root).as_posix()
    dirname = doc.path.parent.name

    unknown_fields = sorted(set(doc.fields) - ALLOWED_TOP_LEVEL_FIELDS)
    if unknown_fields:
        errors.append(f"{relpath}: unknown frontmatter fields: {', '.join(unknown_fields)}")

    unknown_metadata_fields = sorted(set(doc.metadata_fields) - ALLOWED_METADATA_FIELDS)
    if unknown_metadata_fields:
        errors.append(
            f"{relpath}: unknown metadata fields: {', '.join(unknown_metadata_fields)}"
        )

    visibility = doc.metadata_fields.get("visibility")
    if visibility is not None and visibility not in ALLOWED_VISIBILITY_VALUES:
        errors.append(
            f"{relpath}: invalid metadata.visibility '{visibility}' "
            f"(must be one of {', '.join(sorted(ALLOWED_VISIBILITY_VALUES))})"
        )

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
    elif not OUTPUT_EXPECTATION_RE.search(doc.body):
        errors.append(f"{relpath}: SKILL.md body must contain a '## Output expectation' heading")

    line_count = len(doc.path.read_text(encoding="utf-8").splitlines())
    if line_count > 500:
        errors.append(f"{relpath}: SKILL.md has {line_count} lines; keep under 500")

    return errors


def description_style_warnings(doc: SkillDoc, repo_root: Path) -> list[str]:
    warnings: list[str] = []
    relpath = doc.path.relative_to(repo_root).as_posix()
    description = doc.fields.get("description", "")
    for flag in description_trigger_only_flags(description):
        if flag.startswith("long-description:"):
            length = flag.split(":", maxsplit=1)[1]
            warnings.append(
                f"{relpath}: description style: {length} chars; "
                f"recommended max is {DESCRIPTION_RECOMMENDED_MAX_CHARS}"
            )
        else:
            warnings.append(f"{relpath}: description style: {flag}")

    return warnings


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_args(args.repo_root)
    skills_dir = repo_root / args.skills_dir
    github_skills_dir = repo_root / ".github" / "skills"
    errors: list[str] = []
    warnings: list[str] = []

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
            warnings.extend(description_style_warnings(doc, repo_root=repo_root))

    if errors:
        print("Skill validation failed:")
        for err in errors:
            print(f"- {err}")
        if warnings:
            print("")
            print("Skill validation warnings:")
            for warning in warnings:
                print(f"- {warning}")
        return 1

    print(f"Validated {len(docs)} skills under {skills_dir.relative_to(repo_root).as_posix()}.")
    if warnings:
        print("Skill validation warnings:")
        for warning in warnings:
            print(f"- {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

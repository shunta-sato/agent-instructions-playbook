#!/usr/bin/env python3
"""Skill data collection for the skill inventory report: SKILL.md frontmatter
parsing, per-skill counts, broad-trigger risk-flag detection, and trigger-eval
coverage loading.

Split out of ``report_skill_inventory`` (400-line overflow, second cut). This
module holds the ``SkillInventory``/``EvalCoverage`` records and everything
that produces them; the CLI file keeps argument parsing, report assembly, and
rendering, and ``skill_inventory_checks`` holds the warning/ratchet/
quality-bar logic that consumes these records."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from scripts.skill_description_style import description_trigger_only_flags
    from scripts.skill_inventory_checks import parse_visibility, to_repo_relative
except ImportError:  # pragma: no cover - direct execution puts scripts/ on sys.path
    from skill_description_style import description_trigger_only_flags
    from skill_inventory_checks import parse_visibility, to_repo_relative


TOP_LEVEL_FIELD_RE = re.compile(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$")
BLOCK_SCALAR_VALUES = {"|", "|-", "|+", ">", ">-", ">+"}
BROAD_TRIGGER_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("mandatory", re.compile(r"\bMANDATORY\b")),
    (
        "always-use",
        re.compile(r"\balways\s+(?:use|trigger|invoke)\b", re.IGNORECASE),
    ),
    (
        "whenever",
        re.compile(r"\bwhenever\b", re.IGNORECASE),
    ),
    (
        "any-code-change",
        re.compile(
            r"\bany\s+(?:code/test|code|test)\s+change\b",
            re.IGNORECASE,
        ),
    ),
    (
        "any-change",
        re.compile(r"\bany\s+change\b", re.IGNORECASE),
    ),
    (
        "any-work",
        re.compile(
            r"\bany\s+(?:task|request|work|implementation|feature|diff)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "all-work",
        re.compile(
            r"\b(?:all|every)\s+"
            r"(?:task|request|work|change|implementation|feature|diff)s?\b",
            re.IGNORECASE,
        ),
    ),
    (
        "task-mentions",
        re.compile(r"\btask\s+mentions\b", re.IGNORECASE),
    ),
)
COUNTED_SUBDIRS = {
    "asset_count": "assets",
    "example_count": "examples",
    "reference_count": "references",
    "script_count": "scripts",
    "template_count": "templates",
}


@dataclass(frozen=True)
class SkillInventory:
    path: Path
    directory: str
    name: str
    description: str
    description_length: int
    line_count: int
    reference_count: int
    template_count: int
    script_count: int
    asset_count: int
    example_count: int
    eval_coverage_count: int
    eval_should_trigger_count: int
    eval_should_not_trigger_count: int
    description_trigger_only_flags: list[str]
    broad_trigger_risk_flags: list[str]
    visibility: str


@dataclass(frozen=True)
class EvalCoverage:
    should_trigger: dict[str, int]
    should_not_trigger: dict[str, int]
    eval_files: list[Path]
    unknown_references: list[str]
    errors: list[str]



def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1].strip()
    return value


def normalize_block_scalar(style: str, lines: list[str]) -> str:
    nonblank_indents = [
        len(line) - len(line.lstrip(" "))
        for line in lines
        if line.strip()
    ]
    indent = min(nonblank_indents) if nonblank_indents else 0
    normalized = [
        line[indent:] if len(line) >= indent else ""
        for line in lines
    ]

    if style.startswith(">"):
        return " ".join(line.strip() for line in normalized if line.strip())
    return "\n".join(normalized).strip()


def parse_frontmatter_fields(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}

    parts = text.split("---", 2)
    if len(parts) != 3:
        return {}

    lines = parts[1].splitlines()
    fields: dict[str, str] = {}
    line_index = 0
    while line_index < len(lines):
        raw_line = lines[line_index]
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            line_index += 1
            continue
        if raw_line[0].isspace():
            line_index += 1
            continue

        match = TOP_LEVEL_FIELD_RE.match(raw_line)
        if not match:
            line_index += 1
            continue

        key = match.group(1)
        value = strip_quotes(match.group(2) or "")
        if value in BLOCK_SCALAR_VALUES:
            block_lines: list[str] = []
            line_index += 1
            while line_index < len(lines):
                next_line = lines[line_index]
                if (
                    next_line
                    and not next_line[0].isspace()
                    and TOP_LEVEL_FIELD_RE.match(next_line)
                ):
                    break
                block_lines.append(next_line)
                line_index += 1
            fields[key] = normalize_block_scalar(value, block_lines)
            continue

        fields[key] = value
        line_index += 1

    return fields


def count_files(path: Path) -> int:
    if not path.is_dir():
        return 0
    return sum(1 for child in sorted(path.rglob("*")) if child.is_file())


def broad_trigger_flags(text: str) -> list[str]:
    flags: list[str] = []
    seen: set[str] = set()

    for line_no, line in enumerate(text.splitlines(), start=1):
        for label, pattern in BROAD_TRIGGER_PATTERNS:
            if pattern.search(line):
                flag = f"{label}:line {line_no}"
                if flag not in seen:
                    seen.add(flag)
                    flags.append(flag)

    return flags


def load_skill_inventories(
    repo_root: Path,
    skills_dir: Path,
) -> tuple[list[SkillInventory], dict[str, int], list[str]]:
    errors: list[str] = []
    docs: list[SkillInventory] = []
    name_counts: dict[str, int] = {}

    if not skills_dir.is_dir():
        rel_dir = skills_dir.relative_to(repo_root).as_posix()
        return [], name_counts, [f"{rel_dir}: directory is missing"]

    skill_paths = sorted(skills_dir.glob("*/SKILL.md"))
    if not skill_paths:
        rel_dir = skills_dir.relative_to(repo_root).as_posix()
        return [], name_counts, [f"{rel_dir}: no skills found"]

    for path in skill_paths:
        text = path.read_text(encoding="utf-8")
        fields = parse_frontmatter_fields(path)
        name = fields.get("name") or path.parent.name
        description = fields.get("description", "")
        name_counts[name] = name_counts.get(name, 0) + 1

        counts = {
            output_name: count_files(path.parent / subdir)
            for output_name, subdir in COUNTED_SUBDIRS.items()
        }

        docs.append(
            SkillInventory(
                path=path,
                directory=path.parent.name,
                name=name,
                description=description,
                description_length=len(description),
                line_count=len(text.splitlines()),
                reference_count=counts["reference_count"],
                template_count=counts["template_count"],
                script_count=counts["script_count"],
                asset_count=counts["asset_count"],
                example_count=counts["example_count"],
                eval_coverage_count=0,
                eval_should_trigger_count=0,
                eval_should_not_trigger_count=0,
                description_trigger_only_flags=description_trigger_only_flags(description),
                broad_trigger_risk_flags=broad_trigger_flags(text),
                visibility=parse_visibility(text),
            )
        )

    duplicate_names = sorted(name for name, count in name_counts.items() if count > 1)
    for name in duplicate_names:
        paths = [
            to_repo_relative(repo_root, doc.path)
            for doc in docs
            if doc.name == name
        ]
        errors.append(f"duplicate skill name '{name}': {', '.join(paths)}")

    for doc in docs:
        relpath = to_repo_relative(repo_root, doc.path)
        if doc.line_count > 500:
            errors.append(f"{relpath}: SKILL.md has {doc.line_count} lines; max is 500")
        if doc.description_length > 1024:
            errors.append(
                f"{relpath}: description is {doc.description_length} chars; max is 1024"
            )

    return docs, name_counts, errors


def read_name_list(
    case: dict[str, Any],
    key: str,
    context: str,
    errors: list[str],
) -> list[str]:
    value = case.get(key, [])
    if not isinstance(value, list):
        errors.append(f"{context}: {key} must be a list of skill names")
        return []

    names: list[str] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, str):
            errors.append(f"{context}: {key}[{index}] must be a skill name string")
            continue
        names.append(item)
    return names


def load_eval_coverage(
    repo_root: Path,
    eval_dir: Path,
    known_skill_names: set[str],
) -> EvalCoverage:
    should_trigger = {name: 0 for name in sorted(known_skill_names)}
    should_not_trigger = {name: 0 for name in sorted(known_skill_names)}
    unknown_references: list[str] = []
    errors: list[str] = []

    if not eval_dir.is_dir():
        rel_dir = eval_dir.relative_to(repo_root).as_posix()
        return EvalCoverage(
            should_trigger=should_trigger,
            should_not_trigger=should_not_trigger,
            eval_files=[],
            unknown_references=[],
            errors=[f"{rel_dir}: directory is missing"],
        )

    eval_files = sorted(eval_dir.glob("*.json"))
    for path in eval_files:
        relpath = to_repo_relative(repo_root, path)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{relpath}: invalid JSON: {exc}")
            continue

        if not isinstance(payload, dict):
            errors.append(f"{relpath}: top-level value must be an object")
            continue

        cases = payload.get("cases", [])
        if not isinstance(cases, list):
            errors.append(f"{relpath}: cases must be a list")
            continue

        for index, case in enumerate(cases, start=1):
            context = f"{relpath}:{index}"
            if not isinstance(case, dict):
                errors.append(f"{context}: case must be an object")
                continue

            for key, bucket in (
                ("should_trigger", should_trigger),
                ("should_not_trigger", should_not_trigger),
            ):
                for name in read_name_list(case, key, context, errors):
                    if name not in known_skill_names:
                        unknown_references.append(f"{context}: {key}: {name}")
                        continue
                    bucket[name] += 1

    for reference in sorted(set(unknown_references)):
        errors.append(f"unknown eval skill reference: {reference}")

    return EvalCoverage(
        should_trigger=should_trigger,
        should_not_trigger=should_not_trigger,
        eval_files=eval_files,
        unknown_references=sorted(set(unknown_references)),
        errors=errors,
    )


def apply_eval_coverage(
    skills: list[SkillInventory],
    coverage: EvalCoverage,
) -> list[SkillInventory]:
    updated: list[SkillInventory] = []
    for skill in skills:
        positive = coverage.should_trigger.get(skill.name, 0)
        negative = coverage.should_not_trigger.get(skill.name, 0)
        updated.append(
            SkillInventory(
                path=skill.path,
                directory=skill.directory,
                name=skill.name,
                description=skill.description,
                description_length=skill.description_length,
                line_count=skill.line_count,
                reference_count=skill.reference_count,
                template_count=skill.template_count,
                script_count=skill.script_count,
                asset_count=skill.asset_count,
                example_count=skill.example_count,
                eval_coverage_count=positive + negative,
                eval_should_trigger_count=positive,
                eval_should_not_trigger_count=negative,
                description_trigger_only_flags=skill.description_trigger_only_flags,
                broad_trigger_risk_flags=skill.broad_trigger_risk_flags,
                visibility=skill.visibility,
            )
        )
    return updated

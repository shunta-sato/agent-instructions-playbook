#!/usr/bin/env python3
"""Report deterministic inventory and trigger-risk data for local Agent Skills."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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
    broad_trigger_risk_flags: list[str]


@dataclass(frozen=True)
class EvalCoverage:
    should_trigger: dict[str, int]
    should_not_trigger: dict[str, int]
    eval_files: list[Path]
    unknown_references: list[str]
    errors: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Report .agents/skills inventory, trigger eval coverage, and "
            "broad-trigger risk flags."
        )
    )
    parser.add_argument(
        "--repo-root",
        default="",
        help="Repository root to scan (default: inferred from this script location).",
    )
    parser.add_argument(
        "--skills-dir",
        default=".agents/skills",
        help="Skills directory relative to repo root.",
    )
    parser.add_argument(
        "--eval-dir",
        default="evals/skill-triggers",
        help="Skill trigger eval directory relative to repo root.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output (ignored in text mode).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero on CI-relevant inventory errors.",
    )
    return parser.parse_args()


def repo_root_from_args(explicit_root: str) -> Path:
    if explicit_root:
        return Path(explicit_root).resolve()
    return Path(__file__).resolve().parent.parent


def to_repo_relative(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root).as_posix()


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
                broad_trigger_risk_flags=broad_trigger_flags(text),
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
                broad_trigger_risk_flags=skill.broad_trigger_risk_flags,
            )
        )
    return updated


def build_warnings(repo_root: Path, skills: list[SkillInventory]) -> list[str]:
    warnings: list[str] = []
    for skill in skills:
        relpath = to_repo_relative(repo_root, skill.path)
        if skill.eval_coverage_count == 0:
            warnings.append(f"{relpath}: no trigger eval coverage")
        if skill.broad_trigger_risk_flags:
            flags = ", ".join(skill.broad_trigger_risk_flags)
            warnings.append(f"{relpath}: broad trigger risk flags: {flags}")
    return warnings


def skill_to_json(repo_root: Path, skill: SkillInventory) -> dict[str, object]:
    return {
        "name": skill.name,
        "directory": skill.directory,
        "path": to_repo_relative(repo_root, skill.path),
        "description_length": skill.description_length,
        "skill_md_line_count": skill.line_count,
        "reference_count": skill.reference_count,
        "template_count": skill.template_count,
        "script_count": skill.script_count,
        "asset_count": skill.asset_count,
        "example_count": skill.example_count,
        "eval_coverage_count": skill.eval_coverage_count,
        "eval_should_trigger_count": skill.eval_should_trigger_count,
        "eval_should_not_trigger_count": skill.eval_should_not_trigger_count,
        "broad_trigger_risk_flags": skill.broad_trigger_risk_flags,
    }


def build_report(repo_root: Path, skills_dir_name: str, eval_dir_name: str) -> dict[str, object]:
    skills_dir = repo_root / skills_dir_name
    eval_dir = repo_root / eval_dir_name

    skills, _name_counts, skill_errors = load_skill_inventories(repo_root, skills_dir)
    known_skill_names = {skill.name for skill in skills}
    coverage = load_eval_coverage(repo_root, eval_dir, known_skill_names)
    skills = apply_eval_coverage(skills, coverage)

    errors = skill_errors + coverage.errors
    warnings = build_warnings(repo_root, skills)

    return {
        "schema_version": 1,
        "repo_root": str(repo_root),
        "skills_dir": skills_dir_name,
        "eval_dir": eval_dir_name,
        "totals": {
            "skills": len(skills),
            "eval_files": len(coverage.eval_files),
            "eval_references": sum(
                skill.eval_coverage_count for skill in skills
            ),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "skills": [skill_to_json(repo_root, skill) for skill in skills],
        "errors": errors,
        "warnings": warnings,
    }


def render_text(report: dict[str, object]) -> str:
    totals = report["totals"]
    assert isinstance(totals, dict)
    skills = report["skills"]
    assert isinstance(skills, list)

    lines = [
        "Skill inventory report",
        f"repo_root: {report['repo_root']}",
        f"skills_dir: {report['skills_dir']}",
        f"eval_dir: {report['eval_dir']}",
        (
            "totals: "
            f"skills={totals['skills']} "
            f"eval_files={totals['eval_files']} "
            f"eval_references={totals['eval_references']} "
            f"errors={totals['errors']} "
            f"warnings={totals['warnings']}"
        ),
        "",
        (
            "name | desc_chars | lines | refs | templates | scripts | assets | "
            "examples | evals | risk_flags"
        ),
        "--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---",
    ]

    for item in skills:
        assert isinstance(item, dict)
        risk_flags = item["broad_trigger_risk_flags"]
        assert isinstance(risk_flags, list)
        lines.append(
            f"{item['name']} | "
            f"{item['description_length']} | "
            f"{item['skill_md_line_count']} | "
            f"{item['reference_count']} | "
            f"{item['template_count']} | "
            f"{item['script_count']} | "
            f"{item['asset_count']} | "
            f"{item['example_count']} | "
            f"{item['eval_coverage_count']} | "
            f"{', '.join(str(flag) for flag in risk_flags) if risk_flags else '-'}"
        )

    errors = report["errors"]
    assert isinstance(errors, list)
    if errors:
        lines.extend(["", "Errors:"])
        lines.extend(f"- {error}" for error in errors)

    warnings = report["warnings"]
    assert isinstance(warnings, list)
    if warnings:
        lines.extend(["", "Warnings:"])
        lines.extend(f"- {warning}" for warning in warnings)

    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_args(args.repo_root)
    report = build_report(repo_root, args.skills_dir, args.eval_dir)

    if args.format == "json":
        if args.pretty:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(report, ensure_ascii=False))
    else:
        print(render_text(report))

    errors = report["errors"]
    assert isinstance(errors, list)
    if args.check and errors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

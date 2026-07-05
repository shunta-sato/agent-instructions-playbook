#!/usr/bin/env python3
"""Validate critical function-design skill protocol concepts.

This validator intentionally checks concepts, not exact prose. Each concept has
one or more regex alternatives so wording can change while accidental removal of
required protocol elements is still caught.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Concept:
    label: str
    patterns: tuple[str, ...]


@dataclass(frozen=True)
class ProtocolTarget:
    name: str
    paths: tuple[str, ...]
    concepts: tuple[Concept, ...]


def concept(label: str, *patterns: str) -> Concept:
    return Concept(label=label, patterns=patterns)


FUNCTION_BOUNDARY = ProtocolTarget(
    name="function-boundary-governor",
    paths=(
        ".agents/skills/function-boundary-governor/SKILL.md",
        ".agents/skills/function-boundary-governor/references/function-boundary-governor.md",
    ),
    concepts=(
        concept("decision outcome: keep", r"\bkeep\b"),
        concept("decision outcome: rename", r"\brename\b"),
        concept("decision outcome: split", r"\bsplit\b"),
        concept("decision outcome: merge", r"\bmerge\b"),
        concept("decision outcome: replace", r"\breplace\b"),
        concept("decision outcome: inline", r"\binline\b"),
        concept("decision outcome: no-op", r"\bno[- ]op\b"),
        concept("rubric: concept clarity", r"concept clarity"),
        concept("rubric: single reason to change", r"single reason to change"),
        concept("rubric: invariant ownership", r"invariant ownership"),
        concept("rubric: call-site readability", r"call[- ]site readability"),
        concept(
            "rubric: side-effect profile",
            r"side[- ]effect profile",
            r"side[- ]effect control",
            r"side effects?",
        ),
        concept("rubric: error behavior", r"error behavior", r"error contract"),
        concept("rubric: abstraction cost", r"abstraction cost"),
        concept("rubric: duplication risk", r"duplication risk"),
        concept("rubric: future divergence likelihood", r"future divergence likelihood"),
        concept("rubric: boundary crossing risk", r"boundary crossing risk"),
        concept("rubric: test protection", r"test protection"),
        concept("reject: textual similarity only", r"textual(?:ly)? similar", r"similarity is textual only"),
        concept("reject: vague helper names", r"vague names?", r"common.+util.+helper"),
        concept(
            "reject: boolean flags/options",
            r"boolean flags?",
            r"flags?/options?",
            r"optional behavior switches",
            r"parameterization pressure",
        ),
        concept("reject: different error behavior", r"error behavior.+differ", r"error behavior differs"),
        concept("reject: different side effects", r"side effects?.+differ", r"side effects? differ"),
        concept(
            "reject: worse call-site readability",
            r"call sites? become harder to read",
            r"worse call[- ]site readability",
            r"call[- ]site clarity differ",
        ),
        concept("reject: insufficient tests", r"tests? (?:are )?insufficient", r"insufficient tests?"),
        concept("autonomy: AI-led", r"\bAI-led\b", r"autonomously"),
        concept("autonomy: decide and act", r"decide and act", r"decide .+ action"),
    ),
)


DESTRUCTIVE_REFACTOR = ProtocolTarget(
    name="destructive-refactor",
    paths=(".agents/skills/destructive-refactor/SKILL.md",),
    concepts=(
        concept("baseline", r"\bbaseline\b"),
        concept("target design", r"target design"),
        concept("break window", r"break window"),
        concept("call-site migration", r"call sites? (?:must )?migrate", r"migrated call sites?"),
        concept("convergence", r"\bconvergence\b", r"converging back to green"),
        concept("rollback", r"\brollback\b"),
        concept("ledger update", r"ledger update", r"ledger updates"),
        concept("temporary red state", r"temporary red state"),
        concept("obsolete function deletion", r"delete obsolete", r"obsolete wrappers?/functions?"),
        concept(
            "no unledgered compatibility shims",
            r"forbid compatibility shims unless staged migration",
            r"compatibility shims?.+ledger",
        ),
        concept("staged migration recorded", r"staged migration.+ledger", r"staged adapters?.+removal condition"),
        concept("autonomy: AI-led", r"\bAI-led\b", r"decision: `replaced \| no-op \| rollback`"),
    ),
)


QUALITY_GATE = ProtocolTarget(
    name="quality-gate",
    paths=(
        ".agents/skills/quality-gate/SKILL.md",
        ".agents/skills/quality-gate/references/quality-gate.md",
    ),
    concepts=(
        concept("function-boundary decision evidence", r"function-boundary(?:-governor)?.+decision"),
        concept("destructive-refactor convergence evidence", r"destructive-refactor.+convergence"),
        concept("ledger evidence", r"ledger .+present", r"ledger evidence", r"ledger entry"),
        concept("verification command evidence", r"verification commands?", r"validation commands", r"command status"),
        concept("rollback/no-op reasoning", r"no-op or rollback.+explicit reasoning", r"rollback.+reason"),
    ),
)


AGENTS_CORE = ProtocolTarget(
    name="AGENTS.md core routing",
    paths=("AGENTS.md",),
    concepts=(
        concept("smallest safe change default", r"smallest safe change"),
        concept(
            "function-design coherent-design exception",
            r"function-boundary-governor.+destructive-refactor.+smallest coherent final design",
            r"smallest coherent final design",
        ),
        concept("no broad cleanup", r"No broad cleanups", r"no large unrelated cleanup"),
    ),
)


AUTONOMY_TARGET_PATHS = (
    ".agents/skills/function-boundary-governor/SKILL.md",
    ".agents/skills/destructive-refactor/SKILL.md",
)
FORBIDDEN_AUTONOMY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "ask the user which refactor to apply",
        re.compile(r"ask\s+the\s+user\s+which\s+refactor\s+to\s+apply", re.I),
    ),
    (
        "wait for approval before choosing",
        re.compile(r"wait\s+for\s+approval\s+before\s+choosing", re.I),
    ),
    (
        "present candidates and stop",
        re.compile(r"present\s+candidates\s+and\s+stop", re.I),
    ),
    (
        "human must select",
        re.compile(r"human\s+must\s+select", re.I),
    ),
    (
        "ask human to select candidate",
        re.compile(r"ask\s+(?:the\s+)?human\s+to\s+select", re.I),
    ),
)


TARGETS = (
    FUNCTION_BOUNDARY,
    DESTRUCTIVE_REFACTOR,
    QUALITY_GATE,
    AGENTS_CORE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate function-design protocol concepts in repo skill docs."
    )
    parser.add_argument(
        "--repo-root",
        default="",
        help="Repository root (default: inferred from this script location).",
    )
    return parser.parse_args()


def repo_root_from_args(explicit_root: str) -> Path:
    if explicit_root:
        return Path(explicit_root).resolve()
    return Path(__file__).resolve().parent.parent


def read_target_text(repo_root: Path, target: ProtocolTarget, errors: list[str]) -> str:
    parts: list[str] = []
    for relpath in target.paths:
        path = repo_root / relpath
        if not path.is_file():
            errors.append(f"{target.name}: missing required file: {relpath}")
            continue
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def validate_concepts(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for target in TARGETS:
        text = read_target_text(repo_root, target, errors)
        if not text:
            continue
        for item in target.concepts:
            if not any(re.search(pattern, text, re.IGNORECASE | re.DOTALL) for pattern in item.patterns):
                errors.append(f"{target.name}: missing concept: {item.label}")
    return errors


def validate_autonomy(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for relpath in AUTONOMY_TARGET_PATHS:
        path = repo_root / relpath
        if not path.is_file():
            errors.append(f"autonomy: missing required file: {relpath}")
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in FORBIDDEN_AUTONOMY_PATTERNS:
            if pattern.search(text):
                errors.append(f"{relpath}: forbidden autonomy deferral phrase: {label}")
    return errors


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_args(args.repo_root)

    errors = validate_concepts(repo_root)
    errors.extend(validate_autonomy(repo_root))

    if errors:
        print("Function-design protocol validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    concept_count = sum(len(target.concepts) for target in TARGETS)
    print(
        "Validated function-design protocol concepts "
        f"({concept_count} concept checks, {len(FORBIDDEN_AUTONOMY_PATTERNS)} autonomy bans)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

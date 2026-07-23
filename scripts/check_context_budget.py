#!/usr/bin/env python3
"""Check the always-loaded agent context surface against mechanical budgets.

This is the mechanical half of WS-A (see
``plans/20260720-context-surface-reduction.md``): it enforces the budgets
that the four-tier load contract (``metadata.requires`` / ``resources`` /
``commands`` / ``templates``, see ``update_skill_requires.py``) exists to
make possible. It is state-based, like ``check_structure.py``: it inspects
what the tree currently looks like, not what a change proposed.

Rules:

- common-path-budget: AGENTS.md + dev-workflow SKILL.md + its `requires`
  files + quality-gate SKILL.md + its `requires` files, total lines, over
  BUDGET_COMMON. These two skills are mandatory in every delivery-mode task,
  so their reach is the floor every other task pays.
- requires-count: a skill's `metadata.requires` list over REQUIRES_MAX_ENTRIES
  entries. Hardens the warning `update_skill_requires.py` already emits into
  a hard error.
- skill-md-lines: a skill's SKILL.md over SKILL_MD_SOFT_MAX_LINES lines.
- reach-budget: a skill's SKILL.md lines + the sum of its `requires` files'
  lines, over REACH_BUDGET_LINES. Reuses `check_structure.py`'s source-file
  budget so there is one canonical "one unit of context" size in the repo.

Exit code 0 when clean, 1 when findings exist. Only Python stdlib is used.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

try:
    from scripts.check_structure import DEFAULT_MAX_SOURCE_LINES
    from scripts.update_skill_requires import parse_tier_lists, split_frontmatter
except ImportError:  # pragma: no cover - direct execution puts scripts/ on sys.path
    from check_structure import DEFAULT_MAX_SOURCE_LINES
    from update_skill_requires import parse_tier_lists, split_frontmatter

# Measured 559 after wave 2 (AGENTS.md + dev-workflow SKILL.md+ref +
# quality-gate SKILL.md+ref); the old triple-duplicated common path was
# ~611. 600 ratchets the budget below the pre-reduction size while leaving
# working margin. See plans/20260720-context-surface-reduction.md.
BUDGET_COMMON = 600
REQUIRES_MAX_ENTRIES = 2
SKILL_MD_SOFT_MAX_LINES = 150

# Fixed ceilings for skills that predate this gate and already exceeded the soft
# budget when it landed (WS-C owns trimming them). Each cap is the file's size at
# gate introduction: growth past that size is a finding (shrink-then-regrow up to
# the cap is not). Remove an entry once its skill fits SKILL_MD_SOFT_MAX_LINES.
# The reach-budget below bounds the UNCONDITIONAL load (SKILL.md + requires) only;
# worst-case load including matched resources is deliberately not bounded here —
# resources are conditional by contract and their weight is a WS-C trim target.
SKILL_MD_RATCHET_CAPS = {
    ".agents/skills/agent-workflow-contract-review/SKILL.md": 158,
    ".agents/skills/architecture-decision-analysis/SKILL.md": 152,
    ".agents/skills/embedded-system-familiarization/SKILL.md": 163,
    ".agents/skills/preflight-engineering/SKILL.md": 166,
}
REACH_BUDGET_LINES = DEFAULT_MAX_SOURCE_LINES  # 400: one canonical context-unit size

COMMON_PATH_SKILLS = ("dev-workflow", "quality-gate")
SKILLS_DIR = ".agents/skills"


@dataclass(frozen=True)
class Finding:
    rule: str
    location: str
    value: int
    limit: int
    action: str


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check the agent context surface against mechanical budgets."
    )
    parser.add_argument("--repo-root", default="", help="Repository root override.")
    return parser.parse_args(argv)


def repo_root_from_args(explicit_root: str) -> Path:
    if explicit_root:
        return Path(explicit_root).resolve()
    return Path.cwd()


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8", errors="replace").splitlines())


def skill_requires(skill_md: Path) -> list[str]:
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    frontmatter, _body = split_frontmatter(text, skill_md)
    return parse_tier_lists(frontmatter).get("requires", [])


def skill_reach_lines(skill_md: Path) -> int:
    total = line_count(skill_md)
    for rel in skill_requires(skill_md):
        req_path = skill_md.parent / rel
        if req_path.is_file():
            total += line_count(req_path)
    return total


def check_common_path(repo_root: Path) -> list[Finding]:
    paths = [repo_root / "AGENTS.md"]
    for name in COMMON_PATH_SKILLS:
        skill_md = repo_root / SKILLS_DIR / name / "SKILL.md"
        paths.append(skill_md)
        if skill_md.is_file():
            paths.extend(skill_md.parent / rel for rel in skill_requires(skill_md))

    total = sum(line_count(p) for p in paths if p.is_file())
    if total > BUDGET_COMMON:
        return [
            Finding(
                rule="common-path-budget",
                location="AGENTS.md + dev-workflow + quality-gate (+requires)",
                value=total,
                limit=BUDGET_COMMON,
                action=(
                    "single-source further or move content behind "
                    "resources/commands (see plans/20260720-context-surface-reduction.md)"
                ),
            )
        ]
    return []


def check_skill(skill_md: Path, repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        display = skill_md.relative_to(repo_root).as_posix()
    except ValueError:
        display = skill_md.as_posix()

    requires = skill_requires(skill_md)
    if len(requires) > REQUIRES_MAX_ENTRIES:
        findings.append(
            Finding(
                rule="requires-count",
                location=display,
                value=len(requires),
                limit=REQUIRES_MAX_ENTRIES,
                action="move files to resources/commands/templates or trim requires",
            )
        )

    skill_lines = line_count(skill_md)
    skill_cap = SKILL_MD_RATCHET_CAPS.get(display, SKILL_MD_SOFT_MAX_LINES)
    if skill_lines > skill_cap:
        findings.append(
            Finding(
                rule="skill-md-lines",
                location=display,
                value=skill_lines,
                limit=skill_cap,
                action="move detail into references/ and route via requires/resources",
            )
        )

    reach = skill_reach_lines(skill_md)
    if reach > REACH_BUDGET_LINES:
        findings.append(
            Finding(
                rule="reach-budget",
                location=display,
                value=reach,
                limit=REACH_BUDGET_LINES,
                action="shrink requires files, or move detail to resources (loaded conditionally, not always)",
            )
        )
    return findings


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = repo_root_from_args(args.repo_root)

    findings = list(check_common_path(repo_root))

    skills_dir = repo_root / SKILLS_DIR
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        findings.extend(check_skill(skill_md, repo_root))

    for finding in findings:
        print(
            f"FINDING {finding.rule} {finding.location}: "
            f"{finding.value} > {finding.limit} — {finding.action}"
        )
    if not findings:
        print("context-budget: pass")
    else:
        print(f"context-budget: {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

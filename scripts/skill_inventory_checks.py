#!/usr/bin/env python3
"""Warning-ID derivation, quality-bar minimums, visibility parsing, and
warning-baseline load/compare/write for the skill inventory report.

Split out of ``report_skill_inventory`` (400-line overflow). This module is
the check/ratchet logic that ``--check`` and ``--write-baseline`` drive;
``skill_inventory_collection`` holds SKILL.md data collection, and the CLI
file keeps argument parsing, report assembly, and rendering, importing these
symbols back (dual-path import pattern, see below)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TYPE_CHECKING

try:
    from scripts.update_skill_requires import ALLOWED_VISIBILITY_VALUES, DEFAULT_VISIBILITY
except ImportError:  # pragma: no cover - direct execution puts scripts/ on sys.path
    from update_skill_requires import ALLOWED_VISIBILITY_VALUES, DEFAULT_VISIBILITY

if TYPE_CHECKING:  # pragma: no cover - avoids a runtime cycle with skill_inventory_collection
    from scripts.skill_inventory_collection import SkillInventory


METADATA_BLOCK_RE = re.compile(r"^metadata:[ \t]*\n((?:[ \t]+.*(?:\n|$))*)", re.MULTILINE)
VISIBILITY_RE = re.compile(r"^[ \t]*visibility:[ \t]*(\S+)[ \t]*$", re.MULTILINE)
DEFAULT_BASELINE_RELPATH = "scripts/skill_inventory_baseline.json"
# Quality-bar minimums by `metadata.visibility`: (min positive, min negative)
# trigger-eval cases. Visibility classes absent from this map (`template`)
# are exempt. Mirrors README.md's "Skill Quality Bar" / Skill Delta Gate #3.
QUALITY_BAR_MINIMUMS: dict[str, tuple[int, int]] = {
    DEFAULT_VISIBILITY: (2, 3),
    "explicit-only": (1, 2),
}


def to_repo_relative(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root).as_posix()


def baseline_path_from_args(repo_root: Path, explicit_path: str) -> Path:
    if explicit_path:
        return Path(explicit_path).resolve()
    return repo_root / DEFAULT_BASELINE_RELPATH


def parse_visibility(text: str) -> str:
    """Read ``metadata.visibility`` from frontmatter ``text``.

    Falls back to ``DEFAULT_VISIBILITY`` when the field is absent or holds a
    value outside ``ALLOWED_VISIBILITY_VALUES`` (matches update_skill_requires
    and validate_skills's tolerant handling of unset/unknown visibility).
    """
    if not text.startswith("---\n"):
        return DEFAULT_VISIBILITY

    parts = text.split("---", 2)
    if len(parts) != 3:
        return DEFAULT_VISIBILITY

    block_match = METADATA_BLOCK_RE.search(parts[1])
    if not block_match:
        return DEFAULT_VISIBILITY

    visibility_match = VISIBILITY_RE.search(block_match.group(1))
    if not visibility_match:
        return DEFAULT_VISIBILITY

    value = visibility_match.group(1)
    return value if value in ALLOWED_VISIBILITY_VALUES else DEFAULT_VISIBILITY


def build_warnings(repo_root: Path, skills: list[SkillInventory]) -> list[str]:
    warnings: list[str] = []
    for skill in skills:
        relpath = to_repo_relative(repo_root, skill.path)
        if skill.eval_coverage_count == 0:
            warnings.append(f"{relpath}: no trigger eval coverage")
        if skill.broad_trigger_risk_flags:
            flags = ", ".join(skill.broad_trigger_risk_flags)
            warnings.append(f"{relpath}: broad trigger risk flags: {flags}")
        if skill.description_trigger_only_flags:
            flags = ", ".join(skill.description_trigger_only_flags)
            warnings.append(f"{relpath}: description trigger-only flags: {flags}")
        minimums = QUALITY_BAR_MINIMUMS.get(skill.visibility)
        if minimums is not None:
            min_positive, min_negative = minimums
            if skill.eval_should_trigger_count < min_positive:
                warnings.append(
                    f"{relpath}: quality-bar shortfall ({skill.visibility}): "
                    f"{skill.eval_should_trigger_count} positive eval case(s), "
                    f"need >= {min_positive}"
                )
            if skill.eval_should_not_trigger_count < min_negative:
                warnings.append(
                    f"{relpath}: quality-bar shortfall ({skill.visibility}): "
                    f"{skill.eval_should_not_trigger_count} negative eval case(s), "
                    f"need >= {min_negative}"
                )
    return warnings


def skill_warning_ids(skill: SkillInventory) -> list[str]:
    """Stable, line/count-independent warning identifiers for `skill`.

    Used by the `--check` ratchet and `--write-baseline`, kept separate from
    `build_warnings`'s human-readable text (which retains line numbers and
    exact counts) so baselined warnings survive unrelated line-number churn.
    """
    ids: set[str] = set()
    if skill.eval_coverage_count == 0:
        ids.add("no-trigger-eval-coverage")
    for flag in skill.broad_trigger_risk_flags:
        ids.add(f"broad-trigger:{flag.split(':', 1)[0]}")
    for flag in skill.description_trigger_only_flags:
        ids.add(f"description-style:{flag.split(':', 1)[0]}")

    minimums = QUALITY_BAR_MINIMUMS.get(skill.visibility)
    if minimums is not None:
        min_positive, min_negative = minimums
        # The count rides in the id (F1): a baselined shortfall covers the
        # baselined count OR BETTER — a regression to fewer cases mints an
        # uncovered id and fires, while improvement never does.
        if skill.eval_should_trigger_count < min_positive:
            ids.add(f"quality-bar:positive-shortfall@{skill.eval_should_trigger_count}")
        if skill.eval_should_not_trigger_count < min_negative:
            ids.add(f"quality-bar:negative-shortfall@{skill.eval_should_not_trigger_count}")

    return sorted(ids)


def build_warning_id_map(skills: list[SkillInventory]) -> dict[str, list[str]]:
    """{skill name: sorted stable warning ids}, omitting skills with none."""
    result: dict[str, list[str]] = {}
    for skill in skills:
        ids = skill_warning_ids(skill)
        if ids:
            result[skill.name] = ids
    return dict(sorted(result.items()))


def load_baseline(path: Path) -> dict[str, list[str]]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}

    result: dict[str, list[str]] = {}
    for name, ids in data.items():
        if isinstance(name, str) and isinstance(ids, list):
            result[name] = [warning_id for warning_id in ids if isinstance(warning_id, str)]
    return result


def write_baseline(path: Path, warning_id_map: dict[str, list[str]]) -> None:
    payload = {name: sorted(ids) for name, ids in sorted(warning_id_map.items())}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ratchet_findings(
    current: dict[str, list[str]],
    baseline: dict[str, list[str]],
) -> dict[str, list[str]]:
    """Compare `current` (this run's warning ids) against the committed
    `baseline`. A current id absent from the baseline is a `new_warnings`
    entry (an error under --check); a baseline id no longer produced is a
    `stale_baseline` entry (informational; shrinkage is the goal)."""
    def covered(warning_id: str, baselined: set[str]) -> bool:
        if warning_id in baselined:
            return True
        # Ordered coverage for count-carrying quality-bar ids: a baseline entry
        # with an equal-or-lower count covers the current state (equal counts
        # match exactly above; higher current count = improvement).
        prefix, sep, count = warning_id.rpartition("@")
        if sep and prefix.startswith("quality-bar:") and count.isdigit():
            for entry in baselined:
                b_prefix, b_sep, b_count = entry.rpartition("@")
                if b_sep and b_prefix == prefix and b_count.isdigit():
                    if int(b_count) <= int(count):
                        return True
        return False

    new_warnings: list[str] = []
    for skill_name in sorted(current):
        baselined = set(baseline.get(skill_name, []))
        for warning_id in current[skill_name]:
            if not covered(warning_id, baselined):
                new_warnings.append(f"{skill_name}: {warning_id}")

    stale_baseline: list[str] = []
    for skill_name in sorted(baseline):
        current_ids = set(current.get(skill_name, []))
        for warning_id in baseline[skill_name]:
            if warning_id not in current_ids:
                stale_baseline.append(f"{skill_name}: {warning_id}")

    return {"new_warnings": new_warnings, "stale_baseline": stale_baseline}

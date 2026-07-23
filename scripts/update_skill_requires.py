#!/usr/bin/env python3
"""Generate and verify the four-tier load-contract manifest in SKILL.md frontmatter.

A skill's frontmatter may carry four `metadata` list fields, each holding
skill-relative paths:

- `requires`  — load before executing; unreadable ⇒ error. Keep to 0-2 entries.
- `resources` — load ONLY when the condition its SKILL.md states matches; the
  SKILL.md condition is the sole authority for when to open one.
- `commands`  — execute or cite by path; never inline into context.
- `templates` — open only when producing that output artifact.

Coverage rule (fail-closed): every file under a skill's `references/`,
`templates/`, and `scripts/` subdirectories must appear in exactly one of
the four lists; a listed file that does not exist is an error. Duplicate
membership across tiers is also an error.

Tier-shape rule (checked in `--check`): `scripts/*` entries may only sit in
`commands`; `templates/*` entries only in `templates`; `references/*`
entries only in `requires` or `resources`. A `requires` list longer than 2
entries is a warning for now — the budget gate hardens it into a failure in
a later wave; existing skills must not fail on this alone.

Migration state decides `--write` behavior per skill:
- "Unmigrated" (none of `resources`/`commands`/`templates` present): keep
  today's behavior — regenerate a single `requires` list holding every file
  under `references/`, `templates/`, and `scripts/`. This keeps skills that
  have not adopted the tier split valid and green.
- "Migrated" (any of `resources`/`commands`/`templates` present): `--write`
  only fixes coverage gaps by appending newly discovered, uncovered files to
  a `# UNSORTED` marker inside the matching list (`resources` for
  `references/*`, `commands` for `scripts/*`, `templates` for
  `templates/*`). It never touches `requires` and never moves an existing
  entry between tiers — retiering is a human decision.

Usage:
    python scripts/update_skill_requires.py --write   # rewrite manifests
    python scripts/update_skill_requires.py --check   # fail if stale (CI)

Only Python stdlib is used.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REQUIRED_SUBDIRS = ("references", "templates", "scripts")
FRONTMATTER_DELIM = "---"

TIER_FIELDS = ("requires", "resources", "commands", "templates")
NEW_TIER_FIELDS = ("resources", "commands", "templates")
TIER_SUBDIR = {
    "requires": "references",
    "resources": "references",
    "commands": "scripts",
    "templates": "templates",
}
SUBDIR_FIELD = {"references": "resources", "scripts": "commands", "templates": "templates"}
REQUIRES_WARN_MAX = 2
UNSORTED_MARKER = "# UNSORTED"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate metadata.requires manifests for repo skills."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="Rewrite stale manifests.")
    mode.add_argument("--check", action="store_true", help="Exit 1 if any manifest is stale.")
    parser.add_argument(
        "--skills-dir",
        default=".agents/skills",
        help="Skills directory relative to repo root.",
    )
    return parser.parse_args()


def required_files(skill_dir: Path) -> list[str]:
    files: list[str] = []
    for sub in REQUIRED_SUBDIRS:
        subdir = skill_dir / sub
        if not subdir.is_dir():
            continue
        for path in sorted(subdir.rglob("*")):
            if path.is_file():
                files.append(path.relative_to(skill_dir).as_posix())
    return files


def split_frontmatter(text: str, path: Path) -> tuple[list[str], str]:
    """Return (frontmatter lines without delimiters, body text)."""
    if not text.startswith(FRONTMATTER_DELIM + "\n"):
        raise ValueError(f"{path}: missing frontmatter opening marker")
    parts = text.split(FRONTMATTER_DELIM, 2)
    if len(parts) != 3:
        raise ValueError(f"{path}: missing frontmatter closing marker")
    return parts[1].strip("\n").splitlines(), parts[2]


def strip_existing_requires(lines: list[str]) -> list[str]:
    """Remove an existing `requires:` block nested under `metadata:`."""
    result: list[str] = []
    skipping = False
    for line in lines:
        if line.strip() == "requires:" and line.startswith("  "):
            skipping = True
            continue
        if skipping:
            if line.startswith("    - "):
                continue
            skipping = False
        result.append(line)
    return result


def build_frontmatter(lines: list[str], requires: list[str], path: Path) -> list[str]:
    """Insert a fresh requires block at the end of the metadata block."""
    lines = strip_existing_requires(lines)
    if not requires:
        return lines

    try:
        meta_idx = next(i for i, line in enumerate(lines) if line.rstrip() == "metadata:")
    except StopIteration:
        raise ValueError(f"{path}: frontmatter has no metadata block")

    end = meta_idx + 1
    while end < len(lines) and (lines[end].startswith("  ") or not lines[end].strip()):
        end += 1

    block = ["  requires:"] + [f"    - {item}" for item in requires]
    return lines[:end] + block + lines[end:]


def render(frontmatter: list[str], body: str) -> str:
    return FRONTMATTER_DELIM + "\n" + "\n".join(frontmatter) + "\n" + FRONTMATTER_DELIM + body


def process_skill(skill_md: Path) -> tuple[str, str]:
    """Return (current text, expected text) for one unmigrated SKILL.md.

    Unchanged legacy behavior: regenerate `requires` from every file under
    `references/`, `templates/`, and `scripts/`. Only valid for skills that
    carry none of `resources`/`commands`/`templates` (see `is_migrated`).
    """
    text = skill_md.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(text, skill_md)
    requires = required_files(skill_md.parent)
    expected = render(build_frontmatter(frontmatter, requires, skill_md), body)
    return text, expected


def parse_tier_lists(lines: list[str]) -> dict[str, list[str]]:
    """Return {field: [items]} for each TIER_FIELDS block present in frontmatter."""
    tiers: dict[str, list[str]] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if line.startswith("  ") and not line.startswith("    ") and stripped.endswith(":"):
            field = stripped[:-1]
            if field in TIER_FIELDS:
                items: list[str] = []
                j = i + 1
                while j < len(lines) and (lines[j].startswith("    ") or not lines[j].strip()):
                    entry = lines[j].strip()
                    if entry.startswith("- "):
                        items.append(entry[2:].strip())
                    j += 1
                tiers[field] = items
                i = j
                continue
        i += 1
    return tiers


def is_migrated(tiers: dict[str, list[str]]) -> bool:
    return any(field in tiers for field in NEW_TIER_FIELDS)


def collect_warnings(tiers: dict[str, list[str]], relpath: str) -> list[str]:
    warnings: list[str] = []
    requires_count = len(tiers.get("requires", []))
    if requires_count > REQUIRES_WARN_MAX:
        warnings.append(
            f"{relpath}: requires has {requires_count} entries; "
            f"the budget gate will cap this at {REQUIRES_WARN_MAX} later"
        )
    return warnings


def check_migrated_skill(
    relpath: str, tiers: dict[str, list[str]], physical: list[str], body: str = ""
) -> list[str]:
    """Return coverage + tier-shape + resource-condition errors for a migrated skill."""
    errors: list[str] = []
    physical_set = set(physical)

    membership: dict[str, list[str]] = {}
    for field in TIER_FIELDS:
        for item in tiers.get(field, []):
            membership.setdefault(item, []).append(field)

    for f in physical:
        fields = membership.get(f, [])
        if not fields:
            errors.append(f"{relpath}: {f} is not listed in requires/resources/commands/templates")
        elif len(fields) > 1:
            errors.append(f"{relpath}: {f} is listed in more than one tier: {', '.join(fields)}")

    for field in TIER_FIELDS:
        for item in tiers.get(field, []):
            if item not in physical_set:
                errors.append(f"{relpath}: {field} lists a file that does not exist: {item}")
                continue
            expected_subdir = TIER_SUBDIR[field]
            if item.split("/", 1)[0] != expected_subdir:
                errors.append(f"{relpath}: {field} entry '{item}' must live under {expected_subdir}/")

    # A resource loads ONLY when the SKILL.md body states its condition; a resource
    # the body never mentions can therefore never load — the silent inversion of the
    # skipped-required-file failure the requires manifest originally fixed.
    for item in tiers.get("resources", []):
        basename = item.rsplit("/", 1)[-1]
        if body and basename not in body:
            errors.append(
                f"{relpath}: resources entry '{item}' is never mentioned in the SKILL.md "
                "body — state its open-condition or move it to requires"
            )

    return errors


def _append_unsorted(lines: list[str], field: str, new_items: list[str]) -> list[str]:
    header = f"  {field}:"
    for i, line in enumerate(lines):
        if line.rstrip() == header:
            j = i + 1
            while j < len(lines) and (lines[j].startswith("    ") or not lines[j].strip()):
                j += 1
            insert: list[str] = []
            if not any(lines[k].strip() == UNSORTED_MARKER for k in range(i + 1, j)):
                insert.append(f"    {UNSORTED_MARKER}")
            insert += [f"    - {item}" for item in new_items]
            return lines[:j] + insert + lines[j:]

    try:
        meta_idx = next(i for i, line in enumerate(lines) if line.rstrip() == "metadata:")
    except StopIteration:
        raise ValueError("frontmatter has no metadata block")
    end = meta_idx + 1
    while end < len(lines) and (lines[end].startswith("  ") or not lines[end].strip()):
        end += 1
    block = [header, f"    {UNSORTED_MARKER}"] + [f"    - {item}" for item in new_items]
    return lines[:end] + block + lines[end:]


def fix_migrated_skill(text: str, skill_md: Path) -> str:
    """Append uncovered files to their matching tier's `# UNSORTED` position.

    Never edits `requires` and never moves an existing entry between tiers —
    only newly discovered, uncovered files are appended.
    """
    frontmatter, body = split_frontmatter(text, skill_md)
    tiers = parse_tier_lists(frontmatter)
    physical = required_files(skill_md.parent)

    covered = {item for field in TIER_FIELDS for item in tiers.get(field, [])}
    by_field: dict[str, list[str]] = {"resources": [], "commands": [], "templates": []}
    for f in physical:
        if f in covered:
            continue
        field = SUBDIR_FIELD[f.split("/", 1)[0]]
        by_field[field].append(f)

    if not any(by_field.values()):
        return text

    lines = list(frontmatter)
    for field, new_items in by_field.items():
        if new_items:
            lines = _append_unsorted(lines, field, new_items)

    return render(lines, body)


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    skills_dir = repo_root / args.skills_dir
    if not skills_dir.is_dir():
        print(f"error: {skills_dir} is not a directory", file=sys.stderr)
        return 2

    stale: list[Path] = []
    contract_errors: list[str] = []
    warnings: list[str] = []

    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        text = skill_md.read_text(encoding="utf-8")
        try:
            frontmatter, _body = split_frontmatter(text, skill_md)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        tiers = parse_tier_lists(frontmatter)
        relpath = skill_md.relative_to(repo_root).as_posix()
        warnings.extend(collect_warnings(tiers, relpath))

        if is_migrated(tiers):
            physical = required_files(skill_md.parent)
            contract_errors.extend(check_migrated_skill(relpath, tiers, physical, _body))
            if args.write:
                fixed = fix_migrated_skill(text, skill_md)
                if fixed != text:
                    stale.append(skill_md)
                    skill_md.write_text(fixed, encoding="utf-8")
            continue

        legacy_physical = required_files(skill_md.parent)
        mis_tiered = [
            f for f in legacy_physical if f.split("/", 1)[0] in ("scripts", "templates")
        ]
        if mis_tiered:
            # Legacy full-regenerate would dump these into requires, i.e. always-load
            # an executable/template as prompt context — refuse instead of mis-tiering.
            contract_errors.append(
                f"{relpath}: owns {', '.join(sorted(mis_tiered))} but has not adopted the "
                "commands/templates tiers — add resources/commands/templates fields"
            )
            continue

        try:
            current, expected = process_skill(skill_md)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        if current != expected:
            stale.append(skill_md)
            if args.write:
                skill_md.write_text(expected, encoding="utf-8")

    rel = [p.relative_to(repo_root).as_posix() for p in stale]
    for warning in warnings:
        print(f"warning: {warning}")

    if args.check:
        ok = True
        if stale:
            ok = False
            print("Stale load-contract manifests (run --write):")
            for name in rel:
                print(f"- {name}")
        if contract_errors:
            ok = False
            print("Load-contract violations:")
            for err in contract_errors:
                print(f"- {err}")
        if ok:
            print("All skill load-contract manifests are current.")
            return 0
        return 1

    if contract_errors:
        print("Load-contract violations (fix manually; --write never moves entries between tiers):")
        for err in contract_errors:
            print(f"- {err}")
    if stale:
        print(f"Updated {len(stale)} manifest(s):")
        for name in rel:
            print(f"- {name}")
    else:
        print("All skill load-contract manifests already current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

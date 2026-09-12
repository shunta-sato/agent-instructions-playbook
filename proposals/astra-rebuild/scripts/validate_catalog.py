#!/usr/bin/env python3
"""Validate active packages and evaluation definitions; never grade model behavior."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    skills = {path.parent.name: path for path in (root / "skills").glob("*/SKILL.md")}
    if not skills:
        return ["empty skill catalog"]
    for name, path in skills.items():
        if path.is_symlink() or path.parent.is_symlink():
            errors.append(f"{name}: distribution packages must not be symlinks")
            continue
        if any(item.is_symlink() for item in path.parent.rglob("*")):
            errors.append(f"{name}: package resources must not be symlinks")
        content = path.read_text(encoding="utf-8")
        parts = content.split("---\n", 2)
        if len(parts) != 3 or parts[0]:
            errors.append(f"{name}: missing front matter")
            continue
        lines = parts[1].splitlines()
        if any(": " not in line or line[:1].isspace() for line in lines):
            errors.append(f"{name}: only flat name and JSON-quoted description are supported")
        fields = dict(line.split(": ", 1) for line in lines if ": " in line)
        if len(fields) != len(lines):
            errors.append(f"{name}: duplicate or unsupported front matter")
        try:
            description = json.loads(fields.get("description", "null"))
        except json.JSONDecodeError:
            description = None
        if fields.get("name") != name or not NAME.fullmatch(name):
            errors.append(f"{name}: invalid name")
        if set(fields) != {"name", "description"}:
            errors.append(f"{name}: use only name/description; no hidden required-load graph")
        if not isinstance(description, str) or not description.strip():
            errors.append(f"{name}: missing description")
        elif len(description) > 240:
            errors.append(f"{name}: description exceeds the documented 240-character editorial budget")
        for target in re.findall(r"\]\(([^)]+)\)", parts[2]):
            if "://" in target or target.startswith("#"):
                continue
            resolved = (path.parent / target.split("#", 1)[0]).resolve()
            if not resolved.is_relative_to(path.parent.resolve()) or not resolved.exists():
                errors.append(f"{name}: missing or non-local resource: {target}")
        for resource in re.findall(r"`(scripts/[^` ]+\.py)`", parts[2]):
            if not (path.parent / resource).is_file():
                errors.append(f"{name}: missing bundled command: {resource}")
    try:
        migration = json.loads((root / "docs/migration-map.json").read_text())
        old_names = set()
        for entry in migration["entries"]:
            if entry["old"] in old_names:
                errors.append("duplicate legacy migration entry")
            old_names.add(entry["old"])
            destination = (root / entry["destination"]).resolve()
            if not destination.is_relative_to(root.resolve()) or not destination.is_file():
                errors.append(f"missing migration destination: {entry['old']}")
        packs = json.loads((root / "packs.json").read_text())
        if packs.get("version") != 2 or not isinstance(packs.get("packs"), dict):
            errors.append("invalid pack schema")
        else:
            exposed: set[str] = set()
            for name, members in packs["packs"].items():
                if not NAME.fullmatch(name) or not isinstance(members, list) or not members or not all(isinstance(item, str) for item in members):
                    errors.append(f"invalid pack: {name}")
                    continue
                if len(members) != len(set(members)) or set(members) - skills.keys():
                    errors.append(f"duplicate/unknown pack members: {name}")
                exposed.update(members)
            if exposed != skills.keys():
                errors.append("some skills are absent from all packs")
        suite = json.loads((root / "evals/cases.json").read_text())
        if suite.get("version") != 2 or not isinstance(suite.get("cases"), list) or not suite["cases"]:
            errors.append("invalid behavior suite")
        else:
            seen = set()
            for case in suite["cases"]:
                if not isinstance(case, dict):
                    errors.append("case must be an object")
                    continue
                key = case.get("id")
                if not isinstance(key, str) or not NAME.fullmatch(key) or key in seen:
                    errors.append("invalid/duplicate case id")
                    continue
                seen.add(key)
                if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
                    errors.append(f"{key}: missing prompt")
                names = case.get("skills")
                if not isinstance(names, list) or not all(isinstance(n, str) and n in skills for n in names):
                    errors.append(f"{key}: invalid skill selection")
                for field, directory in (("fixture", "fixtures"), ("oracle", "oracles")):
                    name = case.get(field)
                    if name is not None:
                        if not isinstance(name, str):
                            errors.append(f"{key}: invalid {field}")
                            continue
                        target = root / "evals" / directory / name
                        if not target.resolve().is_relative_to((root / "evals" / directory).resolve()) or not target.exists():
                            errors.append(f"{key}: missing or escaping {field}")
                reviews = case.get("review_checks")
                if not isinstance(reviews, list) or not all(isinstance(x, str) and x.strip() for x in reviews):
                    errors.append(f"{key}: invalid review checks")
                elif not case.get("oracle") and not reviews:
                    errors.append(f"{key}: case has no oracle or review criteria")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        errors.append(str(exc))
    return errors


def main() -> int:
    errors = validate(ROOT)
    if errors:
        print("Catalog validation failed:\n" + "\n".join(f"- {e}" for e in errors))
        return 1
    print("Active catalog, resources, packs and eval definitions validated; model behavior was not executed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

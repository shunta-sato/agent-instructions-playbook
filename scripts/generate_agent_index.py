#!/usr/bin/env python3
"""Generate the compact AGENTS.md skill index and optional README catalog."""

from __future__ import annotations

import argparse
import glob
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

try:
    from scripts.update_skill_requires import DEFAULT_VISIBILITY
except ImportError:  # pragma: no cover
    from update_skill_requires import DEFAULT_VISIBILITY

BEGIN_MARKER = "<!-- BEGIN AGENT INDEX (generated) -->"
END_MARKER = "<!-- END AGENT INDEX (generated) -->"
README_SKILLS_BEGIN_MARKER = "<!-- BEGIN README SKILL CATALOG (generated) -->"
README_SKILLS_END_MARKER = "<!-- END README SKILL CATALOG (generated) -->"
DEFAULT_MAX_BYTES = 8192
INDEX_VISIBILITY_GROUPS = {"explicit-only": "skills-explicit", "template": "skills-template"}


@dataclass(frozen=True)
class SkillMeta:
    name: str
    short: str
    skill_path: str
    visibility: str = DEFAULT_VISIBILITY


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return value.strip()


def _squash_ws(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def _truncate(value: str, max_len: int) -> str:
    value = _squash_ws(value).replace("|", "/")
    return value if len(value) <= max_len else value[: max_len - 1] + "…"


def _parse_skill_frontmatter(skill_md: Path) -> Tuple[str, str, str]:
    text = _read_text(skill_md)
    if not text.startswith("---"):
        raise ValueError(f"Missing YAML frontmatter: {skill_md}")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Malformed YAML frontmatter: {skill_md}")
    frontmatter = parts[1]
    name_match = re.search(r"^\s*name:\s*(.+)\s*$", frontmatter, re.M)
    desc_match = re.search(r"^\s*description:\s*(.+)\s*$", frontmatter, re.M)
    short_match = re.search(r"^\s*short-description:\s*(.+)\s*$", frontmatter, re.M)
    visibility_match = re.search(r"^\s*visibility:\s*(.+)\s*$", frontmatter, re.M)
    if not name_match:
        raise ValueError(f"Missing 'name' in frontmatter: {skill_md}")
    name = _strip_quotes(name_match.group(1))
    short = _strip_quotes((short_match or desc_match).group(1)) if short_match or desc_match else ""
    visibility = _strip_quotes(visibility_match.group(1)) if visibility_match else DEFAULT_VISIBILITY
    return name, short, visibility


def _collect_skills(repo_root: Path) -> List[SkillMeta]:
    skills: list[SkillMeta] = []
    pattern = repo_root / ".agents" / "skills" / "*" / "SKILL.md"
    for raw in sorted(glob.glob(str(pattern))):
        path = Path(raw)
        name, short, visibility = _parse_skill_frontmatter(path)
        skills.append(
            SkillMeta(name, _truncate(short, 72), path.relative_to(repo_root).as_posix(), visibility)
        )
    return sorted(skills, key=lambda skill: (skill.name, skill.skill_path))


def _collect_source_skills(repo_root: Path) -> List[SkillMeta]:
    return _collect_skills(repo_root)


def _build_index_text(repo_root: Path, max_bytes: int) -> str:
    skills = _collect_skills(repo_root)
    lines = [
        "AGENT_INDEX_V1",
        f"meta|format=v1|max_bytes={max_bytes}|invoke=codex:$<skill>,copilot:/<skill>",
        "defaults|govern=user-value-delivery|workflow=dev-workflow|finish=quality-gate|verify=COMMANDS.md",
        "core|AGENTS.md|COMMANDS.md|PLANS.md|plans/README.md|README.md|REFERENCES.md",
        "skills|name|short|skill_path",
    ]
    lines.extend(
        f"skill|{skill.name}|{skill.short}|{skill.skill_path}"
        for skill in skills if skill.visibility == DEFAULT_VISIBILITY
    )
    for visibility, token in INDEX_VISIBILITY_GROUPS.items():
        names = [skill.name for skill in skills if skill.visibility == visibility]
        if names:
            lines.append("|".join([token, *names]))
    lines.append("end|AGENT_INDEX_V1")
    index = "\n".join(lines) + "\n"
    size = len(index.encode("utf-8"))
    if size > max_bytes:
        raise ValueError(f"Generated index is too large: {size} bytes > {max_bytes} bytes")
    return index


def _markdown_table_cell(value: str) -> str:
    return _squash_ws(value).replace("|", r"\|")


def _build_readme_skill_catalog_text(repo_root: Path) -> str:
    lines = ["| Skill | Description | Source |", "| --- | --- | --- |"]
    for skill in _collect_source_skills(repo_root):
        lines.append(
            f"| `{_markdown_table_cell(skill.name)}` | {_markdown_table_cell(skill.short)} | "
            f"`{_markdown_table_cell(skill.skill_path)}` |"
        )
    return "\n".join(lines) + "\n"


def _replace_block(text: str, begin: str, end: str, body: str, *, required: bool) -> str:
    if begin not in text or end not in text:
        if required:
            raise ValueError(f"Missing required markers: {begin} / {end}")
        return text
    pre, rest = text.split(begin, 1)
    _, post = rest.split(end, 1)
    block = f"{begin}\n{body}{end}"
    return pre.rstrip() + "\n\n" + block + "\n\n" + post.lstrip()


def _embed_into_agents_md(agents_text: str, index_text: str) -> str:
    return _replace_block(
        agents_text, BEGIN_MARKER, END_MARKER, f"```text\n{index_text}```\n", required=True
    )


def _embed_into_readme(readme_text: str, catalog_text: str) -> str:
    return _replace_block(
        readme_text, README_SKILLS_BEGIN_MARKER, README_SKILLS_END_MARKER,
        catalog_text, required=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--agents", default="AGENTS.md")
    parser.add_argument("--readme", default="README.md")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parent.parent
    agents_path = repo_root / args.agents
    readme_path = repo_root / args.readme
    original_agents = _read_text(agents_path)
    original_readme = _read_text(readme_path)
    updated_agents = _embed_into_agents_md(original_agents, _build_index_text(repo_root, args.max_bytes))
    updated_readme = _embed_into_readme(original_readme, _build_readme_skill_catalog_text(repo_root))

    if args.check:
        changed = False
        if updated_agents != original_agents:
            print("AGENTS.md agent index is out of date.")
            changed = True
        if updated_readme != original_readme:
            print("README.md skill catalog is out of date.")
            changed = True
        if changed:
            print("Run: python scripts/generate_agent_index.py --write")
            return 1
        return 0

    if updated_agents != original_agents:
        agents_path.write_text(updated_agents, encoding="utf-8")
        print("Updated AGENTS.md agent index.")
    else:
        print("AGENTS.md agent index is already up to date.")
    if updated_readme != original_readme:
        readme_path.write_text(updated_readme, encoding="utf-8")
        print("Updated README.md skill catalog.")
    else:
        print("README.md skill catalog is already up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

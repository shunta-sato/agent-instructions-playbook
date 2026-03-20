#!/usr/bin/env python3
"""
generate_agent_index.py

Generates a compressed, machine-friendly index of this repo's playbooks and embeds it into AGENTS.md.

Design goals:
- Always-on "index" in AGENTS.md (passive context), inspired by Vercel's eval findings.
- Keep it small (default max 8192 bytes) to avoid context bloat.
- Deterministic output (no timestamps).

Usage:
  python scripts/generate_agent_index.py --write   # update AGENTS.md in place (default)
  python scripts/generate_agent_index.py --check   # fail if AGENTS.md is not up-to-date
"""

from __future__ import annotations

import argparse
import glob
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


BEGIN_MARKER = "<!-- BEGIN AGENT INDEX (generated) -->"
END_MARKER = "<!-- END AGENT INDEX (generated) -->"
README_SKILLS_BEGIN_MARKER = "<!-- BEGIN README SKILL CATALOG (generated) -->"
README_SKILLS_END_MARKER = "<!-- END README SKILL CATALOG (generated) -->"
DEFAULT_MAX_BYTES = 8192


@dataclass(frozen=True)
class SkillMeta:
    name: str
    short: str
    codex_path: str


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1]
    return s.strip()


def _squash_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())


def _truncate(s: str, max_len: int) -> str:
    s = _squash_ws(s).replace("|", "/")
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"


def _parse_skill_frontmatter(skill_md: Path) -> Tuple[str, str]:
    """
    Returns (name, short_description). Uses metadata.short-description when available,
    else falls back to description.
    We intentionally implement a minimal parser to avoid external dependencies.
    """
    txt = _read_text(skill_md)
    if not txt.startswith("---"):
        raise ValueError(f"Missing YAML frontmatter: {skill_md}")
    parts = txt.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Malformed YAML frontmatter: {skill_md}")
    fm = parts[1]

    name_m = re.search(r"^\s*name:\s*(.+)\s*$", fm, re.M)
    desc_m = re.search(r"^\s*description:\s*(.+)\s*$", fm, re.M)
    short_m = re.search(r"^\s*short-description:\s*(.+)\s*$", fm, re.M)

    if not name_m:
        raise ValueError(f"Missing 'name' in frontmatter: {skill_md}")
    name = _strip_quotes(name_m.group(1))

    short = ""
    if short_m:
        short = _strip_quotes(short_m.group(1))
    elif desc_m:
        short = _strip_quotes(desc_m.group(1))

    return name, short


def _collect_skills(repo_root: Path) -> List[SkillMeta]:
    codex = {}

    for p in glob.glob(str(repo_root / ".agents" / "skills" / "*" / "SKILL.md")):
        md = Path(p)
        name, short = _parse_skill_frontmatter(md)
        codex[name] = (short, str(md.relative_to(repo_root).as_posix()))

    names = sorted(set(codex.keys()))
    out: List[SkillMeta] = []

    for name in names:
        if name.endswith("-template"):
            continue

        short = codex[name][0]
        short = _truncate(short, 72)

        codex_path = codex[name][1]

        out.append(
            SkillMeta(
                name=name,
                short=short,
                codex_path=codex_path,
            )
        )

    return out


def _collect_source_skills(repo_root: Path) -> List[SkillMeta]:
    """Collect skill catalog from .agents/skills only (source of truth)."""
    out: List[SkillMeta] = []
    for p in glob.glob(str(repo_root / ".agents" / "skills" / "*" / "SKILL.md")):
        md = Path(p)
        name, short = _parse_skill_frontmatter(md)
        out.append(
            SkillMeta(
                name=name,
                short=_truncate(short, 72),
                codex_path=str(md.relative_to(repo_root).as_posix()),
            )
        )
    return sorted(out, key=lambda s: s.name)


def _build_index_text(
    repo_root: Path,
    max_bytes: int,
) -> str:
    skills = _collect_skills(repo_root)

    lines: List[str] = []
    lines.append("AGENT_INDEX_V1")
    lines.append(f"meta|format=v1|max_bytes={max_bytes}|codex_invoke=$<skill>")
    lines.append("defaults|workflow=dev-workflow|finish=quality-gate|verify=COMMANDS.md")
    lines.append("core|AGENTS.md|COMMANDS.md|PLANS.md|plans/README.md|README.md|REFERENCES.md")

    lines.append("skills|name|short|codex_skill")
    for s in skills:
        lines.append(f"skill|{s.name}|{s.short}|{s.codex_path}")

    lines.append("end|AGENT_INDEX_V1")

    index = "\n".join(lines) + "\n"
    size = len(index.encode("utf-8"))
    if size > max_bytes:
        raise ValueError(
            f"Generated index is too large: {size} bytes > {max_bytes} bytes. "
            "Shorten short-descriptions or raise max_bytes (but keep AGENTS.md small)."
        )

    return index


def _build_readme_skill_catalog_text(repo_root: Path) -> str:
    skills = _collect_source_skills(repo_root)
    lines: List[str] = []
    for s in skills:
        lines.append(f"- `{s.name}` — {s.short}")
    return "\n".join(lines) + "\n"


def _embed_into_agents_md(agents_text: str, index_text: str) -> str:
    if BEGIN_MARKER not in agents_text or END_MARKER not in agents_text:
        raise ValueError(
            f"Missing markers in AGENTS.md. Required markers:\n{BEGIN_MARKER}\n{END_MARKER}"
        )

    pre, rest = agents_text.split(BEGIN_MARKER, 1)
    _, post = rest.split(END_MARKER, 1)

    block = (
        f"{BEGIN_MARKER}\n"
        "```text\n"
        f"{index_text}"
        "```\n"
        f"{END_MARKER}"
    )

    # Keep exactly one blank line between sections around the block.
    pre = pre.rstrip() + "\n\n"
    post = "\n\n" + post.lstrip()

    return pre + block + post


def _embed_into_readme(readme_text: str, catalog_text: str) -> str:
    if README_SKILLS_BEGIN_MARKER not in readme_text or README_SKILLS_END_MARKER not in readme_text:
        raise ValueError(
            "Missing markers in README.md. Required markers:\n"
            f"{README_SKILLS_BEGIN_MARKER}\n{README_SKILLS_END_MARKER}"
        )

    pre, rest = readme_text.split(README_SKILLS_BEGIN_MARKER, 1)
    _, post = rest.split(README_SKILLS_END_MARKER, 1)

    block = (
        f"{README_SKILLS_BEGIN_MARKER}\n"
        f"{catalog_text}"
        f"{README_SKILLS_END_MARKER}"
    )

    pre = pre.rstrip() + "\n\n"
    post = "\n\n" + post.lstrip()
    return pre + block + post


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="Fail if AGENTS.md would change.")
    ap.add_argument("--write", action="store_true", help="Write changes to AGENTS.md (default).")
    ap.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    ap.add_argument(
        "--repo-root", type=str, default="", help="Repo root (default: parent of scripts/)."
    )
    ap.add_argument(
        "--agents", type=str, default="AGENTS.md", help="Path to AGENTS.md relative to repo root."
    )
    ap.add_argument(
        "--readme", type=str, default="README.md", help="Path to README.md relative to repo root."
    )
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parent.parent
    agents_path = (repo_root / args.agents).resolve()
    readme_path = (repo_root / args.readme).resolve()

    original_agents = _read_text(agents_path)
    original_readme = _read_text(readme_path)
    index_text = _build_index_text(repo_root=repo_root, max_bytes=args.max_bytes)
    catalog_text = _build_readme_skill_catalog_text(repo_root=repo_root)
    updated_agents = _embed_into_agents_md(original_agents, index_text)
    updated_readme = _embed_into_readme(original_readme, catalog_text)

    if args.check:
        has_diff = False
        if updated_agents != original_agents:
            print("AGENTS.md agent index is out of date.")
            print("Run: python scripts/generate_agent_index.py --write")
            has_diff = True
        if updated_readme != original_readme:
            print("README.md skill catalog is out of date.")
            print("Run: python scripts/generate_agent_index.py --write")
            has_diff = True
        if has_diff:
            return 1
        return 0

    # default to write if neither flag is explicitly chosen
    if not args.write and not args.check:
        args.write = True

    if args.write:
        wrote_any = False
        if updated_agents != original_agents:
            agents_path.write_text(updated_agents, encoding="utf-8")
            print("Updated AGENTS.md agent index.")
            wrote_any = True
        else:
            print("AGENTS.md agent index is already up to date.")
        if updated_readme != original_readme:
            readme_path.write_text(updated_readme, encoding="utf-8")
            print("Updated README.md skill catalog.")
            wrote_any = True
        else:
            print("README.md skill catalog is already up to date.")
        if not wrote_any:
            print("Nothing to update.")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

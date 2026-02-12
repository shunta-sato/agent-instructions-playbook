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
DEFAULT_MAX_BYTES = 8192


@dataclass(frozen=True)
class SkillMeta:
    name: str
    short: str
    codex_path: str  # "-" if missing
    github_path: str  # "-" if missing
    prompt: str  # "/name" or "-" if missing


@dataclass(frozen=True)
class InstructionMeta:
    title: str
    apply_to: str
    path: str
    first_rule: str


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


def _parse_prompt_file(prompt_md: Path) -> Tuple[str, str]:
    """
    Returns (name, short). Name comes from first '# ' heading.
    Short comes from the first non-empty line after that heading.
    """
    lines = _read_text(prompt_md).splitlines()
    for i, line in enumerate(lines):
        if line.startswith("# "):
            name = line[2:].strip()
            short = ""
            for j in range(i + 1, len(lines)):
                if lines[j].strip():
                    short = lines[j].strip()
                    break
            return name, short
    raise ValueError(f"Missing '# <name>' heading: {prompt_md}")


def _parse_instruction_file(repo_root: Path, instr_md: Path) -> InstructionMeta:
    txt = _read_text(instr_md)

    apply_to = ""
    if txt.startswith("---"):
        parts = txt.split("---", 2)
        if len(parts) >= 3:
            fm = parts[1]
            m = re.search(r"^\s*applyTo:\s*(.+)\s*$", fm, re.M)
            if m:
                apply_to = _strip_quotes(m.group(1))

    lines = txt.splitlines()
    title = instr_md.stem
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break

    first_rule = ""
    if "# " in txt:
        # Find first non-empty non-heading line after the first H1.
        try:
            h1_idx = next(i for i, l in enumerate(lines) if l.startswith("# "))
            for j in range(h1_idx + 1, len(lines)):
                if not lines[j].strip():
                    continue
                if lines[j].startswith("#"):
                    continue
                first_rule = lines[j].strip()
                break
        except StopIteration:
            pass

    return InstructionMeta(
        title=_truncate(title, 40),
        apply_to=_truncate(apply_to, 40),
        path=str(instr_md.relative_to(repo_root).as_posix()),
        first_rule=_truncate(first_rule, 72),
    )


def _collect_skills(repo_root: Path, prompts: Dict[str, str]) -> List[SkillMeta]:
    codex = {}
    github = {}

    for p in glob.glob(str(repo_root / ".agents" / "skills" / "*" / "SKILL.md")):
        md = Path(p)
        name, short = _parse_skill_frontmatter(md)
        codex[name] = (short, str(md.relative_to(repo_root).as_posix()))

    for p in glob.glob(str(repo_root / ".github" / "skills" / "*" / "SKILL.md")):
        md = Path(p)
        name, short = _parse_skill_frontmatter(md)
        github[name] = (short, str(md.relative_to(repo_root).as_posix()))

    names = sorted(set(codex.keys()) | set(github.keys()))
    out: List[SkillMeta] = []

    for name in names:
        # prefer codex short if present, else github short
        short = codex.get(name, github.get(name))[0]
        short = _truncate(short, 72)

        codex_path = codex[name][1] if name in codex else "-"
        github_path = github[name][1] if name in github else "-"
        prompt_name = f"/{name}" if name in prompts else "-"

        out.append(
            SkillMeta(
                name=name,
                short=short,
                codex_path=codex_path,
                github_path=github_path,
                prompt=prompt_name,
            )
        )

    return out


def _collect_prompts(repo_root: Path) -> Dict[str, str]:
    prompts: Dict[str, str] = {}
    for p in glob.glob(str(repo_root / ".github" / "prompts" / "*.prompt.md")):
        md = Path(p)
        name, short = _parse_prompt_file(md)
        prompts[name] = _truncate(short, 72)
    return prompts


def _build_index_text(
    repo_root: Path,
    max_bytes: int,
) -> str:
    prompts = _collect_prompts(repo_root)
    skills = _collect_skills(repo_root, prompts)

    # Optional mapping: prompt -> related skill (to reduce decision friction)
    prompt_to_skill = {
        "review-antipatterns": "code-smells-and-antipatterns",
        "review-readability": "code-readability",
        "review-modularity": "modularity",
        "write-requirements": "requirements-documentation",
        "dev-workflow": "dev-workflow",
        "quality-gate": "quality-gate",
        "status-update": "execution-plans",
    }

    # Prompts that do not share the same name with a skill are listed explicitly.
    skill_names = {s.name for s in skills}
    extra_prompt_names = sorted([p for p in prompts.keys() if p not in skill_names])

    # Instructions (path-specific rules)
    instrs: List[InstructionMeta] = []
    for p in glob.glob(str(repo_root / ".github" / "instructions" / "*.instructions.md")):
        instrs.append(_parse_instruction_file(repo_root, Path(p)))
    instrs.sort(key=lambda x: x.path)

    lines: List[str] = []
    lines.append("AGENT_INDEX_V1")
    lines.append(
        f"meta|format=v1|max_bytes={max_bytes}|codex_invoke=$<skill>|prompt_invoke=/<prompt>"
    )
    lines.append(
        "important|Prefer repo playbooks/references over pre-training for project-specific decisions."
    )
    lines.append("defaults|workflow=dev-workflow|finish=quality-gate|verify=COMMANDS.md")
    lines.append("path_rules|copilot=auto_apply_applyTo|codex=manual_open")
    lines.append("core|AGENTS.md|COMMANDS.md|PLANS.md|plans/README.md|README.md|REFERENCES.md")

    lines.append("skills|name|short|codex_skill|github_skill|prompt")
    for s in skills:
        lines.append(
            f"skill|{s.name}|{s.short}|{s.codex_path}|{s.github_path}|{s.prompt}"
        )

    if extra_prompt_names:
        lines.append("prompts|name|short|path|related_skill")
        for name in extra_prompt_names:
            path = f".github/prompts/{name}.prompt.md"
            related = prompt_to_skill.get(name, "-")
            lines.append(f"prompt|{name}|{prompts[name]}|{path}|{related}")

    if instrs:
        lines.append("instructions|title|applyTo|path|first_rule")
        for ins in instrs:
            lines.append(
                f"instruction|{ins.title}|{ins.apply_to}|{ins.path}|{ins.first_rule}"
            )

    lines.append("end|AGENT_INDEX_V1")

    index = "\n".join(lines) + "\n"
    size = len(index.encode("utf-8"))
    if size > max_bytes:
        raise ValueError(
            f"Generated index is too large: {size} bytes > {max_bytes} bytes. "
            "Shorten short-descriptions or raise max_bytes (but keep AGENTS.md small)."
        )

    return index


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
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parent.parent
    agents_path = (repo_root / args.agents).resolve()

    original = _read_text(agents_path)
    index_text = _build_index_text(repo_root=repo_root, max_bytes=args.max_bytes)
    updated = _embed_into_agents_md(original, index_text)

    if args.check:
        if updated != original:
            print("AGENTS.md agent index is out of date.")
            print("Run: python scripts/generate_agent_index.py --write")
            return 1
        return 0

    # default to write if neither flag is explicitly chosen
    if not args.write and not args.check:
        args.write = True

    if args.write:
        if updated != original:
            agents_path.write_text(updated, encoding="utf-8")
            print("Updated AGENTS.md agent index.")
        else:
            print("AGENTS.md agent index is already up to date.")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Lint the instruction graph across `.agents/skills`.

For every skill (its `SKILL.md` plus every `.md` file listed in its
`metadata.requires`/`resources`/`templates`), verify:

1. Every backticked `` `$name` `` / `` `/name` `` skill reference resolves to
   an existing skill directory.
2. Every backticked token that looks like a skill-relative or repo-relative
   documentation path (`references/...`, `scripts/...`, `templates/...`,
   `.agents/...`, `plans/...`, `evals/...`, `tests/...`, or a known
   repo-root file) resolves to a real file. Bare filenames with no `/`
   (other than the root allowlist), and prefixes surveyed to be entirely
   illustrative output-artifact or target-project conventions (`docs/`,
   `reports/`, singular `.agent/`) are intentionally out of scope — see
   plans/20260725-lint-migration.md and the L2 worker report for the survey
   that grounds this.
3. Every `<path-or-skill-name> §<anchor>` reference (numeric like `§2a` or
   `§4.4`, a `§N-§M` range, or a word/phrase like `§Coverage`) resolves to a
   heading, bold-line, or `Label:` line marker in the target file(s). Only
   anchors with a backticked path/skill-name token immediately before them
   on the same line are checked — bare self-references with no path token
   are out of scope by design (see report).
4. Every `metadata.commands` entry exists and is a `.py`/`.sh` file.

Content inside fenced code blocks (``` / ~~~) is skipped for rules 1-3: it
is quoted example/template output (e.g. a worked preflight dry run), not a
live routing instruction.

Findings not present in the committed `scripts/instruction_graph_baseline.json`
ratchet fail the run (exit 1); baselined findings are pre-existing,
judgment-required, or sibling-owned (dev-workflow/quality-gate) and pass —
shrinking that file is the goal, not growing it.

Only Python stdlib is used.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from scripts.update_skill_requires import TIER_FIELDS, parse_tier_lists, split_frontmatter
except ImportError:  # pragma: no cover - direct execution puts scripts/ on sys.path
    from update_skill_requires import TIER_FIELDS, parse_tier_lists, split_frontmatter

SKILLS_DIR = ".agents/skills"
BASELINE_PATH = "scripts/instruction_graph_baseline.json"

DOLLAR_SKILL_RE = re.compile(r"`\$([a-z][a-z0-9-]*)`")
SLASH_SKILL_RE = re.compile(r"`/([a-z][a-z0-9-]*)`")
BACKTICK_RE = re.compile(r"`([^`\n]+)`")
FENCE_RE = re.compile(r"^\s*(```+|~~~+)")

PLACEHOLDER_CHARS = ("<", ">", "*", "{")
N_STYLE_RE = re.compile(r"(?:^|[-_./])N(?:$|[-_./])")
EXTENSION_RE = re.compile(r"\.[A-Za-z0-9]{1,10}$")
PATH_PREFIXES = ("references/", "scripts/", "templates/", ".agents/", "plans/", "evals/", "tests/")
ROOT_FILES = {"AGENTS.md", "COMMANDS.md", "PLANS.md", "README.md", "REFERENCES.md", "CLAUDE.md", "CHANGELOG.md"}

NUMERIC_ANCHOR_RE = re.compile(r"\d+[a-zA-Z]?(?:\.\d+)?")
WORD_STOP_RE = re.compile(r"[.,)\]:;—]")
BETWEEN_OK_RE = re.compile(r"^[\s(:\-—]*$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
BOLD_LINE_RE = re.compile(r"^\*\*(.+?)\*\*")
LABEL_LINE_RE = re.compile(r"^([A-Za-z][A-Za-z ]{1,40}?):")

COMMAND_EXTENSIONS = (".py", ".sh")


@dataclass(frozen=True)
class Finding:
    rule: str
    location: str  # "path:line" or "path (metadata.commands)"
    detail: str


def finding_key(f: Finding) -> str:
    return f"{f.rule}|{f.location}|{f.detail}"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint the .agents/skills instruction graph.")
    parser.add_argument("--repo-root", default="", help="Repository root override.")
    return parser.parse_args(argv)


def repo_root_from_args(explicit_root: str) -> Path:
    return Path(explicit_root).resolve() if explicit_root else Path.cwd()


def is_placeholder(token: str) -> bool:
    if any(c in token for c in PLACEHOLDER_CHARS):
        return True
    return bool(N_STYLE_RE.search(token))


def looks_like_checkable_path(token: str) -> bool:
    if is_placeholder(token) or not EXTENSION_RE.search(token):
        return False
    if token in ROOT_FILES:
        return True
    return token.startswith(PATH_PREFIXES)


def resolve_path(token: str, skill_dir: Path, repo_root: Path) -> Path | None:
    skill_rel = skill_dir / token
    if skill_rel.is_file():
        return skill_rel
    repo_rel = repo_root / token
    if repo_rel.is_file():
        return repo_rel
    return None


def fence_mask(lines: list[str]) -> list[bool]:
    """Per-line: True when the line is a fence delimiter or inside a fenced block."""
    in_fence = False
    mask: list[bool] = []
    for line in lines:
        if FENCE_RE.match(line):
            mask.append(True)
            in_fence = not in_fence
            continue
        mask.append(in_fence)
    return mask


def discover_skills(skills_dir: Path) -> dict[str, Path]:
    return {p.parent.name: p for p in sorted(skills_dir.glob("*/SKILL.md"))}


def owned_md_files(skill_md: Path, tiers: dict[str, list[str]]) -> list[Path]:
    files = [skill_md]
    for field in TIER_FIELDS:
        for rel in tiers.get(field, []):
            if rel.endswith(".md"):
                candidate = skill_md.parent / rel
                if candidate.is_file():
                    files.append(candidate)
    return files


def scan_skill_refs(lines: list[str], mask: list[bool], known: set[str], location: str) -> list[Finding]:
    findings: list[Finding] = []
    for i, line in enumerate(lines):
        if mask[i]:
            continue
        for m in DOLLAR_SKILL_RE.finditer(line):
            if m.group(1) not in known:
                findings.append(Finding("dangling-skill-ref", f"{location}:{i + 1}", "$" + m.group(1)))
        for m in SLASH_SKILL_RE.finditer(line):
            if m.group(1) not in known:
                findings.append(Finding("dangling-skill-ref", f"{location}:{i + 1}", "/" + m.group(1)))
    return findings


def scan_path_refs(
    lines: list[str], mask: list[bool], skill_dir: Path, repo_root: Path, location: str
) -> list[Finding]:
    findings: list[Finding] = []
    for i, line in enumerate(lines):
        if mask[i]:
            continue
        for m in BACKTICK_RE.finditer(line):
            token = m.group(1)
            if not looks_like_checkable_path(token):
                continue
            if resolve_path(token, skill_dir, repo_root) is None:
                findings.append(Finding("dangling-path", f"{location}:{i + 1}", token))
    return findings


def parse_anchor_at(line: str, at: int) -> tuple[str, int, str] | None:
    """`line[at] == '§'`. Return (anchor_text, end_index, kind)."""
    pos = at + 1
    m = NUMERIC_ANCHOR_RE.match(line, pos)
    if m:
        end = m.end()
        range_m = re.match(r"-§(\d+[a-zA-Z]?(?:\.\d+)?)", line[end:])
        if range_m:
            return (m.group(0), end + range_m.end(), "range:" + range_m.group(1))
        return (m.group(0), end, "numeric")
    stop = WORD_STOP_RE.search(line, pos)
    word_end = stop.start() if stop else len(line)
    word = line[pos:word_end].strip()
    return (word, word_end, "word") if word else None


def nearest_preceding_token(line: str, backticks: list[tuple[int, int, str]], pos: int) -> str | None:
    best: tuple[str, int] | None = None
    for start, end, token in backticks:
        if end <= pos and BETWEEN_OK_RE.match(line[end:pos]) and (best is None or end > best[1]):
            best = (token, end)
    return best[0] if best else None


def resolve_anchor_targets(
    token: str, skill_dir: Path, repo_root: Path, owned_by_skill: dict[str, list[Path]]
) -> list[Path] | None:
    bare = token[1:] if token.startswith("$") else token
    if "/" not in bare and not EXTENSION_RE.search(bare) and bare in owned_by_skill:
        return owned_by_skill[bare]
    if looks_like_checkable_path(token):
        resolved = resolve_path(token, skill_dir, repo_root)
        return [resolved] if resolved else None
    return None


def heading_ids(text: str) -> set[str]:
    ids: set[str] = set()
    for line in text.splitlines():
        m = HEADING_RE.match(line)
        if not m:
            continue
        rest = m.group(2).strip()
        if rest.startswith("§"):
            rest = rest[1:]
        token = rest.split(None, 1)[0] if rest else ""
        token = token.rstrip(").:")
        if token:
            ids.add(token.lower())
    return ids


def marker_phrases(text: str) -> list[str]:
    phrases: list[str] = []
    for line in text.splitlines():
        m = HEADING_RE.match(line)
        if m:
            phrases.append(m.group(2).strip().lstrip("§").strip())
            continue
        stripped = line.strip()
        m = BOLD_LINE_RE.match(stripped)
        if m:
            phrases.append(m.group(1).strip())
            continue
        m = LABEL_LINE_RE.match(stripped)
        if m:
            phrases.append(m.group(1).strip())
    return phrases


def anchor_resolves(anchor: str, targets: list[Path]) -> bool:
    ids: set[str] = set()
    phrases: list[str] = []
    for path in targets:
        text = path.read_text(encoding="utf-8", errors="replace")
        ids |= heading_ids(text)
        phrases += marker_phrases(text)
    if NUMERIC_ANCHOR_RE.fullmatch(anchor):
        return anchor.lower() in ids
    needle = anchor.strip().lower()
    return any(needle in phrase.lower() for phrase in phrases)


def scan_anchor_refs(
    lines: list[str],
    mask: list[bool],
    skill_dir: Path,
    repo_root: Path,
    owned_by_skill: dict[str, list[Path]],
    location: str,
) -> list[Finding]:
    findings: list[Finding] = []
    for i, line in enumerate(lines):
        if mask[i]:
            continue
        backticks = [(m.start(), m.end(), m.group(1)) for m in BACKTICK_RE.finditer(line)]
        pos = 0
        while True:
            idx = line.find("§", pos)
            if idx == -1:
                break
            parsed = parse_anchor_at(line, idx)
            if parsed is None:
                pos = idx + 1
                continue
            anchor_text, end, kind = parsed
            pos = end
            token = nearest_preceding_token(line, backticks, idx)
            if token is None:
                continue
            targets = resolve_anchor_targets(token, skill_dir, repo_root, owned_by_skill)
            if targets is None:
                continue
            if kind.startswith("range:"):
                ok = anchor_resolves(anchor_text, targets) and anchor_resolves(kind.split(":", 1)[1], targets)
            else:
                ok = anchor_resolves(anchor_text, targets)
            if not ok:
                findings.append(Finding("dangling-anchor", f"{location}:{i + 1}", f"{token} §{anchor_text}"))
    return findings


def check_commands(skill_md: Path, tiers: dict[str, list[str]], location: str) -> list[Finding]:
    findings: list[Finding] = []
    for rel in tiers.get("commands", []):
        candidate = skill_md.parent / rel
        if not candidate.is_file() or candidate.suffix not in COMMAND_EXTENSIONS:
            findings.append(Finding("bad-command", location, rel))
    return findings


def load_baseline(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    return {f"{e['rule']}|{e['location']}|{e['detail']}" for e in data.get("baseline", [])}


def collect_findings(repo_root: Path) -> list[Finding]:
    skills_dir = repo_root / SKILLS_DIR
    skill_map = discover_skills(skills_dir)
    known_names = set(skill_map)

    tiers_by_skill: dict[str, dict[str, list[str]]] = {}
    owned_by_skill: dict[str, list[Path]] = {}
    for name, skill_md in skill_map.items():
        frontmatter, _body = split_frontmatter(skill_md.read_text(encoding="utf-8"), skill_md)
        tiers = parse_tier_lists(frontmatter)
        tiers_by_skill[name] = tiers
        owned_by_skill[name] = owned_md_files(skill_md, tiers)

    findings: list[Finding] = []
    for name, skill_md in skill_map.items():
        skill_dir = skill_md.parent
        for md_file in owned_by_skill[name]:
            lines = md_file.read_text(encoding="utf-8", errors="replace").splitlines()
            mask = fence_mask(lines)
            location = md_file.relative_to(repo_root).as_posix()
            findings += scan_skill_refs(lines, mask, known_names, location)
            findings += scan_path_refs(lines, mask, skill_dir, repo_root, location)
            findings += scan_anchor_refs(lines, mask, skill_dir, repo_root, owned_by_skill, location)
        findings += check_commands(
            skill_md, tiers_by_skill[name], f"{skill_md.relative_to(repo_root).as_posix()} (metadata.commands)"
        )
    return findings


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = repo_root_from_args(args.repo_root)

    findings = collect_findings(repo_root)
    baseline = load_baseline(repo_root / BASELINE_PATH)
    new_findings = [f for f in findings if finding_key(f) not in baseline]
    baselined = len(findings) - len(new_findings)

    for f in new_findings:
        print(f"FINDING {f.rule} {f.location}: {f.detail}")
    if new_findings:
        print(f"instruction-graph: {len(new_findings)} new finding(s), {baselined} baselined")
    else:
        print(f"instruction-graph: pass ({baselined} baselined)")
    return 1 if new_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

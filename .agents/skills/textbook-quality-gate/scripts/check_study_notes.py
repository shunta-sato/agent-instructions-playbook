#!/usr/bin/env python3
"""Deterministic, privacy-safe checks for generic study-note packs."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TEXTBOOK_HEADINGS = (
    "why it matters",
    "when to use",
    "inputs",
    "outputs",
    "failure",
    "next reader action",
    "links",
)
WIKILINK_RE = re.compile(r"\[\[([^\[\]\n]+)\]\]")
TAG_RE = re.compile(r"(?<!\w)#([A-Za-z0-9_/-]+)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check generic study-note Markdown roots without printing note contents."
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=("textbook-full-gate", "shared-mechanical-only"),
        help="Gate mode to run.",
    )
    parser.add_argument("note_roots", nargs="+", help="One or more note roots to scan.")
    return parser.parse_args()


def rel(path: Path, base: Path) -> str:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return path.name


def discover_markdown(roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        if root.is_file() and root.suffix.lower() in {".md", ".markdown"}:
            files.append(root)
        elif root.is_dir():
            files.extend(
                p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".markdown"}
            )
    return sorted(set(files))


def build_targets(files: list[Path]) -> set[str]:
    targets: set[str] = set()
    for path in files:
        stem = path.stem.casefold()
        targets.add(stem)
        targets.add(path.with_suffix("").as_posix().casefold())
        targets.add(path.as_posix().casefold())
    return targets


def target_candidates(raw: str) -> list[str]:
    target = raw.split("|", 1)[0].split("#", 1)[0].strip()
    if not target:
        return []
    lowered = target.casefold()
    candidates = [lowered]
    if lowered.endswith(".md"):
        candidates.append(lowered[:-3])
    else:
        candidates.append(f"{lowered}.md")
    candidates.append(Path(lowered).name)
    return candidates


def check_frontmatter(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return "frontmatter opening delimiter has no closing delimiter"
    return None


def check_wikilinks(text: str) -> list[str]:
    problems: list[str] = []
    if text.count("[[") != text.count("]]"):
        problems.append("unbalanced wikilink delimiters")
    for match in WIKILINK_RE.finditer(text):
        if not match.group(1).strip():
            problems.append("empty wikilink target")
    return problems


def has_required_textbook_shape(text: str) -> bool:
    lowered = text.casefold()
    hits = sum(1 for heading in TEXTBOOK_HEADINGS if heading in lowered)
    return hits >= 4


def is_too_thin(text: str) -> bool:
    non_empty = [line for line in text.splitlines() if line.strip()]
    words = re.findall(r"\b\w+\b", text)
    return len(non_empty) < 8 or len(words) < 120


def scan_file(path: Path, base: Path, mode: str, targets: set[str]) -> list[str]:
    display = rel(path, base)
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [f"{display}: file is not valid UTF-8 text"]

    problems: list[str] = []
    if "�" in text:
        problems.append(f"{display}: Unicode replacement-character corruption detected")
    if "\x00" in text:
        problems.append(f"{display}: possible binary or corruption artifact detected")

    frontmatter_problem = check_frontmatter(text)
    if frontmatter_problem:
        problems.append(f"{display}: {frontmatter_problem}")

    problems.extend(f"{display}: {problem}" for problem in check_wikilinks(text))

    for match in WIKILINK_RE.finditer(text):
        candidates = target_candidates(match.group(1))
        if candidates and not any(candidate in targets for candidate in candidates):
            problems.append(f"{display}: unresolved wikilink target")

    has_pack_convention = text.startswith("---\n") or "tags:" in text or TAG_RE.search(text)
    if has_pack_convention and not ("tags:" in text or TAG_RE.search(text)):
        problems.append(f"{display}: pack convention appears to require tags but none were found")

    if mode == "textbook-full-gate":
        if is_too_thin(text):
            problems.append(f"{display}: note appears too thin for textbook learning use")
        if not has_required_textbook_shape(text):
            problems.append(f"{display}: missing detectable textbook learning sections")

    return problems


def main() -> int:
    args = parse_args()
    roots = [Path(root) for root in args.note_roots]
    missing = [root for root in roots if not root.exists()]
    if missing:
        for root in missing:
            print(f"ERROR: note root does not exist: {root.name}")
        return 2

    files = discover_markdown(roots)
    if not files:
        print("FAIL: no Markdown files discovered under provided roots")
        return 1

    common_base = Path.cwd().resolve()
    targets = build_targets(files)
    problems: list[str] = []
    for path in files:
        problems.extend(scan_file(path, common_base, args.mode, targets))

    print(f"Mode: {args.mode}")
    print(f"Markdown files checked: {len(files)}")
    if problems:
        print("Result: fail")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("Result: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

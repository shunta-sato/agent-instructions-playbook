#!/usr/bin/env python3
"""Deterministic, privacy-safe checks for generic study-note packs."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

TEXTBOOK_SECTION_ALIASES = (
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


@dataclass(frozen=True)
class NoteFile:
    path: Path
    text: str


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
    parser.add_argument(
        "--require-tags",
        action="store_true",
        help="Fail notes without tags. By default, frontmatter alone does not imply tags are required.",
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
                p
                for p in root.rglob("*")
                if p.is_file() and p.suffix.lower() in {".md", ".markdown"}
            )
    return sorted(set(files))


def load_notes(files: list[Path], base: Path) -> tuple[list[NoteFile], list[str]]:
    notes: list[NoteFile] = []
    problems: list[str] = []
    for path in files:
        display = rel(path, base)
        try:
            notes.append(NoteFile(path=path, text=path.read_text(encoding="utf-8")))
        except UnicodeDecodeError:
            problems.append(f"{display}: file is not valid UTF-8 text")
    return notes, problems


def build_targets(files: list[Path], roots: list[Path]) -> set[str]:
    targets: set[str] = set()
    resolved_roots = [root.resolve() for root in roots]
    for path in files:
        resolved = path.resolve()
        targets.add(path.stem.casefold())
        targets.add(path.name.casefold())

        for root in resolved_roots:
            if root.is_file():
                root = root.parent
            try:
                root_relative = resolved.relative_to(root)
            except ValueError:
                continue

            without_suffix = root_relative.with_suffix("").as_posix().casefold()
            with_suffix = root_relative.as_posix().casefold()
            targets.add(without_suffix)
            targets.add(with_suffix)
            targets.add(root_relative.name.casefold())
            targets.add(Path(without_suffix).name.casefold())
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
    if not Path(lowered).name.endswith(".md"):
        candidates.append(f"{Path(lowered).name}.md")
    return candidates


def check_frontmatter(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return "frontmatter opening delimiter has no closing delimiter"
    return None


def has_tags(text: str) -> bool:
    return "tags:" in text or TAG_RE.search(text) is not None


def check_wikilinks(text: str) -> list[str]:
    problems: list[str] = []
    if text.count("[[") != text.count("]]"):
        problems.append("unbalanced wikilink delimiters")
    for match in WIKILINK_RE.finditer(text):
        if not match.group(1).strip():
            problems.append("empty wikilink target")
    return problems


def detectable_textbook_sections(text: str) -> int:
    lowered = text.casefold()
    return sum(1 for heading in TEXTBOOK_SECTION_ALIASES if heading in lowered)


def is_too_thin(text: str) -> bool:
    non_empty = [line for line in text.splitlines() if line.strip()]
    words = re.findall(r"\b\w+\b", text)
    return len(words) < 80 or (len(words) < 120 and len(non_empty) < 4)


def scan_file(
    note: NoteFile,
    base: Path,
    mode: str,
    targets: set[str],
    require_tags: bool,
    pack_uses_tags: bool,
) -> tuple[list[str], list[str]]:
    path = note.path
    text = note.text
    display = rel(path, base)

    problems: list[str] = []
    warnings: list[str] = []
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

    note_has_tags = has_tags(text)
    if require_tags and not note_has_tags:
        problems.append(f"{display}: tags are required by --require-tags but none were found")
    elif pack_uses_tags and not note_has_tags:
        warnings.append(f"{display}: pack uses tags elsewhere but this note has none")

    if mode == "textbook-full-gate":
        if is_too_thin(text):
            problems.append(f"{display}: note appears too thin for textbook learning use")
        if detectable_textbook_sections(text) < 4:
            warnings.append(
                f"{display}: textbook learning sections were not mechanically detected; "
                "confirm semantic coverage with textbook-learning-content-review"
            )

    return problems, warnings


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
    notes, load_problems = load_notes(files, common_base)
    targets = build_targets(files, roots)
    pack_uses_tags = any(has_tags(note.text) for note in notes)
    problems: list[str] = list(load_problems)
    warnings: list[str] = []
    for note in notes:
        note_problems, note_warnings = scan_file(
            note,
            common_base,
            args.mode,
            targets,
            args.require_tags,
            pack_uses_tags,
        )
        problems.extend(note_problems)
        warnings.extend(note_warnings)

    print(f"Mode: {args.mode}")
    print(f"Markdown files checked: {len(files)}")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")
    if problems:
        print("Result: fail")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("Result: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

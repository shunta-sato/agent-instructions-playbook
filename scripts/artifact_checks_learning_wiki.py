#!/usr/bin/env python3
"""LLM Wiki artifact checks (`.agent/wiki`) -- the second artifact shape
under the `learning` checker name; split out of `artifact_checks_learning`
to stay inside the structure budget (see that module's docstring for why
the split is a clean boundary rather than a line-count dodge).

Shared checker signature (pinned; identical to the sibling module and to
`artifact_checks_docs` / `artifact_checks_packs`)::

    run_checks(repo_root, artifact_path, spec, registry) -> list[str]

`artifact_path` is the `.agent/wiki` directory itself (registry kind
`detect_dir: ".agent/wiki"`), so the pinned signature fits this shape
without adjustment. `required_files` / `forbid_fill_sentinel` /
`forbid_symlinks` are reused by IMPORTING the private check functions from
`artifact_checks_packs` (dual-path import below), never copied.

This checker judges STRUCTURE only (file presence, heading presence, fixed
metadata-field presence/shape, link resolution) -- never whether the
knowledge recorded in an entry is actually true or well-scoped.

## Finding-id scheme (namespace `wiki:`)

- `wiki:missing-file:<rel>` / `wiki:fill-sentinel:<rel>` /
  `wiki:symlink-in-pack:<rel>` -- re-prefixed pack-generic findings.
- `wiki:heading:<file>:<heading>` -- an entry (any `*.md` other than
  `README.md`/`index.md`) is missing one of the nine required `## `
  headings from spec section 7.
- `wiki:missing-field:<file>:<field>` -- one of the four fixed fields
  (`status` | `confidence` | `last-verified` | `revisit-when`) has no
  matching `Field: value` line anywhere in the entry, or (for
  `revisit-when`) the line is present with an empty value.
- `wiki:invalid-value:<file>:<field>` -- the field line is present but its
  value fails validation (`status` not in the enum, `confidence` not in the
  enum, `last-verified` not `YYYY-MM-DD` shaped).
- `wiki:orphan:<file>` -- an entry is never linked from `index.md`.
- `wiki:duplicate-link:<target>` -- `index.md` links to the same relative
  target more than once (spec section 7: "orphan entries, dead links, and
  duplicate links are lint findings").
- `wiki:dead-link:<file>:<href>` -- a relative link in `index.md` does not
  resolve under the wiki directory; this also covers an absolute or `..`
  href (a link that could never resolve inside the wiki directory is dead
  by construction, so no separate traversal-id namespace is introduced).
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

try:
    from scripts.artifact_checks_packs import (
        _check_forbid_fill_sentinel,
        _check_forbid_symlinks,
        _check_required_files,
    )
except ImportError:  # pragma: no cover - direct execution without repo root on sys.path
    from artifact_checks_packs import (  # type: ignore[no-redef]
        _check_forbid_fill_sentinel,
        _check_forbid_symlinks,
        _check_required_files,
    )

WIKI_REQUIRED_HEADINGS = [
    "Scope",
    "Project knowledge",
    "Applies when",
    "Does not apply when",
    "Operational consequence",
    "Evidence",
    "Confidence",
    "Freshness",
    "Promoted learning",
]
INFRA_FILENAMES = {"README.md", "index.md"}

STATUS_ENUM = {"active", "superseded", "expired"}
CONFIDENCE_ENUM = {"confirmed", "plausible", "unknown"}
LAST_VERIFIED_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

HEADING_LINE_RE = re.compile(r"^#{1,6}[ \t]+(.*?)[ \t]*$", re.MULTILINE)
STATUS_LINE_RE = re.compile(r"(?m)^Status:[ \t]*(.*?)[ \t]*$")
CONFIDENCE_LINE_RE = re.compile(r"(?m)^Confidence:[ \t]*(.*?)[ \t]*$")
LAST_VERIFIED_LINE_RE = re.compile(r"(?m)^Last verified:[ \t]*(.*?)[ \t]*$")
REVISIT_WHEN_LINE_RE = re.compile(r"(?m)^Revisit when:[ \t]*(.*?)[ \t]*$")
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def _check_entry(entry: Path, wiki_root: Path) -> list[str]:
    findings = []
    text = _read_text(entry) or ""
    name = entry.relative_to(wiki_root).as_posix()

    present_headings = {m.strip() for m in HEADING_LINE_RE.findall(text)}
    findings += [
        f"wiki:heading:{name}:{heading}"
        for heading in WIKI_REQUIRED_HEADINGS
        if heading not in present_headings
    ]

    status_match = STATUS_LINE_RE.search(text)
    if not status_match or not status_match.group(1):
        findings.append(f"wiki:missing-field:{name}:status")
    elif status_match.group(1) not in STATUS_ENUM:
        findings.append(f"wiki:invalid-value:{name}:status")

    confidence_match = CONFIDENCE_LINE_RE.search(text)
    if not confidence_match or not confidence_match.group(1):
        findings.append(f"wiki:missing-field:{name}:confidence")
    elif confidence_match.group(1) not in CONFIDENCE_ENUM:
        findings.append(f"wiki:invalid-value:{name}:confidence")

    lv_match = LAST_VERIFIED_LINE_RE.search(text)
    if not lv_match or not lv_match.group(1):
        findings.append(f"wiki:missing-field:{name}:last-verified")
    elif not LAST_VERIFIED_RE.match(lv_match.group(1)):
        findings.append(f"wiki:invalid-value:{name}:last-verified")

    revisit_match = REVISIT_WHEN_LINE_RE.search(text)
    if not revisit_match or not revisit_match.group(1):
        findings.append(f"wiki:missing-field:{name}:revisit-when")

    return findings


def _normalize_href(href: str) -> str:
    target = href.split("#", 1)[0].strip()
    if target.startswith("./"):
        target = target[2:]
    return target


def _check_orphans_and_duplicates(
    entries: list[Path], index_text: str, wiki_root: Path
) -> list[str]:
    targets = [_normalize_href(href) for href in MD_LINK_RE.findall(index_text)]
    linked = set(targets)
    findings = [
        f"wiki:orphan:{entry.relative_to(wiki_root).as_posix()}"
        for entry in entries
        if entry.relative_to(wiki_root).as_posix() not in linked
    ]

    counts = Counter(t for t in targets if t)
    findings += [f"wiki:duplicate-link:{target}" for target, n in sorted(counts.items()) if n > 1]
    return findings


def _check_dead_links(artifact_path: Path, index_name: str, index_text: str) -> list[str]:
    findings = []
    for href in MD_LINK_RE.findall(index_text):
        target = _normalize_href(href)
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        if target.startswith("/") or any(seg == ".." for seg in target.split("/")):
            findings.append(f"wiki:dead-link:{index_name}:{href}")
            continue
        if not (artifact_path / target).exists():
            findings.append(f"wiki:dead-link:{index_name}:{href}")
    return findings


def run_checks(repo_root: Path, artifact_path: Path, spec: dict, registry: dict) -> list[str]:
    del repo_root, registry  # unused by wiki checks; kept for the shared signature
    findings: list[str] = []
    findings += [f"wiki:{f}" for f in _check_required_files(artifact_path, spec)]
    findings += [f"wiki:{f}" for f in _check_forbid_fill_sentinel(artifact_path, spec)]
    findings += [f"wiki:{f}" for f in _check_forbid_symlinks(artifact_path, spec)]

    index_path = artifact_path / "index.md"
    if not index_path.is_file():
        return findings  # already reported by required_files above

    entries = sorted(
        p for p in sorted(artifact_path.rglob("*.md")) if p.is_file() and p.name not in INFRA_FILENAMES
    )
    for entry in entries:
        findings += _check_entry(entry, artifact_path)

    index_text = _read_text(index_path) or ""
    findings += _check_orphans_and_duplicates(entries, index_text, artifact_path)
    findings += _check_dead_links(artifact_path, index_path.name, index_text)

    return findings

#!/usr/bin/env python3
"""Docs-family artifact checkers: heading-based structural checks for
Markdown artifacts (bug reports, workflow-contract reviews, ExecPlans).

Two heading modes, selected by an artifact kind's ``heading_mode`` field in
``.agents/artifact-registry.json``:

- ``exact``: every ``spec["required_headings"]`` entry must appear as a
  markdown heading line, any ``#``-level, matched on the exact text after
  the hashes and the following whitespace. Finding id:
  ``missing-heading:<heading>``.
- ``keyword-sections``: the file's H1 (first ``# `` line) selects one of two
  section-keyword sets. If it contains ``spec["design_record_title_marker"]``
  case-insensitively, the required groups are
  ``spec["design_record_required_section_keywords"]``; otherwise
  ``spec["required_section_keywords"]``. Each group is a list of alternative
  keywords, satisfied when any ``## ``-level heading contains any
  alternative, case-insensitively. Finding id:
  ``missing-section:<first-keyword-of-group>``. For the design-record
  contract, a matched section must also have body content
  (``empty-section:<first-keyword-of-group>``).

Fenced code blocks are blanked before matching in both modes.

Both return stable, line-number-independent finding ids so the baseline
ratchet in ``lint_artifacts`` survives content churn (reordering headings or
editing prose under them does not change a finding id).

Shared checker signature (pinned; ``scripts/artifact_checks_packs.py``
implements the same):
``run_checks(repo_root, artifact_path, spec, registry) -> list[str]``.
"""

from __future__ import annotations

import re
from pathlib import Path

# Any-level heading: 1-6 hashes, required whitespace, exact text captured
# with surrounding whitespace stripped.
HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.*?)[ \t]*$")
# H1 requires exactly one hash (the second character must be whitespace, so
# "##..." lines never match).
H1_RE = re.compile(r"^#[ \t]+(.*?)[ \t]*$")
# H2 requires exactly two hashes (the third character must be whitespace, so
# "###..." lines never match).
H2_RE = re.compile(r"^##[ \t]+(.*?)[ \t]*$")


# Fenced-code-block delimiter (``` or ~~~, optionally indented/info-stringed).
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def _read_lines(artifact_path: Path) -> list[str]:
    """File lines with fenced-code-block contents blanked, so a heading
    inside a ``` block can never satisfy a structural requirement."""
    lines = artifact_path.read_text(encoding="utf-8", errors="replace").splitlines()
    stripped: list[str] = []
    in_fence = False
    for line in lines:
        if FENCE_RE.match(line):
            in_fence = not in_fence
            stripped.append("")
            continue
        stripped.append("" if in_fence else line)
    return stripped


def _heading_texts(lines: list[str]) -> set[str]:
    """Exact text of every heading line, any level."""
    texts: set[str] = set()
    for line in lines:
        match = HEADING_RE.match(line)
        if match:
            texts.add(match.group(2))
    return texts


def check_exact_headings(lines: list[str], required_headings: list[str]) -> list[str]:
    present = _heading_texts(lines)
    return [
        f"missing-heading:{heading}"
        for heading in required_headings
        if heading not in present
    ]


def _first_h1(lines: list[str]) -> str | None:
    for line in lines:
        match = H1_RE.match(line)
        if match:
            return match.group(1)
    return None


def _h2_headings_lower(lines: list[str]) -> list[str]:
    texts = []
    for line in lines:
        match = H2_RE.match(line)
        if match:
            texts.append(match.group(1).lower())
    return texts


def _h2_sections(lines: list[str]) -> list[tuple[str, bool]]:
    """(lowercased H2 text, section has at least one non-blank non-heading
    body line before the next heading of any level)."""
    sections: list[tuple[str, bool]] = []
    current: str | None = None
    has_body = False
    for line in lines:
        if HEADING_RE.match(line):
            if current is not None:
                sections.append((current, has_body))
            h2 = H2_RE.match(line)
            current = h2.group(1).lower() if h2 else None
            has_body = False
            continue
        if current is not None and line.strip():
            has_body = True
    if current is not None:
        sections.append((current, has_body))
    return sections


def check_keyword_sections(lines: list[str], spec: dict) -> list[str]:
    h1 = _first_h1(lines) or ""
    marker = spec.get("design_record_title_marker", "")
    is_design_record = bool(marker) and marker.lower() in h1.lower()

    required_groups = (
        spec.get("design_record_required_section_keywords", [])
        if is_design_record
        else spec.get("required_section_keywords", [])
    )

    sections = _h2_sections(lines)
    findings: list[str] = []
    for group in required_groups:
        if not group:
            continue
        matching = [
            has_body
            for heading, has_body in sections
            if any(keyword.lower() in heading for keyword in group)
        ]
        if not matching:
            findings.append(f"missing-section:{group[0]}")
        # A design record's contract is so small that heading presence alone
        # proves nothing; each required section must also have body content.
        elif is_design_record and not any(matching):
            findings.append(f"empty-section:{group[0]}")
    return findings


def run_checks(
    repo_root: Path, artifact_path: Path, spec: dict, registry: dict
) -> list[str]:
    del repo_root, registry  # unused by docs checks; kept for the shared signature
    lines = _read_lines(artifact_path)
    mode = spec.get("heading_mode")
    if mode == "exact":
        return check_exact_headings(lines, spec.get("required_headings", []))
    if mode == "keyword-sections":
        return check_keyword_sections(lines, spec)
    return [f"unknown-heading-mode:{mode}"]

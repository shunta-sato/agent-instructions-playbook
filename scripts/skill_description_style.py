"""Shared style checks for Agent Skill frontmatter descriptions."""

from __future__ import annotations

import re


DESCRIPTION_RECOMMENDED_MAX_CHARS = 420
DESCRIPTION_STYLE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ordered-then", re.compile(r"\bthen\b", re.IGNORECASE)),
    ("body-reference", re.compile(r"\bAlways\s+(?:open|read)\b", re.IGNORECASE)),
    (
        "procedure-verb",
        re.compile(
            r"\b(?:classify|execute|hand\s+off|create\s+and\s+maintain|"
            r"produce|produces|return|returns|run|make\s+a\s+Test\s+List|"
            r"update\s+the\s+list)\b",
            re.IGNORECASE,
        ),
    ),
)


def description_trigger_only_flags(description: str) -> list[str]:
    flags: list[str] = []
    if len(description) > DESCRIPTION_RECOMMENDED_MAX_CHARS:
        flags.append(f"long-description:{len(description)}")

    for label, pattern in DESCRIPTION_STYLE_PATTERNS:
        if pattern.search(description):
            flags.append(label)

    return flags

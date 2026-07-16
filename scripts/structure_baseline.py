#!/usr/bin/env python3
"""Structure-debt baseline schema, validation, and reconciliation.

This module owns the *optional* structure-debt baseline: a file a repository
may provide to record pre-existing structure-budget findings so they do not
block every future change. It is independent of ``git`` history, file
mtimes, filename ordering, and network access — reconciliation depends only
on the current on-disk file shape (``Finding`` objects from
``structure_rules.py``), the current baseline document, and which files this
invocation actually scanned.

The baseline is a **ratchet, not a waiver**:

- An entry suppresses only the *exact* current finding (same rule, path,
  value, and canonical limit) as non-blocking ``accepted_debt``.
- A regression (worse value) or a stale/looser-than-current entry (file
  improved, or no longer breaches the rule) fails closed instead of
  silently accepting the old, larger debt — but staleness from "no longer
  breaches the rule" is only detectable for entries whose file was part of
  this invocation's scanned scope; an entry for a file outside that scope
  (e.g. an untouched file on a partial, explicit-paths run) is left neutral
  rather than guessed at. A full default scan's scope is every git-tracked
  source file, so it still detects every stale entry in the repository.
- Duplicate entries, missing/non-source paths, threshold mismatches,
  malformed schema, and out-of-repo paths (see ``structure_paths.py``) are
  baseline-document defects, not scan-scope questions: they are checked
  against every entry regardless of whether that entry's file was scanned
  this invocation, so they fail closed on every run, partial or full, and
  are never left neutral the way scanned-scope staleness can be.
- This module never writes or rewrites the baseline file; authoring and
  refreshing entries is always a maintainer decision.

Schema (version 1): ``{"version": 1, "entries": [{"rule": "source-file-lines",
"path": "src/x.rs", "value": 500, "limit": 400}]}``.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

# ``structure_rules``/``structure_paths`` are sibling modules in this
# directory. Whether this file is imported as ``scripts.structure_baseline``
# (package-qualified, as tests do) or run directly as a script determines
# which import form resolves them; branching on ``__package__`` is explicit
# and deterministic, unlike a try/except import guess.
if __package__:
    from scripts.structure_paths import normalize_entry_path, path_escape
    from scripts.structure_rules import Finding, SOURCE_EXTENSIONS
else:
    from structure_paths import normalize_entry_path, path_escape
    from structure_rules import Finding, SOURCE_EXTENSIONS

DEFAULT_BASELINE_PATH = ".agents/structure-baseline.json"
BASELINE_SCHEMA_VERSION = 1
KNOWN_RULES = {"source-file-lines", "entrypoint-logic-lines", "inline-test-lines"}
BASELINE_TOP_KEYS = {"version", "entries"}
BASELINE_ENTRY_KEYS = {"rule", "path", "value", "limit"}
RULE_LIMIT_ARG = {
    "source-file-lines": "max_source_lines",
    "entrypoint-logic-lines": "max_entrypoint_lines",
    "inline-test-lines": "max_inline_test_lines",
}


@dataclass(frozen=True)
class BaselineEntry:
    """One accepted-debt record parsed from a baseline document."""

    rule: str
    path: str
    value: int
    limit: int


@dataclass(frozen=True)
class BaselineIssue:
    """A fail-closed baseline problem: schema, staleness, or regression."""

    kind: str
    rule: str
    path: str
    detail: str


def resolve_baseline_path(args: argparse.Namespace) -> tuple[Path | None, bool]:
    """Return ``(path, explicit)``; ``path`` is ``None`` when no baseline applies."""
    if args.baseline is not None:
        return Path(args.baseline), True
    default_path = Path.cwd() / DEFAULT_BASELINE_PATH
    return (default_path, False) if default_path.is_file() else (None, False)


def _issue(kind: str, detail: str, rule: str = "", path: str = "") -> BaselineIssue:
    """Build a ``BaselineIssue`` without repeating four keyword arguments
    per call site."""
    return BaselineIssue(kind=kind, rule=rule, path=path, detail=detail)


def _is_nonneg_int(value: object) -> bool:
    """Return whether ``value`` is a non-negative ``int`` (bools are rejected)."""
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _parse_baseline_entry(
    raw: object, index: int, disp: str
) -> tuple[BaselineEntry | None, BaselineIssue | None]:
    """Parse and schema-validate one raw baseline entry."""
    if not isinstance(raw, dict) or set(raw.keys()) != BASELINE_ENTRY_KEYS:
        return None, _issue(
            "malformed-schema",
            f"baseline {disp} entries[{index}]: must be an object with "
            f"exactly {sorted(BASELINE_ENTRY_KEYS)}",
        )

    rule, path, value, limit = (raw.get(k) for k in ("rule", "path", "value", "limit"))
    if (
        not isinstance(rule, str)
        or not isinstance(path, str)
        or not path
        or not _is_nonneg_int(value)
        or not _is_nonneg_int(limit)
    ):
        return None, _issue(
            "malformed-schema",
            f"baseline {disp} entries[{index}]: 'rule'/'path' must be non-empty "
            "strings, 'value'/'limit' non-negative integers",
        )

    path = normalize_entry_path(path)
    escape_detail = path_escape(path)
    if escape_detail is not None:
        return None, _issue(
            "path-escape",
            f"baseline {disp} entries[{index}]: {escape_detail}",
            rule,
            path,
        )

    if rule not in KNOWN_RULES:
        return None, _issue(
            "unknown-rule",
            f"baseline {disp} entries[{index}] uses unknown rule {rule!r}; "
            f"expected one of {sorted(KNOWN_RULES)}",
            rule,
            path,
        )

    return BaselineEntry(rule=rule, path=path, value=value, limit=limit), None


def _malformed(detail: str) -> tuple[list[BaselineEntry], list[BaselineIssue]]:
    """Build the ``([], [issue])`` shape every malformed-document return uses."""
    return [], [_issue("malformed-schema", detail)]


def load_baseline_entries(
    baseline_path: Path,
) -> tuple[list[BaselineEntry], list[BaselineIssue]]:
    """Read, JSON-parse, and schema-validate a baseline in one fail-closed pass."""
    disp = baseline_path.as_posix()
    try:
        document = json.loads(baseline_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return _malformed(f"cannot read baseline {disp}: {exc}")
    except json.JSONDecodeError as exc:
        return _malformed(f"baseline {disp} is not valid JSON: {exc}")

    if not isinstance(document, dict) or set(document.keys()) != BASELINE_TOP_KEYS:
        return _malformed(
            f"baseline {disp} must be a JSON object with exactly "
            f"{sorted(BASELINE_TOP_KEYS)}"
        )
    version = document.get("version")
    if not _is_nonneg_int(version) or version != BASELINE_SCHEMA_VERSION:
        return _malformed(
            f"baseline {disp} version must be {BASELINE_SCHEMA_VERSION}, "
            f"found {version!r}"
        )
    raw_entries = document.get("entries")
    if not isinstance(raw_entries, list):
        return _malformed(f"baseline {disp} 'entries' must be a list")

    entries: list[BaselineEntry] = []
    issues: list[BaselineIssue] = []
    for index, raw_entry in enumerate(raw_entries):
        entry, issue = _parse_baseline_entry(raw_entry, index, disp)
        if issue is not None:
            issues.append(issue)
        else:
            entries.append(entry)
    return entries, issues


def _entry_problem(
    entry: BaselineEntry, args: argparse.Namespace, disp: str
) -> BaselineIssue | None:
    """Return the blocking issue for ``entry``, or ``None`` if it is usable.

    Path confinement is already guaranteed by :func:`structure_paths.path_escape` at
    parse time, so ``entry.path`` here is always repo-relative and
    symlink-free.
    """
    source_path = Path.cwd() / entry.path
    if not source_path.is_file() or source_path.suffix not in SOURCE_EXTENSIONS:
        return _issue(
            "missing-path",
            f"baseline {disp} references {entry.path!r}, which is missing or "
            "not a recognized source file",
            entry.rule,
            entry.path,
        )

    canonical_limit = getattr(args, RULE_LIMIT_ARG[entry.rule])
    if entry.limit != canonical_limit:
        return _issue(
            "threshold-mismatch",
            f"baseline {disp} entry for {entry.rule!r} {entry.path!r} records "
            f"limit {entry.limit}, but the canonical limit now is "
            f"{canonical_limit}; refresh the baseline",
            entry.rule,
            entry.path,
        )
    return None


def validate_baseline_entries(
    entries: list[BaselineEntry], args: argparse.Namespace, baseline_path: Path
) -> tuple[list[BaselineEntry], list[BaselineIssue]]:
    """Drop (and report) duplicates, dangling paths, and threshold mismatches.

    Runs over every parsed entry unconditionally — these are document-level
    defects, not scan-scope questions, so they fail closed regardless of
    which files this invocation scanned. Only entries that pass every check
    here are passed on to :func:`reconcile_baseline` as usable.
    """
    disp = baseline_path.as_posix()
    counts: dict[tuple[str, str], int] = {}
    for entry in entries:
        key = (entry.rule, entry.path)
        counts[key] = counts.get(key, 0) + 1
    dupes = {key for key, count in counts.items() if count > 1}

    issues = [
        _issue(
            "duplicate-entry",
            f"baseline {disp} has duplicate entries for rule {r!r} path {p!r}; "
            "remove the duplicate so the intended value is unambiguous",
            r,
            p,
        )
        for r, p in sorted(dupes)
    ]

    usable: list[BaselineEntry] = []
    for entry in entries:
        if (entry.rule, entry.path) in dupes:
            continue
        problem = _entry_problem(entry, args, disp)
        if problem is not None:
            issues.append(problem)
        else:
            usable.append(entry)
    return usable, issues


def to_repo_relpath(display_path: str) -> str:
    """Normalize a display path to cwd-relative posix, for scope comparison.

    Default-scan findings carry absolute paths; explicit-CLI-path findings
    carry whatever was passed. Baseline entries are always cwd-relative, so
    both the finding-lookup key and the scanned-files scope set (built by
    ``check_structure.py`` from the same ``collect_files()`` result) need
    this same conversion. Used only for lookup/scope keys, never applied to
    ``Finding.path`` itself, so unbaselined output stays byte-for-byte
    unchanged.
    """
    path = Path(display_path)
    if path.is_absolute():
        try:
            return path.relative_to(Path.cwd()).as_posix()
        except ValueError:
            return path.as_posix()
    return path.as_posix()


def reconcile_baseline(
    findings: list[Finding],
    usable_entries: list[BaselineEntry],
    baseline_path: Path,
    scanned_paths: frozenset[str],
) -> tuple[list[Finding], list[Finding], list[BaselineIssue]]:
    """Split findings into blocking / accepted-debt and detect baseline drift.

    ``usable_entries`` have already passed :func:`validate_baseline_entries`
    (schema, duplicate, path, and threshold checks all passed unconditionally,
    regardless of scan scope), so the only remaining question this function
    answers is metric reconciliation: does a usable entry's recorded value
    still match reality, and — for that alone — was its file even part of
    this invocation's scope.

    ``scanned_paths`` is this invocation's scope: the cwd-relative posix
    paths of every file ``check_structure.py`` actually scanned (the full
    git-tracked default scan, or the explicit CLI paths). It matters because
    a baseline entry not reproduced by any finding is ambiguous on its own —
    either the file genuinely improved (stale, must fail closed per AC4), or
    the file simply was not part of *this* invocation's scope (neutral, not
    an error). Only the former can be told apart from the latter by checking
    scope, so an unmatched entry is judged stale only when its path is in
    ``scanned_paths``; a full default scan's scope is every tracked source
    file, so it still catches every stale entry in the repository.

    - Exact match (same value) -> accepted debt.
    - Finding worse than the recorded value -> regression (still blocking).
    - Finding better than the recorded value -> stale baseline (blocking;
      AC4: never overstate debt).
    - A scanned entry matching no finding at all -> stale baseline (the file
      no longer breaches the rule at all).
    - An unscanned entry matching no finding -> left neutral: not reported
      as an error, and not reported as accepted debt either.
    - No baseline entry for a finding -> ordinary blocking finding.
    """
    lookup = {(entry.rule, entry.path): entry for entry in usable_entries}
    matched: set[tuple[str, str]] = set()
    blocking: list[Finding] = []
    accepted: list[Finding] = []
    issues: list[BaselineIssue] = []
    disp = baseline_path.as_posix()

    for finding in findings:
        key = (finding.rule, to_repo_relpath(finding.path))
        entry = lookup.get(key)
        if entry is None:
            blocking.append(finding)
            continue

        matched.add(key)
        if finding.value == entry.value:
            accepted.append(finding)
        elif finding.value > entry.value:
            issues.append(
                _issue(
                    "regression",
                    f"{finding.path} regressed on {finding.rule}: now "
                    f"{finding.value}, baseline recorded {entry.value} — this "
                    "is a new regression, not accepted debt",
                    finding.rule,
                    finding.path,
                )
            )
        else:
            issues.append(
                _issue(
                    "stale-baseline",
                    f"{finding.path} improved on {finding.rule}: now "
                    f"{finding.value}, baseline still records the looser "
                    f"value {entry.value}; refresh the baseline entry to "
                    f"{finding.value} so accepted debt is never overstated",
                    finding.rule,
                    finding.path,
                )
            )

    for entry in usable_entries:
        if (entry.rule, entry.path) in matched or entry.path not in scanned_paths:
            continue
        issues.append(
            _issue(
                "stale-baseline",
                f"baseline {disp} entry for {entry.rule!r} {entry.path!r} "
                "no longer reproduces a finding (the file no longer "
                "breaches this rule); refresh or remove the baseline entry",
                entry.rule,
                entry.path,
            )
        )

    return blocking, accepted, issues

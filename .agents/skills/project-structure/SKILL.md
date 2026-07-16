---
name: project-structure
description: "Use when creating a new source file, module, crate, or package, when deciding where code or tests should live, or when a touched file exceeds the structure budget (scripts/check_structure.py). Gives forward-looking physical layout rules: entrypoint vs library split, module boundaries, and test placement. Use design-balance for responsibility layout across modules."
metadata:
  short-description: Physical code layout and structure budget
  requires:
    - references/project-structure-rust.md
---

## Purpose

Generative guidance for the **physical layout** of code: which file a piece of code or a test belongs in, when an entrypoint must delegate to a library, and when a file must be split.

This skill owns the canonical **structure budget**. It is state-based on purpose: it applies to what files look like now, not only to what a change proposes. Slow accretion (many small appends to one file) is exactly the failure it exists to stop.

`design-balance` decides *which unit owns a responsibility*; this skill decides *where units physically live and how large a file may grow*.

## When to use

Use this skill when:

- creating a new project, binary, crate, package, source file, or module
- deciding where new code or new tests should be placed
- the structure watch in `dev-workflow` or the structural exit check in `quality-gate` reports a finding
- an entrypoint file (`main.rs`, `src/bin/*.rs`, `main.py`, `__main__.py`, `main.go`, `main.c/cc/cpp`) is gaining logic or tests

## Structure budget (canonical)

Checked mechanically with `python scripts/check_structure.py <touched files>`:

| Rule | Limit | Required action on breach |
|---|---|---|
| `source-file-lines` | 400 total lines per source file | Split into modules; record the split via `design-balance` (module ownership) or `function-boundary-governor` (function moves). |
| `entrypoint-logic-lines` | 150 logic lines in an entrypoint file | Move domain logic into library modules (Rust: `lib.rs`). Entrypoints hold wiring only: argument parsing, config load, calls into the library, exit-code mapping. |
| `inline-test-lines` | 200 lines of Rust `#[cfg(test)]` blocks per file | Move tests to a sibling test module (`src/<area>/tests.rs`) or `tests/` integration tests. |

Budget breaches are findings, not advice: `quality-gate` treats an unresolved finding as `no-submit` unless an explicit bounded waiver (for example generated code) is recorded in the change brief.

## Structure-debt baseline (ratchet, not a waiver)

A repository may record pre-existing structure debt explicitly instead of re-litigating it on each change. This is **not** a waiver: it is a ratchet that can only tighten.

- Default path: `.agents/structure-baseline.json`; override with `check_structure.py --baseline PATH`.
- Schema v1: `{"version": 1, "entries": [{"rule", "path", "value", "limit"}, ...]}`. `rule` is one of the three canonical rules above; `path` is repo-root-relative and confined to the repo root (no absolute path, no `..` traversal, no symlink anywhere in the path chain); `value`/`limit` are the exact current line count and the *current canonical* limit.
- An entry suppresses only the **exact** current finding (same rule, path, value, and canonical limit) as non-blocking `accepted_debt`. It never suppresses a different value, a new rule, or a new file.
- Fails closed — still `no-submit` — on: a regression (file got worse), a stale/looser-than-current entry (file improved but the baseline still records the old, larger value — the entry must be refreshed to the new value or removed), a duplicate entry (path aliases like `x.py`/`./x.py` are normalized before this check), a missing or non-source `path`, a `limit` that no longer matches the canonical limit, an absolute/`..`/symlinked `path` (`path-escape` — a baseline can never accept debt for a file outside the repository or make debt depend on the checkout's filesystem), or any malformed schema.
- Scan scope affects exactly one question, and only for entries that already passed every other check: whether a *schema-valid, path-valid, canonical-limit-valid* entry's file was scanned this invocation — the only way to tell "genuinely stale" (file no longer breaches the rule) apart from "simply not examined this run". Every other check — duplicate entry, missing/non-source path, threshold mismatch, malformed schema, `path-escape` — is evaluated against the baseline document itself, not against scan scope, so those always fail closed on every invocation, partial or full, whether or not the entry's file was touched.
- Only a schema-valid, path-valid, canonical-limit-valid entry whose file is outside *this invocation's* scanned scope (the explicit files/dirs passed on the command line, or every git-tracked source file on the default no-args scan) is left neutral for that one staleness question — neither accepted debt nor an error — until a scan that includes it (notably the full default scan) runs; that full scan still catches every stale entry in the repository, so debt cannot go permanently undetected.
- Never depends on git history, mtimes, filename ordering, or network access.
- Maintainers own refreshing entries when a baselined file improves; the tool never auto-generates or silently rewrites the baseline.
- `accepted_debt` in `--json` output (or `ACCEPTED-DEBT` lines in text output) is reported separately from `findings`/`baseline_errors` and is never described as clean or passing — it is debt that must not worsen.

## How to use

1) Classify what is being created or touched: `entrypoint | library module | test code | config/build glue`.

2) Apply the language reference for placement rules. For Rust, open `references/project-structure-rust.md`.

3) Run `python scripts/check_structure.py` on the files you touched. If it reports findings, splitting is **required work in this change**, not a follow-up: route module ownership and naming to `$design-balance`, and function moves to `$function-boundary-governor`. A finding covered by an exact, still-current baseline entry (see below) reports as `accepted_debt`, not a blocking finding — but if you improve that file, refresh or remove its baseline entry in the same change so the debt is never overstated.

4) Record the layout decision: one line per created/split file with its role.

## Hard rules

- Entrypoint files never hold domain logic or accumulating test modules. A binary crate gets a `lib.rs` as soon as any domain logic exists.
- New tests are placed by convention (language reference), never appended to an entrypoint.
- A split required by the structure budget is complexity **placement**, not a new abstraction: it does not count against the `implementation-economy` complexity budget, and the smallest-safe-change principle does not exempt it.
- Do not invent deep speculative hierarchies to satisfy the budget; split along the responsibility seams `design-balance` names, one level at a time.

## Output expectation

Return:

- Layout decisions: `file → role (entrypoint | module | test)` for every created or split file.
- Structure budget result: `pass` or each finding with the applied fix or the recorded bounded waiver. If a `.agents/structure-baseline.json` (or `--baseline`) applies, also report `accepted_debt` count and any `baseline_errors` (never claim `accepted_debt` is clean).
- Which skills were routed to for split decisions (`design-balance`, `function-boundary-governor`), or `none`.

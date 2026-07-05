---
name: project-structure
description: "Use when creating a new source file, module, crate, or package, when deciding where code or tests should live, or when a touched file exceeds the structure budget (scripts/check_structure.py). Gives forward-looking physical layout rules: entrypoint vs library split, module boundaries, and test placement. Use design-balance for responsibility layout across modules."
metadata:
  short-description: Physical code layout and structure budget
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

## How to use

1) Classify what is being created or touched: `entrypoint | library module | test code | config/build glue`.

2) Apply the language reference for placement rules. For Rust, open `references/project-structure-rust.md`.

3) Run `python scripts/check_structure.py` on the files you touched. If it reports findings, splitting is **required work in this change**, not a follow-up: route module ownership and naming to `$design-balance`, and function moves to `$function-boundary-governor`.

4) Record the layout decision: one line per created/split file with its role.

## Hard rules

- Entrypoint files never hold domain logic or accumulating test modules. A binary crate gets a `lib.rs` as soon as any domain logic exists.
- New tests are placed by convention (language reference), never appended to an entrypoint.
- A split required by the structure budget is complexity **placement**, not a new abstraction: it does not count against the `implementation-economy` complexity budget, and the smallest-safe-change principle does not exempt it.
- Do not invent deep speculative hierarchies to satisfy the budget; split along the responsibility seams `design-balance` names, one level at a time.

## Output expectation

Return:

- Layout decisions: `file → role (entrypoint | module | test)` for every created or split file.
- Structure budget result: `pass` or each finding with the applied fix or the recorded bounded waiver.
- Which skills were routed to for split decisions (`design-balance`, `function-boundary-governor`), or `none`.

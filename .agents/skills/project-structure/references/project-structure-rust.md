# Rust project layout reference

Placement rules for Rust crates. Used by `$project-structure`.

## Binary crate layout

```
src/
  main.rs        # entrypoint: CLI arg parsing, config, calling the library, exit codes
  lib.rs         # public crate API; re-exports modules
  <area>.rs      # one module per domain area (parser.rs, stats.rs, output.rs, ...)
  <area>/        # directory module when an area grows: mod.rs + submodules
tests/
  <flow>.rs      # integration tests against the public API
```

Rules:

- `main.rs` holds **wiring only** (≤150 logic lines): parse arguments, load config, call `lib.rs` functions, map errors to exit codes. No domain types, no algorithms, no I/O parsing logic.
- Create `lib.rs` the moment any domain logic exists — even for a "small" CLI. `main.rs`-only is acceptable solely for a throwaway script with no tests.
- One module per domain area, named after the domain (`parser`, `stats`, `render`), not after patterns (`utils`, `helpers`, `common` — rejected by `function-boundary-governor`).
- Prefer `pub(crate)` visibility; expose the minimum surface from `lib.rs`.

## Test placement

| Test kind | Location | Size rule |
|---|---|---|
| Unit tests for one module | `#[cfg(test)] mod tests` at the bottom of that module's file | ≤200 lines; beyond that, move to `src/<area>/tests.rs` (`#[cfg(test)] mod tests;` in the parent) |
| Cross-module / CLI behavior | `tests/<flow>.rs` integration tests | Test through the public `lib.rs` API |
| Never | `main.rs` | `main.rs` gets at most a trivial smoke test; behavior tests target library modules |

If a test needs private internals of a module, it belongs to that module's unit tests. If it exercises the assembled behavior, it belongs in `tests/`.

## When to split

- A file crosses the structure budget (400 lines) → split along responsibility seams; ask `$design-balance` to name the units if unclear.
- A module accumulates a second reason to change (parsing + formatting) → split even below the line budget.
- `main.rs` grows beyond wiring → extract to `lib.rs` modules immediately; this is part of the current change, not a cleanup.

## Growth path (smallest coherent steps)

1. `main.rs` only (throwaway, no tests)
2. `main.rs` + `lib.rs` (first domain logic or first test appears)
3. `lib.rs` + `src/<area>.rs` modules (second domain area appears)
4. `src/<area>/mod.rs` directory modules + `tests/` integration tests (area outgrows one file)

Skipping a step forward is fine when the requirement clearly lands there; never stay a step behind the code you already have.

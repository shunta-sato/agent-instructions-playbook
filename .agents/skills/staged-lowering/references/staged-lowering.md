# Staged lowering reference

This playbook is inspired by research that improves correctness on highly constrained targets by:
(1) generating a lightweight DSL/IR, then
(2) lowering it in multiple constrained passes, and
(3) compiling after every pass to feed back concrete errors before continuing.

## Decision guide (use vs not)

Use staged lowering when:
- constraints are strict and non-obvious (alignment/padding, ABI, memory layout, hardware APIs)
- the target API is brittle and compile feedback is the fastest truth source
- implementation is trending toward trial-and-error

Do NOT use staged lowering when:
- the problem is simple CRUD / straightforward glue
- compile/test feedback is already stable and iteration is cheap

## Staged Lowering Plan (template)

### 1) Problem (one paragraph)
- What to build/change:
- Inputs/outputs:
- Non-goals:

### 2) Hard constraints (MUST)
- MUST:
- MUST:
- MUST:

Examples:
- alignment: X-byte aligned
- padding: tiles must be multiples of Y
- ABI: struct layout stable
- API: allowed call sequence / lifecycle

### 3) IR / DSL sketch (minimal but structured)

Write a compact representation that is stable across passes.

- Entities (data types / buffers / DTOs):
- Stages (ordered):
  1) Setup / acquire / CopyIn
  2) Core compute / transform
  3) Emit / CopyOut
- Invariants per stage:
- Edge cases (only list here; implement later):
- Observability hooks (stage boundaries):

### 4) Pass plan (3–5 passes)

**Pass 1 — Skeleton & wiring**
- Goal: compile with placeholders (no full logic)
- Owns: public signatures, data plumbing, minimal validation, named constants

**Pass 2 — Initialization & resources**
- Goal: all setup paths correct (allocation/init/lifecycle)
- Owns: resource mgmt, state init, parameter normalization

**Pass 3 — Core computation**
- Goal: correct core logic on the “happy path”
- Owns: the main algorithm, not edge cases

**Pass 4 — Edge cases (alignment/padding/bounds)**
- Goal: correctness under constraints
- Owns: padding, alignment, tails, boundary-sensitive behavior

**Pass 5 (optional) — Performance refinements**
- Goal: measurable performance change with proof
- Owns: micro-opts with benchmarks/measurements

### 5) Per-pass verification commands (minimal truth)

For each pass, define the fastest checks you can run:
- Compile/build:
- Format/lint/static analysis:
- Unit tests (or a minimal repro):
- If impossible locally: how CI should validate it:

### 6) Per-pass Verification Log (required)

For each pass:
- Pass N:
  - commands:
  - key results:
  - remaining known gaps (next pass owns them):

## Rules that prevent "cheating"

- Never merge “setup + core logic + edges” in one commit/pass.
- Do not move to the next pass with failing compile/tests.
- Prefer compiler/test feedback over assumptions.
- If a workaround is introduced, record: why, risk, removal plan.

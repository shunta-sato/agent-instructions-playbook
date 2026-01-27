# AGENTS.md — AI Agent core instructions (Codex)

This is the minimal contract for AI agents who add or change code, tests, or documentation in this repository.

Goals:

- Keep the code quick to understand for humans (readability).
- Keep changes localized by maintaining strong cohesion and stable boundaries (modularity / coupling / boundaries).
- Keep requirements and acceptance criteria verifiable after the fact (documentation).

This file is intentionally short. Detailed handbooks live in **Skills** and must be invoked explicitly when needed.

## 0. Highest-priority principles

- When in doubt, choose the option that minimizes the reader’s time to understand.
- You are the author. Reduce places where readers get stuck (naming, branching, error paths, edge cases).
- No large cleanups. However, leave touched code slightly easier to read than before.

## Observability (mandatory)

Operational debugging is a required output. If runtime behavior changes, readers must be able to answer “what happened?” and “why?” from the system’s emitted signals.

Rules:
- **If runtime behavior changes, add or update observability** (logs/metrics/traces) so failures are diagnosable without stepping through code.
- **If unsure, explicitly invoke `$observability`.**

## 1. Mandatory workflow

### 1.1 Before you start implementation (MUST)

**For any task that changes code and/or tests, explicitly invoke `$dev-workflow` first and follow it end-to-end (design → implementation → verification).**

- Do not start editing until you have written: Change Brief / Requirements (acceptance criteria) / Test List / Constraints.
- If the task changes the meaning of requirements or acceptance criteria, do not encode the spec only in code. If documentation needs updates, explicitly invoke `$requirements-documentation` first to decide what to update and to keep the diff minimal.

**C++ documentation rules are mandatory:**

- **`.hpp`**: add Doxygen for **all declarations**, including **private** members.  
  For functions/methods: what it does, parameter meaning (`@param`), return meaning (`@return`), and notable failure modes (exceptions / error returns) when applicable.  
  For fields/constants: meaning, unit (if any), and allowed range or set of values.
- **`.cpp`**: for each cohesion unit (a “paragraph”), add a short **intent comment** (Intent / Assumptions / Pitfalls). Do not leave “what it does” restatements.  
  At boundaries / coupling points, add a short **contract** (assumptions, failure behavior, rationale).
- **No magic values**: do not leave non-trivial numeric or string literals as-is. Use named constants (`constexpr`, `enum`, etc.) so the meaning is visible in names.  
  Exceptions (e.g., obvious `0/1`, idioms like `std::size()`) are allowed only with a short reason.
- Unit tests must make the **why** and the **what** clear.

### 1.2 Before you submit (MUST)

**Before submission, explicitly invoke `$quality-gate` and keep fixing until it reports 0 findings.**

- Run build / format / static analysis / tests until everything is green (use the repo’s canonical commands first).  
  If you cannot run a check, state why and provide a reproducible procedure.
- If you updated documentation, re-check it for ambiguity, non-measurable criteria, and missing traceability using the `$quality-gate` checklist.

## 2. Required final output (MUST)

Your final chat output must include the following (it is acceptable if `$quality-gate` output already covers these):

1) **Change Brief (one paragraph)**: purpose, inputs/outputs, constraints, assumptions, boundaries (UI/HTTP/DB/external services).
2) **Requirements (acceptance criteria)**: 1–5 EARS-style “shall” requirements plus measurable acceptance criteria.
3) **Test List (test design)**: a list of 3–10 tests and the first test you will implement.
4) **Constraints (5–9 bullets)**: the constraints you will enforce in this task (readability / modularity / boundaries / error-handling / documentation).
5) **Docs (if applicable)**:
   - updated document paths, updated requirement IDs (or headings), and the rationale for updating
   - if you chose not to update docs, explain why (e.g., internal refactor only; external behavior and acceptance criteria unchanged)
6) **How to test**: the commands you ran (build/format/static-analysis/tests) and the key results.
7) **Self-review**:
   - Readability: up to 3 “reader-stoppers” you found and what you changed to remove them.
   - C++ headers (if you touched `.hpp`): list declarations and confirm Doxygen completeness (`@param/@return`, failure modes; units and ranges/value sets for fields/constants).
   - C++ implementations (if you touched `.cpp`):
     - Comment intent audit: list added/changed comments; remove or rewrite any comment that cannot be classified as Intent / Assumptions / Pitfalls.
     - Magic value audit: list added/changed numeric/string literals; replace with named constants or add a short exception reason.
   - Modularity / coupling / boundaries: list the evaluated units, the worst-level rating, and (if needed) a split/translation plan.
   - Error handling: boundary translation exists, no swallowed failures, and failure paths are readable.
   - Documentation: requirements and acceptance criteria remain unambiguous, measurable, and traceable.

## 3. Skills (read details only when needed)

Skills are designed to load detailed instructions **only when needed**. If you need the body content, invoke the skill explicitly.

- Workflow (requirements → design → test design → TDD → implementation → verification → final gate): `$dev-workflow`
- Final gate (end-to-end checks and self-review): `$quality-gate`

- Requirements analysis → design (EARS requirements, acceptance criteria, quality scenarios, boundary sketch): `$requirements-to-design`
- Requirements documentation (IDs, rationale, acceptance criteria, verification method, traceability): `$requirements-documentation`
- Test-driven development workflow (Test List, Red→Green→Refactor): `$test-driven-development`

- Working with legacy code (safety-net tests, seams, extract/sprout): `$working-with-legacy-code`

- Code readability handbook (naming, comments, control flow, functions, tests; mandatory C++ doc rules): `$code-readability`
- Modularity handbook (cohesion/coupling/boundaries; evaluate at the lowest unit): `$modularity`
- Error-handling handbook (exception translation at boundaries, failure-path design): `$error-handling`
- Architecture boundaries handbook (dependency direction, DIP, DTOs, boundary placement): `$architecture-boundaries`
- Quality attributes / NFR template (ISO/IEC 25010): `$nfr-iso25010`

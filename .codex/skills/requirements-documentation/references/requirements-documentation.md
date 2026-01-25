# Requirements documentation templates

This file is the reference for the `requirements-documentation` skill. When unsure, do nothing fancy: **fill the blanks in the templates**.

---

## 1) Document granularity (start small)

### Requirements Brief (for small changes)

- Purpose (why it is needed)
- In scope / out of scope
- Intended users
- Assumptions / constraints
- Requirements (R-001…, 1–5 items)
- Acceptance criteria (success/failure)
- Verification method (test/review/measurement/monitoring)
- Open questions / assumptions

### Requirements Spec (for larger changes)

Use a standard structure (purpose, scope, glossary, references, overview, constraints, assumptions, deferred items…), but **keep only the chapters you actually need**.

Suggested minimal chapters:

- Introduction (purpose, scope, glossary, references, document structure)
- Overall description (external relations, feature overview, user characteristics, constraints, assumptions, deferrals)
- Requirements (with IDs; priority; rationale; description)
- Non-functional requirements (only those needed: metric / threshold / measurement / tests & monitoring / design notes)
- Data / API / UI (only when needed)
- Traceability (requirements → design → tests)
- Open questions / assumptions

---

## 2) The “shape” of a single requirement (ID / rationale / measurable)

### Requirement item template (table)

| ID | Priority | Type | Requirement (one sentence) | Rationale (why) | Acceptance criteria (success/failure) | Verification method | Trace (design/tests) | Notes |
|---|---|---|---|---|---|---|---|---|
| R-001 | Must/Should/Could | Functional/NFR/Constraint | When/While/If..., the system shall ... |  | success: … / failure: … | unit/integration/e2e/measurement/monitoring | Design: … / Tests: … |  |

Key writing points:

- If you cannot write a verification method and measurable criteria, the requirement is likely ambiguous or missing assumptions.
- Always write units (ms, MB, req/s, etc.) and ranges (min/max) where applicable.
- Do not mix implementation details (library names, class names) into requirements. If it is truly needed, write it as a **constraint** with rationale.

---

## 3) Standardize requirement phrasing (reduce natural-language drift)

- Prefer EARS (When/While/Where/If..., shall...). You can reuse the templates from `$requirements-to-design`.
- If conditions are many, do not cram into one sentence; split conditions into a bullet list.

---

## 4) Minimum quality checks

### Each requirement

- One requirement = one claim (do not mix).
- No misread: define terms in the glossary.
- Avoid vague words (“appropriately”, “as much as possible”, “fast”, “properly”, etc.).
- Measurable: acceptance criteria and verification method exist.
- Realistic: feasible under constraints (cost, schedule, tech, regulations).

### The requirement set

- No duplicates / no contradictions
- Terms and units are consistent
- No important gaps (NFRs, ops, error cases)

---

## 5) Traceability (start small)

Link requirement IDs to design and tests. Start with only these two columns.

| Requirement ID | Design (module/responsibility) | Tests (test names) |
|---|---|---|
| R-001 |  |  |
| R-002 |  |  |

If ops/monitoring matters, add metrics names or dashboard links.

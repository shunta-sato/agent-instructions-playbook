---
name: code-readability
description: "Trigger only for requested readability review/cleanup, touched-code readability work involving comments, names, control flow, function shape, or test clarity, touched C++ headers, or dev-workflow routing to the C++ documentation gate. Do not trigger for ordinary implementation solely because code changed. Enforces mandatory C++ Doxygen and readability documentation gates."
metadata:
  short-description: Code readability
  requires:
    - references/code-readability.md
---

## Purpose

Use this skill to review or clean up code so the next reader can understand intent, structure, and tests faster. It is a readability and C++ documentation gate, not a default implementation skill.

`dev-workflow` may use a lightweight naming/responsibility check in its default lane. That check does not trigger a full readability review unless the triggers below apply.

## When to use

Use this skill only when at least one trigger applies:

- Readability review, readability cleanup, or touched-code readability refactoring is requested.
- Comments, names, control flow, function shape, or test readability are explicitly in scope.
- C++ headers are touched.
- The development workflow routes the C++ Doxygen/documentation gate here.

Do not use this skill just because code was changed.

## How to use

0) Open `references/code-readability.md`. Select **1–3 relevant headings** and cite them by heading name in your reasoning.

1) From the diff (or planned diff), list up to **three** places where a reader will likely pause:
   naming, branching, error handling, boundary conditions, test intent, or documentation gaps.

2) For each place, write one sentence: “What could the reader misunderstand here?”

3) Propose the smallest change that reduces reading time:
   rename, split a paragraph, add an intent/assumption/pitfall comment, introduce a named constant, or adjust a test name/structure.

3a) For class/module names, check whether the name predicts the unit's responsibility sentence. If not, route layout decisions to `design-balance` or rename locally when no layout change is needed.

4) If you touched C++:
   - `.hpp`: add Doxygen to all declarations (including private) and include units/ranges where relevant.
   - `.cpp`: keep comments intent-first; remove restatements of what the code already says; replace magic values with named constants.
   - Tests: make names and structure explain the behavior and why it matters.

## Output expectation

- Prefer proposals that directly reduce reading time.
- If a proposal increases diff size, explain the benefit (reading time saved) and the risk (review complexity / behavior change).

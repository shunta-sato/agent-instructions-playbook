---
name: comment-discipline
description: "Use when writing or reviewing implementation comments, deciding comment vs commit-message vs test-name content, or cleaning up AI-generated comments that restate code (How) or purpose (What). Comments carry only Why-not: constraints, rejected alternatives, hazards, external requirements. Do not use for C++ Doxygen/public-API docs (`code-readability`), or work with no comment/commit/test-name decision."
metadata:
  short-description: Comment channel discipline
  requires:
    - references/comment-discipline.md
---

## Purpose

Use this skill to decide what information belongs in an implementation
comment versus a commit message versus a test name, and to remove
AI-generated comments that restate code instead of adding what code cannot
express.

## When to use

Use this skill when at least one trigger applies:

- Writing or reviewing implementation comments in a diff.
- Cleaning up AI-generated or redundant comments (narrated diffs, restated
  purposes, section banners, correctness arguments to a reviewer).
- Deciding what content goes in a comment, a commit message, or a test
  name/description for the same change.
- Writing a commit message and deciding what to include.

Do not use this skill for:

- C++ Doxygen headers or public-API documentation comments — those are
  governed by the `code-readability` documentation gate, a different genre
  (contract documentation).
- Implementation work with no comment, commit-message, or test-naming
  decision in scope.

## Boundaries

- `code-readability` owns the C++ Doxygen gate and public-API documentation
  comments (contract documentation, i.e. What at the API boundary); those
  stay mandatory where that gate applies and are exempt from this skill.
- `comment-discipline` owns implementation-comment content, commit-message
  content decisions, and test name/description content — not documentation
  formatting or test framework mechanics.

## How to use

0) Open `references/comment-discipline.md`. Select the relevant section(s)
   and cite them by heading name in your reasoning.

1) For each new or edited implementation comment, ask: is this Why-not
   information (constraint, rejected alternative, hazard, external
   requirement)? If not, delete it.

2) If a comment restates How (narrates adjacent code) or What (restates the
   unit's purpose), delete it. If the urge came from unclear code,
   rename/restructure instead — see `code-readability` §4 Comments.

3) Scan for AI-specific anti-patterns (diff narration, correctness
   arguments, section banners, prose type signatures, who/when metadata) and
   remove them.

4) For test code, move expected-behavior statements into the test
   name/structure; do not restate them in a comment above the assertion.

5) For the commit message, state Why (motivation, constraint, trade-off) in
   English; do not narrate the diff file-by-file.

6) Leave public API documentation comments required by the
   `code-readability` gate untouched.

## Output expectation

- List each kept comment with the Why-not category it satisfies (constraint
  / rejected alternative / hazard / external requirement).
- List each removed or rewritten comment and whether it was replaced by a
  rename/restructure.
- Confirm test names/structure carry the expected behavior instead of
  comments.
- Confirm the commit message states Why, not a diff narration, in English.
- State that API-doc comments required by the `code-readability` gate were
  left untouched.

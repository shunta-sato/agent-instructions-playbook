---
name: code-readability
description: "Readability handbook for this repo (naming/comments/control flow/functions/tests). Includes mandatory C++ documentation rules (Doxygen in .hpp incl private, paragraph intent comments in .cpp, named constants instead of magic values, tests that explain why/what). Always open references/code-readability.md and cite headings."
metadata:
  short-description: Code readability
---

## Purpose

Use this skill to make code faster to understand for humans. It provides concrete guidance for naming, comments, control flow, function structure, and tests.

In this repository, it also defines mandatory C++ documentation rules for `.hpp` and `.cpp`.

## When to use

Use this skill when:

- You know what to implement, but you are unsure how to present it in a readable form.
- You are reviewing a change and need to explain *why* it is hard to read, and how to fix it with a minimal diff.
- You want to do a small refactor focused on readability (naming, early returns, paragraphing, test clarity).

## How to use

0) Open `references/code-readability.md`. Select **1–3 relevant headings** and cite them by heading name in your reasoning.

1) From the diff (or planned diff), list up to **three** places where a reader will likely pause:
   naming, branching, error handling, boundary conditions, test intent, or documentation gaps.

2) For each place, write one sentence: “What could the reader misunderstand here?”

3) Propose the smallest change that reduces reading time:
   rename, split a paragraph, add an intent/assumption/pitfall comment, introduce a named constant, or adjust a test name/structure.

4) If you touched C++:
   - `.hpp`: add Doxygen to all declarations (including private) and include units/ranges where relevant.
   - `.cpp`: keep comments “intent-first”; remove restatements of what the code already says; replace magic values with named constants.

## Output expectation

- Prefer proposals that directly reduce reading time.
- If a proposal increases diff size, explain the benefit (reading time saved) and the risk (review complexity / behavior change).

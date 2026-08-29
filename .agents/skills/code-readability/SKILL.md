---
name: code-readability
description: "Use for an explicit readability review or cleanup, or when changed C++ public/stable APIs need contract documentation. Do not trigger for ordinary implementation, private C++ declarations, or local code whose intent is already clear."
metadata:
  short-description: Proportional code readability
  requires:
    - references/code-readability.md
---

## Purpose

Reduce reading and change cost where it matters to the current diff and
maintenance horizon. This is not a documentation or small-function quota.

## When to use

Use when readability is explicitly in scope, a reviewer identifies a concrete
misread risk, or changed C++ public/stable APIs need contract documentation.
Do not trigger solely because a header, test, or source file changed.

## How to use

0) Open `references/code-readability.md` and select one to three relevant
headings.
1. List up to three places in the changed surface where a maintainer could make a
plausible wrong inference.
2. State that inference and the smallest correction: rename, local control-flow
change, contract documentation, or a Why-not comment.
3. Prefer existing project style. Do not introduce a broad cleanup or new
abstraction for readability alone.
4. For C++:
   - document changed public/protected or otherwise stable contracts with Doxygen;
   - document private details only for non-obvious invariants, units, ownership,
     lifetime, or hazards;
   - keep implementation comments to constraints, rejected alternatives, and
     hazards that code/tests cannot express;
   - name only literals whose domain meaning is not evident locally.
5. Stop when the current diff can be understood and safely changed. Defer polish
that is unrelated to the DoD.

## Output expectation

Return the selected headings, concrete misread risks, smallest applied or
proposed corrections, C++ contract-documentation result when applicable, and
optional deferred polish. Do not require a finding when the changed code is
already sufficient.

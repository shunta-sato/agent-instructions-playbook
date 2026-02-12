---
name: requirements-to-design
description: "MANDATORY during planning: convert a task into EARS requirements + measurable acceptance criteria + (if needed) quality scenarios + boundary sketch + failure paths + a test list seed. Always open references/requirements-to-design.md."
metadata:
  short-description: Requirements → design
---

## Purpose

Use this skill to turn an ambiguous request into a small, implementable plan.

It produces:

- EARS-style requirements (“shall”)
- measurable acceptance criteria
- a boundary sketch (UI/HTTP/DB/external services)
- key failure paths
- a seeded Test List

## When to use

Use this skill when you are about to start implementation and the request is not already in a verifiable form.

It is mandatory as part of `$dev-workflow`.

## How to use

1) Open `references/requirements-to-design.md` and fill the template.

2) Keep it small: 1–5 requirements, each with acceptance criteria and verification method.

3) If quality attributes matter, add quality scenarios (latency, availability, etc.) and link to `$nfr-iso25010` if needed.

## Output expectation

- Requirements and acceptance criteria are measurable.
- Assumptions and open questions are explicit.
- The boundary sketch explains what is in scope and what is out of scope.

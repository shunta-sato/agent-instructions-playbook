---
name: error-handling
description: "Use when a change defines or reviews failure contracts: boundary error translation, nullability/sentinel choices, retries/fallbacks, or API/user-visible failure behavior. Do not use for ordinary validation copy edits or pure logging changes with no failure-contract change."
metadata:
  short-description: Boundary error handling
  requires:
    - references/error-handling.md
---

## Purpose

Use this skill to design failure paths without making the happy path unreadable.

It focuses on boundary handling: translate external errors (DB/HTTP/FS/framework) into domain-level errors, and avoid leaking `null`/`None` inward.

## When to use

Use this skill when:

- Adding or changing boundary behavior for DB, HTTP, filesystem, framework, queue, or third-party failures.
- Translating low-level exceptions or error codes into domain, API, CLI, or user-visible responses.
- Choosing between exceptions, result types, sentinel objects, `null`/`None`, or optional values.
- Adding or changing retries, fallbacks, timeouts, partial success, or recovery behavior.
- Reviewing swallowed errors, ambiguous failure returns, or mixed command/query behavior.

Do not use this skill for ordinary validation message copy edits, pure logging changes, formatting, or refactors that do not change the failure contract.

## How to use

0) If this skill is triggered, open `references/error-handling.md`. Select **1–3 relevant headings** and cite them by heading name in your reasoning.

1) Identify boundaries and list possible failures (timeouts, not found, invalid data, permission errors).

2) Decide how to translate those failures into your domain language:
   - raise a domain error with context, or
   - return a dedicated result type / sentinel object (avoid `null/None` by default).

3) Keep the happy path visible:
   separate “normal flow” from “error conversion / logging / cleanup”.

## Output expectation

- Show the boundary, the translation rule, and what the caller sees.
- If a failure is recoverable, show how the normal flow continues safely.

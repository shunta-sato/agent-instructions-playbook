---
name: error-handling
description: "Boundary error-handling handbook (exception translation, failure paths, null/None). Use when designing or reviewing error paths. Always open references/error-handling.md and cite headings."
metadata:
  short-description: Boundary error handling
---

## Purpose

Use this skill to design failure paths without making the happy path unreadable.

It focuses on boundary handling: translate external errors (DB/HTTP/FS/framework) into domain-level errors, and avoid leaking `null`/`None` inward.

## When to use

Use this skill when:

- You are adding or changing code that touches external boundaries (DB/HTTP/files/frameworks).
- You are unsure how to represent failure (exceptions vs error values) and how to keep call sites readable.
- You are reviewing code that swallows errors, returns ambiguous `null/None`, or mixes command + query behavior.

## How to use

0) Open `references/error-handling.md`. Select **1–3 relevant headings** and cite them by heading name in your reasoning.

1) Identify boundaries and list possible failures (timeouts, not found, invalid data, permission errors).

2) Decide how to translate those failures into your domain language:
   - raise a domain error with context, or
   - return a dedicated result type / sentinel object (avoid `null/None` by default).

3) Keep the happy path visible:
   separate “normal flow” from “error conversion / logging / cleanup”.

## Output expectation

- Show the boundary, the translation rule, and what the caller sees.
- If a failure is recoverable, show how the normal flow continues safely.

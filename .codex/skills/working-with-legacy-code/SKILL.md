---
name: working-with-legacy-code
description: "MANDATORY when touching code without reliable automated tests or with nondeterminism (time/random/IO). Create a safety-net test (characterization), introduce seams to make behavior deterministic, then refactor safely while keeping all gates green. Always open references/working-with-legacy-code.md."
metadata:
  short-description: Working with legacy code safely
---

## Purpose

Use this skill to change legacy code safely: code with weak tests, no tests, or behavior that is hard to make deterministic.

The goal is not to “make it perfect” immediately. The goal is to **create safety**, then change behavior in small steps.

## When to use

Invoke this skill **before refactoring** if any of the following is true:

- There are no reliable automated tests covering the behavior you will touch.
- Behavior depends on time, random, threads, network, filesystem, processes, or external services.
- Tests exist but are flaky, slow, or hard to run locally.

## How to use

0) Open `references/working-with-legacy-code.md`. Pick the headings that match your situation and follow the order.

1) Create a safety net first:
   - Write a characterization test (current behavior) or a high-level regression test.
   - Make it deterministic using seams (dependency injection, wrappers, fakes).

2) Only after the safety net is green:
   - Extract small functions, isolate boundaries, and refactor in small diffs.
   - Keep `build / format / static analysis / tests` green at every step.

3) If you cannot add a safety net, stop and explain why. Provide a reproducible manual procedure and the risk.

## Output expectation

- Explicitly list: safety-net test(s), introduced seam(s), and the refactor sequence.
- State what is guaranteed not to change (protected by characterization tests) and what is intended to change.

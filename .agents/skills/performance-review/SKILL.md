---
name: performance-review
description: "Use when non-embedded application code changes request paths, render paths, input-proportional collection processing, loop I/O, N+1 queries, repeated serialization/allocation, serial awaits, or cache/memoization decisions. Declare hot paths, complexity, I/O counts, scale assumptions, and improve-or-accept decisions. For target-local embedded hot paths, use embedded-hot-path-review instead."
metadata:
  short-description: Generic performance review
---

## Purpose

Use this skill to catch avoidable performance costs in ordinary application code before they ship.

It answers one question:

**Will this change scale acceptably on the path where users, requests, jobs, or frames wait?**

## When to use

Use this skill for non-embedded code when a change includes:

- request, render, job, or user-visible paths where latency matters
- loops over input-sized collections
- database queries, filesystem calls, network calls, or serialization inside loops
- N+1 query risk or repeated SDK/API calls
- repeated JSON parsing/serialization, regex, sorting, copying, allocation, or formatting
- serial `await` chains that could be batched, parallelized, cached, or moved off the path
- cache, memoization, batching, pagination, or streaming decisions

Do not use it for:

- target-local embedded loops, polling, sampling, collectors, recorders, or sub-100ms work; use `embedded-hot-path-review`
- pure documentation, schema-only changes, or tests with no runtime path
- one-shot scripts where input size and runtime cost are bounded and not user-visible
- broad architecture option comparison; use `architecture-decision-analysis`

## How to use

1. Identify the path:
   - operation or component
   - request/render/job/background path
   - expected data size and growth axis
   - latency or throughput sensitivity

2. Declare cost:

   | Path | Data scale | Time complexity | I/O/query count | Allocation/copy/serialization cost | Serial wait risk |
   |---|---|---|---|---|---|
   | `<path>` | `<n, bounded, unknown>` | `<O(...)>` | `<count or unknown>` | `<cost or unknown>` | `<yes/no>` |

3. Check red flags:
   - I/O or queries inside loops
   - N+1 behavior
   - unbounded collection growth
   - repeated parse/serialize/regex/sort/copy per item
   - serial external calls on a latency-sensitive path
   - cache/memoization without invalidation or size bounds

4. Decide one:
   - `improve-now`: change the implementation before submit
   - `accept`: cost is bounded, measured, or outside the sensitive path
   - `accept-with-limit`: safe only under stated input bounds or rollout limits
   - `needs-measurement`: no performance claim is allowed until evidence exists

5. If measurement is feasible, run the smallest relevant benchmark, profiler, trace, query log, or test. If measurement is not feasible, state the scale assumption and avoid performance claims beyond that assumption.

6. Hand off to `observability` when runtime latency/error signals are needed after shipping, and to `architecture-decision-analysis` when the fix requires choosing among cross-boundary options.

## Output expectation

Return a concise Performance Review:

- Hot path(s) reviewed.
- Cost declaration table.
- Decision: `improve-now | accept | accept-with-limit | needs-measurement`.
- Evidence: measurement, test, code inspection, query plan/log, or explicit no-measurement limit.
- Follow-up only when a limit or measurement gap remains.

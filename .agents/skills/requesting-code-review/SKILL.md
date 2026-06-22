---
name: requesting-code-review
description: "Use when preparing a focused code-review request for a PR or diff after implementation evidence exists, especially to package scope, reviewer focus, PR URL, verification, known risks, and deferred work without deciding final submit readiness."
metadata:
  short-description: Prepare focused review requests
---

## Purpose

Use this skill to ask for review with enough context for a reviewer to make a
decision quickly.

The skill packages review context. It does not decide submit readiness, replace
`quality-gate`, or hide known gaps.

## Boundaries

- `quality-gate` owns submit/no-submit readiness.
- `requesting-code-review` owns the review request package.
- `receiving-code-review` owns review feedback handling after comments arrive.
- `branch-completion` owns post-review branch and PR lifecycle actions.

## Workflow

1. Confirm the review target.
   - PR URL or diff range.
   - Base and head branches or commits.
   - Whether the PR is draft or ready for review.

2. Gather evidence.
   - Change summary and intentional scope.
   - Files or subsystems changed.
   - Verification commands and results.
   - Required branch-skill artifacts, such as ExecPlan or workflow contract
     review reports.
   - Known risks, deferred work, and explicit non-goals.

3. State reviewer focus.
   - Ask for review of the changed surface, not a full repository audit.
   - Name the highest-risk responsibilities, boundaries, generated artifacts,
     or validation contracts.
   - Identify which topics are out of scope for this PR.

4. Send a review request that includes:
   - Raw PR URL or exact diff identifier.
   - Summary.
   - Verification.
   - Reviewer focus.
   - Deferred or intentionally excluded work.
   - Instruction for where review comments should be left when the user or
     workflow requires a specific channel.

## Request Package

```markdown
Review target: <raw PR URL or diff>

Scope:
- <what changed>
- <what did not change>

Verification:
- `<command>`: <result>

Reviewer focus:
- <boundary, behavior, generated artifact, or risk to inspect>

Known risks / deferred:
- <risk or none>

Please leave review comments on: <GitHub PR / specified channel>
```

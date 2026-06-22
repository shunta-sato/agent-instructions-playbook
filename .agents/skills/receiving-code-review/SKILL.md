---
name: receiving-code-review
description: "Use when handling received code-review feedback on a PR or diff, including requested changes, inline comments, approvals, non-blocking notes, and disputed suggestions. Separates accepted fixes, refutations, deferrals, clarification needs, and merge handoff."
metadata:
  short-description: Process review feedback safely
---

## Purpose

Use this skill to process review feedback without blindly applying every
suggestion.

Each comment needs a disposition, evidence, and either a smallest safe fix or a
clear reason no code change is made.

## Workflow

1. Read review state from the source of truth.
   - PR comments.
   - Review submissions.
   - Inline review threads, including resolved/unresolved state when available.
   - CI/check status if it affects review readiness.

2. Assign each item exactly one disposition:
   - `accept`: The reviewer identified a real issue in scope.
   - `refute`: The suggestion conflicts with requirements, evidence, or scope.
   - `defer`: The issue is valid but belongs outside this PR.
   - `clarify`: The requested change is ambiguous or lacks enough location or
     acceptance detail.
   - `acknowledge`: The item is informational, approval-only, or already
     satisfied.

3. Apply accepted fixes with the smallest safe change.
   - Preserve existing scope and requirements.
   - Re-run the repository-required verification for the changed surface.
   - Keep unrelated working-tree changes out of the response branch.

4. Respond with evidence.
   - Reference the comment or thread.
   - State the disposition and action.
   - Include verification results after fixes.
   - If refuting or deferring, cite the requirement, plan, PR scope, or code
     evidence that supports that decision.

5. Hand off approvals to `branch-completion`.
   - Treat an explicit approved review, or a clear PR comment saying `Approve`,
     as an approval signal.
   - Do not merge while unresolved blocking findings, failing required checks,
     or uncommitted accepted fixes remain.

## Feedback Ledger

Use this compact ledger when review has more than one item:

| Comment / thread | Disposition | Action | Evidence |
| --- | --- | --- | --- |
| `<id or location>` | `accept/refute/defer/clarify/acknowledge` | `<fix or response>` | `<test, requirement, scope, or code ref>` |

If the ledger has only approval and no required changes, record the approval
signal and move to `branch-completion`.

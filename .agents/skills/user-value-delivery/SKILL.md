---
name: user-value-delivery
description: "Use for issue-scoped feature delivery, backlog campaigns, and stalled feature PRs when internal quality work is delaying an observable user capability. Governs scope, sequencing, review admission, delivery cost, and stop conditions. Do not use for factual answers, research-only probes, or tiny isolated fixes."
metadata:
  short-description: User-value delivery governor
---

# User-Value Delivery
## Purpose

Keep feature work directed toward an observable user capability instead of
turning the current issue into a codebase-improvement campaign.

This skill governs scope, sequencing, review admission, delivery cost, and
stopping. It does not weaken explicit acceptance criteria, safety, security,
privacy, compliance, data integrity, compatibility, authorization, branch
protection, or repository-required checks.

## Frame the capability
Before product edits, record:

- **User journey:** the action or trigger and the result the user observes.
- **Definition of Done:** the smallest complete end-to-end behavior.
- **Not required:** maintenance, generalization, or hardening outside this DoD.
- **Failure criticality:** `low | standard | critical`.
- **Maintenance horizon:** `short | bounded | durable`.
- **Cheapest decisive proof:** the focused check that can disprove the approach.

Failure criticality determines correctness, safety, security, and verification
depth. Maintenance horizon determines structure, abstraction, documentation,
and generalization depth. Short-lived code receives no safety exemption;
high-risk code does not automatically require durable architecture.

Freeze the DoD, non-goals, and required-skill route when implementation starts.
A later route addition needs newly discovered blocking evidence.

## Admit proposed work
Treat substantial additions as one of:

1. observable user behavior;
2. correctness, safety, compatibility, failure handling, or resource control
   required by the current DoD;
3. independently valuable infrastructure;
4. maintenance, readability, or speculative hardening.

Admit categories 1 and 2. Admit category 3 only with its own releasable value or
explicit approval. Defer category 4 unless the current capability cannot safely
meet its DoD.

A triggered skill may require a decision or evidence. Its invocation alone does
not justify a framework, generic harness, child issue, broad refactor, or separate
artifact. Reuse the active plan or PR section and record the smallest truthful
evidence.

## Delivery Control
Keep this block in the active ExecPlan or PR description. Before publication,
keep it in the root agent's current plan. Do not create a file only for this block.

```text
Delivery Control
- issue / user journey:
- observable DoD:
- not required:
- failure criticality / maintenance horizon:
- active PR: not-published | <URL>
- state: framing | implementing | reviewable | blocked | monitor | merged
- candidate identity:
- production delta:
- push / required-CI count:
- attempts by cause:
- target attempts by cause:
- capability delta since previous checkpoint:
- next decisive proof:
- final gate owner:
- stop condition:
```

Only the orchestrating agent edits Delivery Control. Workers and reviewers
receive a read-only projection of the user journey, DoD, non-goals, allowed
scope, validation, and stop conditions.

## Delivery limits
- Keep one primary feature PR. A second lane must be independently releasable or
  mutation-free monitoring.
- Stop after two equivalent attempts for the same cause. A further attempt needs
  a materially different hypothesis recorded first.
- Use focused checks during iteration. The assigned owner performs one final full
  HOST gate for an identified candidate by default.
- Initiate no more than two pushes that trigger required CI by default.
- Use one independent review by default. After blocking fixes, re-check only the
  affected findings and surface unless the candidate changed materially.
- Use one final release build by default.
- Stop for scope inversion when supporting implementation becomes larger than
  the remaining user-facing implementation.

When a reliable clock exists, use 15 minutes as the scope-framing objective,
30-minute capability checkpoints, 60 minutes to publish a reviewable vertical
slice, and two hours to reach `merged | reviewable | blocked | monitor`. A missed
objective activates the stop protocol; it does not authorize more preparation.

## Blocking review standard
A finding blocks only when it is concrete, inside the stated operating boundary,
and establishes one of:

- unmet DoD;
- a material regression in a supported journey, or a compatibility-contract breach, introduced or worsened by the candidate;
- a failing required repository check;
- a safety, security, privacy, authorization, or data-integrity defect;
- violation of an explicit measured NFR or resource limit.

Severity labels are evidence, not authority. A blocking finding must name the
violated criterion, concrete failure path, affected actor or journey, relation to
the candidate, and smallest required fix.

Minor cosmetic defects, rare low-impact edge cases outside the DoD, style preferences,
readability improvements, pre-existing debt, optional generalization, generic
hardening, and out-of-boundary scenarios are non-blocking by default. Keep them as optional PR notes without automatic issue creation.

## Stop protocol
At a delivery limit:

1. Stop new behavior, diagnostics, target attempts, and design expansion.
2. Restore the current candidate to a buildable, reviewable state if needed.
3. Publish the existing candidate or record the exact blocker in the active PR.
4. Report the evidence and the smallest scope decision required.
5. Do not continue equivalent work in another branch or subagent.

## Vertical path and finish
Build the shortest real path:

```text
user input or trigger
→ production control flow
→ observable output
→ required failure or omission behavior
→ cheapest decisive integration or target proof
```

After the DoD passes, allow one bounded polish pass: at most three local,
non-blocking fixes, with no new framework, abstraction layer, harness, or scope.

Use `receiving-code-review` for review-comment dispositions and
`branch-completion` for publication, merge, and cleanup. Do not duplicate their
records here.

## Output expectation
Return the framed capability, Delivery Control state, admitted/deferred work,
current capability delta, next decisive proof, and any activated stop condition.
Lead completion reports with what the user can now do.

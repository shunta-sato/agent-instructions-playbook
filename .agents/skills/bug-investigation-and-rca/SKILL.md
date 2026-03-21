---
name: bug-investigation-and-rca
description: "Bug investigation + root cause analysis workflow. Use when fixing crashes, regressions, flakes, hangs, incorrect outputs, or incidents. Produces an evidence-based Bug Report including prevention actions."
metadata:
  short-description: Bug investigation & RCA
---

## Purpose

This skill exists to make bugfixes diagnosable and repeatable by enforcing evidence → root cause → fix → verification → prevention.

## When to use (triggers)

Use this skill when any of these apply:

- Task mentions: bug, regression, flaky, crash, hang, error, incident, outage, “why”, or “root cause”.
- Fixing a test failure that is not a simple typo (behavior-level failure).
- Introducing workaround/ops mitigation.
- Any change that alters failure-handling paths (exceptions, retries, fallbacks).

## How to use (procedure; anti-cheat)

1) Reproduce (or explain why reproduction is currently impossible).
2) Capture evidence (logs/metrics/traces, stack traces, minimal repro, or failing test output).
3) Form hypotheses (max 2) and pick the leading one.
4) Validate the hypothesis (add/adjust logging, add a minimal test, or use debugger/tooling).
5) Apply the smallest safe fix.
6) Verify with tests/repro/tooling output.
7) Add prevention actions (at least 1) with a verifiable end state.

For details and guidance, open `references/bug-investigation-and-rca.md`.

Helper for deterministic artifact bootstrap:
- `python scripts/init_artifact.py --kind bug-report --slug <ticket-or-topic>` (default output: `reports/bug-reports/<slug>.md`)

## Gotchas

- **Common pitfall:** patching immediately, losing reproducibility and evidence.  
  **Instead:** first lock reproduction steps and failure evidence, then secure a minimal repro or failing test.
- **Common pitfall:** fixing multiple hypotheses at once, making it unclear what worked.  
  **Instead:** pick one leading hypothesis, add observation points (logs/tests/metrics), verify, then fix.
- **Common pitfall:** filling Five Whys with guesses, making prevention vague.  
  **Instead:** label each Why as evidence or assumption, and define measurable completion criteria for prevention.
- **Common pitfall:** shipping a workaround as permanent without follow-up tracking.  
  **Instead:** document risk, removal conditions, and tracking ticket, then plan removal timing.

## Output expectation (strict format; always emit)

## Bug Report (RCA)
- Title:
- Symptom (actual behavior):
- Expected behavior:
- Severity/Impact:
- Environment (versions, platform, config):
- Detection (how it was found):

### Reproduction
- Steps to reproduce:
- Minimal repro (if available):
- Frequency:

### Evidence
- Logs / stack trace / metrics / traces:
- What changed recently (if known):

### Root Cause Analysis (Five Whys)
1) Why #1:
2) Why #2:
3) Why #3:
4) Why #4:
5) Why #5 (root cause):

> Rule: each “Why” must be backed by evidence or a clearly labeled assumption.

### Fix
- What changed (summary):
- Why this fix addresses the root cause:

### Verification
- Tests run:
- Repro re-run result:
- Tooling run (if relevant):

### Prevention (must include at least one, measurable)
- Prevent:
- Detect:
- Mitigate:
- Follow-up tasks (with owners / tracking IDs if available):

### Workaround (only if unavoidable)
- Workaround description:
- Risk:
- Removal plan / tracking:

If reproduction is impossible:
- explicitly state why,
- and what evidence was used instead,
- and what instrumentation/test should be added next.

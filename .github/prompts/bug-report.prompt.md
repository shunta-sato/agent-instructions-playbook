# bug-report
Generate an evidence-based Bug Report (RCA) for the bug being fixed in the current change.

Rules:
- Facts vs assumptions must be separated.
- Use Five Whys for root cause analysis.
- Include verification and at least one prevention action.
- Workarounds are last resort and must include risk + removal plan.
- Cap speculative statements and label assumptions explicitly.
- Output must follow the exact format below.

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

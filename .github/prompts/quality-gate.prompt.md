# quality-gate

Final gate prompt for submit/no-submit decision using exit criteria.

Return:

- Gate decision: `submit` or `no-submit`
- Findings list (location, failed/missing criterion, required fix)
- Checks run (exact commands + pass/fail/skipped with reason)
- Triggered-branch evidence status (present/missing + artifact path)
- Explicit open risks/follow-ups (if any)

Notes:
- Keep this prompt focused on exit criteria.
- If deep analysis is needed, route to dedicated review skills and return with updated findings.

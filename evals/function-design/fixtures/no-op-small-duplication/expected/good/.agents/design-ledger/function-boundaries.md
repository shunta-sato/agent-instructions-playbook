# Function Boundary Design Ledger

## Decision type
- boundary decision

## Scope
- Module/files: `tests/test_calculations.py`
- Date: 2026-05-25

## Decision
- Old abstraction(s): none
- New abstraction(s): none
- Keep parallel? yes

## Reasoning
- Concept boundaries: duplicated order dictionaries are test fixture data, not production behavior.
- Invariant ownership: production `order_total` remains focused on calculation.
- Side-effect profile: pure calculation only.
- Error behavior: unchanged.
- Future divergence expectation: fixture data is likely to diverge by test case.

## Guardrails
- Do not reintroduce: production helpers for test fixture data.
- Merge allowed only if a test-local builder improves multiple tests without hiding intent.
- Adapter removal condition: not applicable.

## Verification evidence
- Commands: `python3 -m unittest discover -s tests`
- Results: pass

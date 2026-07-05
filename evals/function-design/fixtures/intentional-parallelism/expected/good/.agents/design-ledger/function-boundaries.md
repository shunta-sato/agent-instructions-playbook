# Function Boundary Design Ledger

## Decision type
- intentional duplication

## Scope
- Module/files: `src/parsers.py`
- Date: 2026-05-25

## Decision
- Old abstraction(s): none
- New abstraction(s): none
- Keep parallel? yes

## Reasoning
- Concept boundaries: required and optional fields are separate caller contracts.
- Invariant ownership: each function owns its field-presence invariant.
- Side-effect profile: pure parsing only.
- Error behavior: required parsing raises, optional parsing returns `None`.
- Future divergence expectation: high because caller contracts differ.

## Guardrails
- Do not reintroduce: generic `_parse_int(required=...)` or mode-switch helpers.
- Merge allowed only if error behavior becomes identical.
- Adapter removal condition: not applicable.

## Verification evidence
- Commands: `python3 -m unittest discover -s tests`
- Results: pass

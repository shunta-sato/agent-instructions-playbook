# Function Boundary Design Ledger

## Decision type
- replaced abstraction

## Scope
- Module/files: `src/exporter.py`, `src/jobs.py`
- Date: 2026-05-25

## Decision
- Old abstraction(s): `build_invoice_payload(include_tax=...)`
- New abstraction(s): `build_invoice_summary`, `build_tax_invoice_payload`, `build_invoice_audit_record`
- Keep parallel? no

## Reasoning
- Concept boundaries: summary, tax payload, and audit record are separate responsibilities.
- Invariant ownership: each function owns one payload shape.
- Side-effect profile: pure payload construction only.
- Error behavior: unchanged key lookup behavior.
- Future divergence expectation: high if collapsed behind boolean behavior switches.

## Guardrails
- Do not reintroduce: boolean behavior flags such as `include_tax`, `include_notes`, `legacy`, or `mode`.
- Merge allowed only if all call sites need the same payload concept.
- Adapter removal condition: not applicable.

## Verification evidence
- Commands: `python3 -m unittest discover -s tests`
- Results: pass

# Function Boundary Design Ledger

## Decision type
- staged adapter

## Scope
- Module/files: `src/accounts.py`, `src/service.py`
- Date: 2026-05-25

## Decision
- Old abstraction(s): `build_account_record`
- New abstraction(s): `build_customer_profile`
- Keep parallel? no

## Reasoning
- Concept boundaries: internal dashboard code needs customer profile data, not the public record shape.
- Invariant ownership: `build_customer_profile` owns the internal display-name shape.
- Side-effect profile: pure data mapping only.
- Error behavior: existing key lookup behavior remains.
- Future divergence expectation: public record shape may remain backward-compatible while internal profile evolves.

## Guardrails
- Do not reintroduce: internal imports of `build_account_record`.
- Merge allowed only if external compatibility is no longer required.
- Adapter removal condition: remove `build_account_record` after external callers have migrated in the next public API cleanup.

## Verification evidence
- Commands: `python3 -m unittest discover -s tests`
- Results: pass

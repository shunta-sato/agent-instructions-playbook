# Function Boundary Design Ledger

## Decision type
- replaced abstraction

## Scope
- Module/files: `src/users.py`, `src/importer.py`, `src/preview.py`
- Date: 2026-05-25

## Decision
- Old abstraction(s): `normalize_and_save_user`
- New abstraction(s): `normalize_user`, `save_normalized_user`
- Keep parallel? no

## Reasoning
- Concept boundaries: pure normalization no longer owns persistence.
- Invariant ownership: normalized user shape is owned by `normalize_user`.
- Side-effect profile: storage mutation is isolated in `save_normalized_user`.
- Error behavior: existing key errors remain unchanged.
- Future divergence expectation: preview and persistence can evolve independently.

## Guardrails
- Do not reintroduce: `dryRun`, `skipPersist`, `withoutSideEffects`, or `normalize_and_save_user`.
- Merge allowed only if the caller needs both normalization and persistence.
- Adapter removal condition: not applicable; old abstraction deleted.

## Verification evidence
- Commands: `python3 -m unittest discover -s tests`
- Results: pass

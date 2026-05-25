# Function Boundary Governor

## Decision rubric (score each 0-2)

- Concept clarity
- Single reason to change
- Invariant ownership
- Call-site readability
- Side-effect profile control
- Error behavior clarity
- Abstraction cost vs benefit
- Duplication risk (accidental)
- Future divergence likelihood
- Boundary crossing risk
- Test protection

Interpretation:
- 18-22: keep/rename/split/inline candidate
- 12-17: merge/replace needs caution
- <=11: replace or no-op unless test evidence is weak

## Mandatory reject signals

Reject (or choose no-op) when:
- similarity is textual only
- abstraction needs vague names
- abstraction requires flags/options to represent different semantics
- side effects differ materially
- error behavior differs materially
- call sites become harder to read
- tests/characterization coverage is insufficient

## Action guidance

- keep: function already has clear concept + owned invariants.
- rename: concept is right, name is wrong.
- split: one function owns multiple reasons to change.
- merge: only when concepts/invariants/error+side-effects align.
- replace: current abstraction is fundamentally wrong.
- inline: abstraction cost exceeds value.
- no-op: avoid speculative cleanup.

## Required evidence log

For each affected function, capture:
- concept it represents
- reason to change axis
- owned invariants
- side effects
- error contract
- call-site readability notes
- chosen action and why alternatives were rejected

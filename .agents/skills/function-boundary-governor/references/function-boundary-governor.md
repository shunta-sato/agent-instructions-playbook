# Function Boundary Governor

## Required discovery

Before deciding, build a boundary inventory:

- List new/edited/deleted functions.
- For each changed function, list direct callers when feasible.
- Search semantic neighbors: similarly named functions, similar bodies, same domain noun/verb, helpers in common/shared/util modules, and tests encoding the same concept.
- Classify each neighbor: `same concept | parallel concept | obsolete abstraction | uncertain`.

If the main uncertainty is which class/module/layer should own a responsibility, stop and route that decision to `design-balance`. Return here only after the module/class layout is clear.

## Scoring model (separate polarity)

Positive evidence (score 0-2 each):
- concept clarity
- single reason to change
- invariant ownership
- call-site readability gain
- side-effect control
- error behavior clarity
- test protection

Risk evidence (score 0-2 each):
- abstraction cost
- duplication risk
- future divergence likelihood
- boundary crossing risk
- public API churn
- parameterization pressure

## Decision rules

Merge only if all are true:
- concept clarity >= 2
- invariant ownership >= 2
- side effects and error behavior match
- call-site readability gain > 0
- boundary crossing risk == 0
- parameterization pressure == 0

Replace when:
- one or more replacement reasons are true:
  - current abstraction owns wrong responsibility or side effects
  - sibling/helper accumulation exists
  - reuse requires flags/options
- and migration feasibility is true:
  - all call sites can migrate now, or
  - staged adapter is explicitly ledgered with removal condition

Keep parallel when one or more are true:
- error behavior differs
- side effects differ
- future divergence likelihood >= 2
- concepts are only textually similar

No-op when one or more are true:
- improvement is speculative
- tests/characterization are insufficient
- duplication is small and likely to diverge

## Mandatory reject signals

Reject refactor (or choose no-op) when:
- similarity is textual only
- abstraction needs vague names
- abstraction requires flags/options for semantic switching
- call sites become harder to read
- tests are insufficient for safe migration

## Required evidence log

For each affected function capture:
- concept, reason-to-change axis, owned invariants
- side effects and error contract
- caller set and neighbor classification
- chosen action and rejected alternatives
- action taken and touched files


## Action guidance for keep/rename/split/inline

Keep when:
- concept, invariant, side-effect profile, and call sites are already coherent.

Rename when:
- responsibility is right but name hides the domain concept or invariant.

Split when:
- one function owns multiple reasons to change or mixes pure logic with effects.

Inline when:
- abstraction cost exceeds value and call sites become clearer without it.

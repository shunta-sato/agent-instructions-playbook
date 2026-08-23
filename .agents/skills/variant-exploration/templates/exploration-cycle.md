# Exploration Cycle <cycle-id>

## Mode receipt

- resolved mode:
- mode source:
- target paths:
- boundary-gate command:
- boundary-gate result:

## Decision frame

- decision question:
- decision unlocked:
- variant budget:
- time/cost budget:
- exploration horizon:
- stop condition:
- synthesis point:

## Boundary classification

### Protected boundaries

| Boundary | Isolation/fake/approval | Verification |
| --- | --- | --- |
|  |  |  |

### Controlled substrate

| Variable | Fixed value / identity | Verification |
| --- | --- | --- |
| base revision |  |  |
| fixture/backend |  |  |
| data/account |  |  |
| target/OS |  |  |
| network/build mode |  |  |

### Variation axes

| Axis | Why decision-relevant | Variants |
| --- | --- | --- |
|  |  |  |

### Disposable surfaces

- 

## Evaluation protocol

### Shared scenarios

| ID | Initial state | Action sequence | Oracle | Artifact |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

### Human rubric

| Dimension | Scale / question | Interpretation limit |
| --- | --- | --- |
|  |  |  |

### Machine measurements

| Metric | Command/harness | Unit | Claim status |
| --- | --- | --- | --- |
|  |  |  | observation-only / experiment ID |

### Identity contract

- source revision:
- protocol revision:
- required build/variant/target fields:

## Variant Briefs

### Variant <id>

```yaml
variant_id:
base_revision:
primary_axis:
hypothesis:
controlled_substrate:
allowed_files:
forbidden_boundaries:
smoke_command:
evaluation_scenarios:
stop_condition:
```

- rigor-floor result:
- review decision:
- blocker fixes:
- evaluation result:
- decision: keep | mutate | drop
- retained knowledge:
- rejected behavior:
- next variation axis:

## Exploration maintenance decisions

| Location | Enabling condition | Minimum refactor | Stop condition | Result |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## Blocker-only review

- review profile: exploration-blockers-only
- pass count:
- decision: pass | block | escalate
- blocking findings:
- invalidated learning/protected boundary:
- minimum fixes:
- explicitly not reviewed:
  - production maintainability
  - architecture cleanliness
  - DRY and abstraction quality
  - broad test coverage
  - production observability

## Observations and evidence

| Statement | Observation or claim | Experiment/claim ID | Limits |
| --- | --- | --- | --- |
|  |  |  |  |

## Cycle outcome

- variants attempted:
- budget consumed:
- kept:
- mutated:
- dropped:
- unresolved confounders:
- recommendation to research-synthesis:

## Productization Brief

Complete only for a promotion candidate.

```yaml
promotion_strategy: rebuild-from-contract
prototype_source_authority: non-authoritative
```

### Feature Contract

### Interaction Contract

### Quality Contract

| Metric | Target / direction | Measurement method | Evidence / provisional limit |
| --- | --- | --- | --- |
|  |  |  |  |

### API / Data Contract

### Accepted evidence

- claim IDs:

### Rejected alternatives and retained knowledge

### Open uncertainties

### Exploration code disposition

### Approved reusable non-runtime artifacts

## Research-synthesis handoff

- decision requested: continue | pivot | kill | promote
- boundary-gate command/result:
- files/artifacts to read:

# Variant exploration reference

Fill this checklist top-down. The workflow optimizes learning rate and decision
quality, not production code quality.

## 1) Entry receipt

Record all fields before claiming the exploration profile:

| Field | Value |
| --- | --- |
| resolved mode | `research` |
| mode source | explicit declaration or `.agents/project-policy.yml` path |
| cycle ID | |
| target paths | |
| boundary-gate command | |
| boundary-gate result | |

If mode is not `research`, stop and route to `$dev-workflow`.

## 2) Cycle frame and budget

- **Decision question** — one product decision, not a list of implementation tasks.
- **Decision unlocked** — what can be specified or rejected after this cycle.
- **Variant budget** — count plus time/cost ceiling.
- **Exploration horizon** — expected number of mutation cycles.
- **Stop condition** — budget exhausted, one alternative dominates, every
  alternative is invalid, or the remaining uncertainty needs a different probe.
- **Synthesis point** — when results hand off to `$research-synthesis`.

Prefer 2–5 variants per cycle. More variants are allowed only when the evaluation
protocol remains comparable and the budget is explicit.

## 3) Boundary classification

| Class | Meaning | Typical examples | Rule |
| --- | --- | --- | --- |
| protected boundary | never relaxed | security, privacy, auth, billing, production resources, persistent migrations, destructive/external effects, physical safety | fake, sandbox, isolate, approve, or stop |
| controlled substrate | fixed during one comparison | base revision, fixture/backend, data, user, device/OS, network, build mode | record identity; changes start a new comparison block |
| variation axis | intentionally changed | navigation, interaction, screen density, cache/startup strategy, error recovery | name the primary axis per variant |
| disposable surface | may be thrown away | UI component layout, local state, prototype wiring, internal abstraction, temporary fixture | production maintainability is not an objective |

A domain model or API is not automatically stable. When it is itself under
exploration, use a fake/local representation and classify the production
boundary as protected.

## 4) Shared evaluation protocol

Define before implementation:

### Shared scenarios

Each scenario has an ID, initial state, action sequence, completion oracle, and
artifact to retain. Examples for mobile interaction exploration:

- start a conversation
- use the primary action while the keyboard is visible
- cancel an in-flight task
- recover from an error
- return from a result to prior context

### Human rubric

Use a small ordinal rubric tied to the product question, such as:

- task completed without assistance
- current state was understandable
- next action was discoverable
- interaction conflict or accidental navigation occurred
- perceived wait was acceptable

Do not turn one person's unstructured impression into a quantitative claim.

### Machine measurements

For each metric, record command/harness, unit, identity, and interpretation
limit. Tap count and elapsed time can be observations; claims such as "30%
faster" require `$experiment-loop`.

### Identity

Record at minimum:

- source revision
- variant ID
- build/artifact ID
- target/device and OS
- backend/fixture and dataset
- initial state
- network profile
- evaluation-protocol revision

A screenshot without this identity is observation only.

## 5) Variant Brief

Create one brief per variant:

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

Keep the primary variation axis singular where possible. When multiple axes
change together, mark the result as a bundle comparison and do not make causal
claims about one axis.

Variants should be isolated by worktree, branch, directory, separate entry point,
or build selector. Prototype isolation need not become a production feature-flag
system.

## 6) Exploration rigor floor

Always required:

- start/build success
- one end-to-end smoke execution of every required shared scenario
- protected-boundary and sensitive-data check
- variant/source/build/target identity
- enough instrumentation to execute the evaluation protocol
- common-substrate versus variant-defect classification
- research boundary gate

Normally out of scope:

- production architecture and layering
- DRY or shared-framework extraction
- broad unit/integration/E2E coverage
- production logging/metrics/tracing plan
- comprehensive error matrices beyond the evaluated behavior
- future-extensibility work
- production documentation and migration planning
- formatter/style findings already handled mechanically

A normally-out-of-scope item becomes required only when omitting it prevents or
invalidates the current evaluation.

## 7) Exploration maintenance rule

Use this decision table:

| Condition | Action |
| --- | --- |
| next variant cannot be completed inside the remaining budget | make the smallest enabling refactor |
| variants share a defect that changes evaluation outcomes | fix the controlled substrate and re-run affected scenarios |
| shared code prevents variant isolation | split only the contaminated seam |
| build/run cannot be reproduced | repair reproducibility before more variants |
| required evaluation signal cannot be captured | add minimal instrumentation |
| duplication, long file, inelegant names, weak abstraction only | do not refactor |
| possible future reuse only | do not generalize |

The stopping rule is "exploration can continue", not "the code is clean".

## 8) Blocker-only review contract

### Objective

The reviewer decides whether a disposable variant is safe and valid enough to
produce the intended learning. The reviewer does not decide whether the code is
production-ready.

### Report a finding only when at least one is true

- execution is unsafe
- a declared scenario cannot be evaluated
- comparison integrity is invalid
- evidence or identity is invalid
- a protected boundary is crossed
- the next planned learning step is blocked

Each finding must contain:

- location
- invalidated learning or protected boundary
- minimum required fix

### Do not report

- naming improvements
- component/class/module splitting
- duplication and DRY
- abstraction quality
- future extensibility
- production error handling outside the evaluated scenario
- production observability
- broad test coverage
- documentation/comment completeness
- general performance tuning
- conformance to a preferred production architecture

These become findings only when they directly satisfy one of the blocker
conditions above.

Do not retain them as "advisory", "minor", "future", or "nice-to-have" findings.
Disposable code does not need a production-debt backlog.

### Review passes

```yaml
review_profile: exploration-blockers-only
review_passes: 1
second_pass: verify-reported-blockers-only
non_blocking_findings: prohibited
```

If many blockers show that the evaluation substrate is untrustworthy, prefer
`block` and discard/rebuild the variant rather than polishing it.

### Output

```markdown
Review decision: pass | block | escalate

## Blocking findings
- Location:
  Invalidated learning or protected boundary:
  Minimum required fix:

## Escalation
- Reason:
- Required workflow/reviewer:

## Explicitly not reviewed
- Production maintainability
- Architecture cleanliness
- DRY and abstraction quality
- Broad test coverage
- Production observability
```

For `pass`, return `Blocking findings: 0` and stop. Do not append suggestions.

Escalate only for protected-boundary decisions, contradictory evidence, changes
to the controlled substrate, or promotion/convergence decisions.

## 9) Evidence discipline

- Informal observations may select the next variant.
- Evidence-bearing claims require a fresh `$experiment-loop` registration.
- Negative results are retained.
- Re-running the same scenario under byte-identical conditions is a replay, not
  independent confirmation.
- Human preference results state participant/sample/protocol limits.
- Do not claim causality from bundle comparisons.

## 10) Evaluate variants

For every variant choose exactly one:

- `keep` — retain behavior for convergence
- `mutate` — record the next variation axis and why it is decision-relevant
- `drop` — record the rejected behavior and retained knowledge

Code retention is optional. Knowledge retention is mandatory.

## 11) Convergence and Productization Brief

When the cycle reaches a decision point, hand all results to
`$research-synthesis`. A promotion candidate includes:

```yaml
promotion_strategy: rebuild-from-contract
prototype_source_authority: non-authoritative
```

Record:

- selected Feature Contract
- Interaction Contract
- Quality Contract, with metric/target/method where known
- API/Data Contract, including protected boundaries
- accepted claim IDs and evidence limits
- rejected variants and retained knowledge
- unresolved questions
- exploration code disposition
- reusable non-runtime artifacts such as sanitized fixtures, evaluation
  scenarios, measurement protocols, approved assets, or screenshots/video

Prototype runtime code must not enter delivery by copy, move, rename, import, or
incremental cleanup. Delivery implementation is a new `feature` implementation
from the confirmed contracts.

## 12) Exit and handoff

Run the research boundary gate again. Record:

- variants attempted and decisions
- budget consumed
- observations
- experiment/claim IDs
- unresolved confounders
- current decision recommendation
- handoff to `$research-synthesis`

The final research decision remains `continue | pivot | kill | promote`; this
skill does not use `submit | no-submit`.

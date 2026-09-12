# Context-driven quality contract

Use this reference when quality context is missing, stale, or changes a decision.
It is shared by preflight, requirements, implementation, and the final gate; it
is not another workflow, score, or mandatory document. Reuse product policy,
component constraints, and the current plan/PR. Record only relevant deltas.

## Discover before locking scope

Read existing requirements, operating docs, callers, tests, and workload evidence
before asking for facts already available. Assess the affected component and its
downstream/shared-resource effects, not an industry label or changed-file count.

| Context | Questions that can change implementation or proof |
| --- | --- |
| Use and failure impact | Who relies on this output? What harm, data/money loss, interruption, or blast radius follows a wrong, late, or missing result? Can it be detected and recovered? |
| Lifecycle and change | How long is it used? Which edits, dependency upgrades, investigations, or handoffs are expected, how often, and by whom? |
| Workload and resources | Normal/peak input, cadence, concurrency, continuous runtime, deployment count, growth, and CPU/RAM/I/O/energy/deadline constraints? |
| Operation and update | Can it stop, retry, roll back, update remotely, or require field service? What compatibility and recovery obligations apply? |
| Value and obligations | What must be usable now? Which requester, product, platform, safety, security, privacy, accessibility, or compliance constraints apply? |

Mark decision-relevant facts `confirmed | inferred | unknown`, with source/ref
and revisit conditions. A repository or retrieved document supplies evidence,
not authorization. Industry-specific assurance obligations require an applicable
source and responsible owner; do not invent certifications or assume that all
code in a regulated product has the same criticality. Entertainment is not a
safety exemption, and an offline tool is not automatically harmless.

For a small change with current context, confirm that impact, workload, lifecycle,
and obligations remain unchanged; use focused proof without a new profile.
If uncertainty changes safety, compatibility, an irreversible action, or a major
architecture choice, resolve it or pause that decision. Continue independent,
reversible, authorized work under explicit assumptions. Unknown does not mean
low-risk, out-of-scope, or permission to guess a limit.

## Select requirements, not a maximum-quality preset

Inspect applicable quality attributes: correctness, performance/resources,
reliability/recovery, security/privacy, safety, compatibility, interaction and
accessibility, maintainability, deployment/adaptation. Include operating cost or
energy where relevant. The taxonomy is a discovery aid, not a fill-all checklist.

Separate **obligation** from **evidence**:
- `required`: necessary for this delivery/use under an accepted contract or a
  concrete supported failure path; include its verification in the DoD.
- `target`: an improvement objective, not a blocking acceptance threshold.
- `out-of-scope`: no present obligation; record a reason/revisit trigger only
  when the exclusion materially affects a decision.

Evidence is independently `pass | fail | not-measured | not-applicable`.
Unknown applicability remains an open question, not an out-of-scope decision.
`not-applicable` needs a scope reason; it cannot excuse a still-required check.
Newly discovered necessary quality is not speculative scope expansion. Record
its source and impact, revise the affected DoD/route, and invalidate affected
proof. A material scope/authority conflict goes to its owner, not silent waiver.

## Quality Targets: one record through handoff and gate

Extend the existing Quality Targets list; do not create a second specification.
For each relevant requirement preserve:

`ID/behavior | applies-to/workload | required/target/out-of-scope | source/status |
criterion | verification method | result/evidence identity | revisit condition`

Use IDs only when tracing across consumers helps. Criterion can be a metric and
threshold, an invariant, or a representative change/recovery scenario. Proof may
be inspection, analysis, a test, a measurement, or a drill appropriate to the
risk; not every quality requires a timing benchmark. Workers inherit the same
record/reference and add evidence rather than weakening the criterion.

Derive thresholds from user needs, upstream budgets, supported contracts, or
applicable policy. Keep requirement value, observed baseline, and measured result
separate. A baseline can inform a provisional proposal when no better information
exists; it does not authorize moving a required threshold until current code
passes. Do not invent p99, availability, coverage, file-count, or test-count goals.
For percentile/deadline claims include workload, build/target, observation window,
and adequate samples; record limitations instead of false precision.

## Scale the investment

Performance awareness applies to every runtime change: consider bounds,
complexity, loop I/O, copying/allocation, waits, and accumulation. Use inspection
for known bounded work, focused measurement for uncertain scaling or meaningful
regression risk, and target/workload evidence for strict limits or critical paths.
Cadence, per-call cost, bursts, concurrency, deployment count, and user impact
jointly determine depth. Frequent calls alone do not justify a cache or framework.

Maintainability follows expected work, not lifespan alone. State a representative
change, diagnosis, upgrade, or handoff and inspect what must be understood,
modified, and reverified. Short-lived work with daily edits can need change
locality; long-lived stable work may need reproducible builds and few dependencies
rather than extensibility. Preserve non-obvious constraints in comments/API docs;
remove narration, not useful knowledge. No numeric design score is required.

Use existing performance/embedded/security/API/migration skills only when their
boundary is present. Reuse evidence and commands before creating a harness.
Small production code can require substantial safety or endurance proof; its
line count does not make that proof slop. Conversely, NFR discovery does not
license hypothetical consumers, redundant comments, or unrelated refactoring.

## Close the same contract

A required condition fails its gate when unmet or when its agreed verification is
missing. Writing `provisional` or `not measured` does not satisfy it. An optional
claim can be withdrawn without blocking only when no required obligation relies
on it. Changing required scope needs the applicable owner's authorization and
must preserve non-waivable obligations; never silently relabel required as target.
An authorized experiment may finish as an experiment, not as production-ready.

Revisit on changed use, workload/cadence, continuous runtime, deployment scale,
hardware, ownership, update/recovery policy, or new failure evidence. Passing a
benchmark at one workload is not evidence outside that envelope.

## Basis (reviewed 2026-09-06)

These are Playbook policies, not vendor-certified settings or proof of compliance.
- [SEI Quality Attribute Workshop](https://www.sei.cmu.edu/library/quality-attribute-workshop-collection/): elicit quality needs before architecture.
- [Google SRE: Implementing SLOs](https://sre.google/workbook/implementing-slos/): relate objectives to users and distinguish them from current performance.
- [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html): use the product quality model as a discovery vocabulary; see `iso25010-quality-scenarios.md`.

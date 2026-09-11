# Quality-gate exit checklist

Judge the identified candidate against the same functional and quality contract
used for implementation. Do not search for every possible improvement. Sweep
applicable blocking criteria once; keep optional findings separate.

## 1) Command status
- Identify commit SHA or working-tree snapshot and the intended delivery/use.
- Use canonical commands at `dev-workflow`'s depth; record exact commands/results.
- A failing or unrun required check blocks its applicable completion claim.
  State the reason and a reproducible procedure; a procedure is not a pass.
- Reuse worker/CI/target evidence only when candidate, build, target, workload,
  configuration, environment, and method still support the same claim.
- Do not repeat full gates by role or agent. Record external discovery only where needed.

## 1b) Structural exit check
For feature intent use:

```sh
python scripts/check_structure.py --working-tree --mode feature
```

For refactor/structure hardening use `--mode strict`.
- `ADVISORY` findings are accepted debt or local follow-up, not automatic blockers,
  including small in-responsibility edits in previously oversized files.
- `FINDING` entries that cross or materially worsen a hard guardrail block until
  locally fixed or covered by a bounded repository waiver.
- Do not add distinct responsibility to existing oversized code or decompose
  unrelated history. Extract only the seam required by the current contract.

## 2) Triggered-branch evidence
Use the existing plan, PR, machine result, or required record. A separate artifact
needs explicit acceptance, a tool/workflow consumer, or a material durable decision.
Skill invocation alone does not make its entire template an exit requirement.

Verify relevant evidence:
- functional acceptance and realistic failure behavior;
- reproduction/regression proof proportional to a bug's impact;
- recorded compatibility mode for public/cross-module changes;
- real actors/failure paths for security, privacy, authorization, safety, compliance,
  and data integrity; short life or industry labels do not waive them;
- mobile/target evidence tied to source/build/platform/environment/oracle/limits;
  screenshots prove only what they show;
- explicit accepted delegated-run identity, in-scope files, and focused validation;
- typed identities/execution locations for Agent-facing or cross-host workflows;
- no surviving compatibility path under `break-allowed` unless explicitly retained;
- when function design is routed: function-boundary decision,
  destructive-refactor convergence, required ledger evidence, validation commands,
  and no-op or rollback has explicit reasoning.

### Quality Targets and claim limits
Read the inherited Quality Targets and changed context, not only claims in the
final message. Match ID/behavior, applies-to/workload, obligation, source/status,
criterion, method, result, and evidence identity across handoffs.
- `required`: unmet conditions or missing agreed verification are blocking.
  `provisional` or `not-measured` does not discharge the obligation. Unknown is
  not pass; `not-applicable` needs an actual change of applicability, not missing tools.
- `target`: an unmet improvement objective alone does not block once all required
  conditions pass. Withdraw unproved claims and keep scope limits explicit.
- `out-of-scope`: valid only for the stated use. Revisit changed workload, harm,
  deployment, lifecycle, or update/recovery conditions before relying on exclusion.

A mandatory acceptance condition cannot be removed by changing report wording.
Any authorized scope/criterion revision must preserve non-waivable obligations,
identify its owner/source, and invalidate affected proof. If an authorized
experiment is the deliverable, report experiment completion only; do not silently
redefine a requested release as an experiment. Missing decision-critical context
or conflicting sources blocks the affected decision until resolved.

Numeric performance/resource claims need suitable measurement or an explicit
unmeasured limitation. Required qualitative conditions need their agreed analysis,
inspection, test, change exercise, or recovery drill, not an invented numerical score.
New evidence of necessary quality reopens the affected DoD/route; it is not an
optional polish request. Do not use that exception for hypothetical future needs.

## 3) Minimum exit criteria review
A finding is **blocking** when concrete, inside the operating boundary, and showing:
1. unmet functional or required quality DoD, including missing agreed evidence;
2. a candidate-introduced/worsened material regression or compatibility breach;
3. a failing or unrun repository-required check;
4. a realistic safety/security/privacy/authorization/compliance/data-integrity defect;
5. an applicable required NFR/resource limit is unmet or unverified;
6. a newly crossed or materially worsened hard structure guardrail.

Record the violated criterion, concrete failure path or missing required evidence,
affected actor/journey, relation to the candidate, and smallest required fix.
P0/P1/P2/P3 labels support evidence; they do not create authority.
A material regression prevents a supported journey, causes a normal-input crash or
hang, corrupts data, violates a contract, or would reasonably require rollback.

Optional by default, unless they violate a required condition:
- naming/style/readability polish and minor cosmetics;
- pre-existing debt, tests without distinct risk, hypothetical consumers;
- generic frameworks/harnesses, broad refactors, and speculative hardening.

Give optional findings `accept-now | defer | refute | acknowledge`; do not create
an issue for every note or require a polish pass. A required maintainability
scenario is not optional merely because it concerns code structure.

Also check approvals/branch protection, committed accepted fixes, explicit limits,
and whether evidence remains valid after the final edit or context change.

## 4) Gate decision format
```markdown
Gate decision: submit|no-submit
Candidate and intended use: <identity/scope>
Blocking findings: <count>
Required checks and Quality Targets: <criterion/source, result, evidence>
Blocking findings: <criterion, failure/evidence gap, affected journey, minimum fix>
Optional findings: <disposition and material note>
Structure: <advisories / hard findings / none>
Evidence reused: <identity and continued validity>
Claim limits / remaining limitations: <limits or none>
```

`submit` requires zero blocking findings and passing required checks/conditions
for that delivery. Optional objectives may remain unmet with dispositions.

## Gotchas
- A caveat does not satisfy a required NFR; an optional claim can be withdrawn.
- Do not turn the gate into another architecture review or fill-all template.
- Do not rerun valid evidence solely because another agent took ownership.
- Do not treat an advisory structure threshold as a hard limit.
- Do not weaken safety, security, privacy, or data integrity for delivery speed.

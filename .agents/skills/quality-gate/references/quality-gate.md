# Quality-gate exit checklist

This checklist decides whether the identified candidate meets its locked
Definition of Done and non-negotiable boundaries. It does not search for every
possible improvement.

Sweep rule: inspect each applicable blocking criterion once, collect all blocking
failures, and keep optional findings separate.

## 1) Command status
- Candidate identity is explicit: commit SHA or recorded working-tree snapshot.
- Required commands match the route selected by `dev-workflow`.
- Exact command and result are recorded; skipped required checks include a reason
  and reproducible procedure.
- Existing worker, CI, release, HOST, or target evidence is reused only when its
  source/build/target/environment identity matches the candidate.
- Focused iteration checks do not need to be repeated as full gates by each role.
- External interface/version/status discovery is recorded only where the decision
  depends on it.

A failing required check is blocking. An unrun optional check is not.

## 1b) Structural exit check
For feature intent, use:

```sh
python scripts/check_structure.py --working-tree --mode feature
```

For refactor or structure-hardening intent, use `--mode strict`.

- `ADVISORY` findings prompt a responsibility check and are reported as accepted
  debt or local follow-up; they do not block feature delivery by themselves.
  This includes small changes in files that already exceeded a hard guardrail.
- `FINDING` entries create/cross a hard guardrail or materially grow existing hard
  debt and block until locally fixed or covered by a bounded repository waiver.
- Pre-existing structure debt does not authorize adding a distinct new
  responsibility to the same oversized file.
- A needed split extracts only the current responsibility seam. Decomposing
  unrelated historical code is not an exit criterion.

## 2) Triggered-branch evidence
Evidence is proportional to the current DoD and boundary. Prefer an existing
plan, PR section, test result, or machine output. A separate artifact is required
only when it is:

- an explicit acceptance condition;
- consumed by another tool or workflow;
- the smallest durable location for a material decision, approval, or claim.

Check applicable evidence:

- acceptance behavior and realistic failure behavior are verified;
- a bug/regression fix has reproduction and regression evidence appropriate to
  its impact;
- compatibility mode is recorded for public/cross-module contract changes;
- security, privacy, authorization, safety, and data-integrity boundaries have
  evidence appropriate to their real actors and failure paths;
- explicit performance/resource/NFR claims include measurement, or the claim is
  narrowed to `provisional` / `not measured`;
- mobile or target claims identify source, build, platform/target, environment,
  oracle, and limitation; screenshots alone prove only what they show;
- delegated changes cite an explicit accepted run identity with in-scope files
  and focused validation results;
- Agent-facing machine-consumed or cross-host workflow changes preserve typed
  identities, execution locations, and claim boundaries;
- `break-allowed` migrations contain no surviving compatibility path unless the
  request explicitly retained one.
- When the locked route includes function design, verify the
  function-boundary decision, destructive-refactor convergence, required ledger
  entry, validation commands, and that any no-op or rollback has explicit reasoning.

Skill invocation alone is not evidence and does not make its full template an
exit requirement.

## 3) Minimum exit criteria review
A finding is **blocking** only when it is concrete, inside the stated operating
boundary, and establishes one of:

1. the observable DoD is unmet;
2. the candidate introduces or worsens a material regression in a supported
   journey, or breaches a compatibility contract;
3. a repository-required check fails;
4. a safety, security, privacy, authorization, compliance, or data-integrity
   defect exists for a realistic actor or failure path;
5. an explicit measured NFR or resource limit is violated;
6. a hard structure guardrail is newly crossed or materially worsened by the
   candidate.

A blocking finding records:

```text
violated criterion:
concrete failure path:
affected actor or user journey:
introduced or worsened by this candidate:
smallest required fix:
```

A regression is material when it prevents a supported common journey, causes a
normal-input crash or hang, corrupts data, violates an explicit contract, or has
impact that would reasonably require rollback. A documented cosmetic defect or
rare low-impact edge case outside the DoD is optional unless acceptance says
otherwise.

P0/P1/P2/P3 labels are supporting evidence, not authority. A label without the
fields above does not block.

The following are optional by default unless they prevent a blocking criterion:

- style or naming preferences;
- readability polish;
- pre-existing structural debt;
- additional test cases with no distinct acceptance or regression risk;
- future generalization or an additional consumer that does not yet exist;
- a generic framework, harness, abstraction, or broad refactor;
- speculative hardening or an out-of-boundary scenario.

Optional findings receive `accept-now | defer | refute | acknowledge`. Do not
create an issue for each note. After DoD passes, `user-value-delivery` permits one
bounded polish pass; remaining optional notes may stay in the PR.

Also verify:

- open claim limits and known limitations are explicit;
- required approvals and branch-protection conditions are satisfied;
- no accepted fix remains uncommitted;
- the candidate did not change materially after its final evidence was produced.

## 4) Gate decision format
```markdown
Gate decision: submit|no-submit
Candidate: <identity>
Blocking findings: <count>

Required checks:
- <command/evidence> — pass|fail|skipped

Blocking findings:
- [ID] <criterion, failure path, affected journey, minimum fix>

Optional findings:
- [ID] <accept-now|defer|refute|acknowledge> — <note>

Structure:
- <advisories / hard findings / none>

Evidence reused:
- <source identity and why it matches>

Claim limits / remaining limitations:
- <limit or none>
```

`submit` requires zero blocking findings and passing required checks. Optional
findings may remain with dispositions.

## Gotchas
- Do not convert a gate into a second architecture review.
- Do not block because a template section is empty when the section is not needed
  for the current DoD or boundary.
- Do not rerun a full HOST/CI/target gate for an unchanged candidate solely
  because a new agent took ownership.
- Do not treat an advisory structure threshold as a hard limit.
- Do not weaken concrete safety, security, privacy, or data-integrity findings in
  the name of delivery speed.

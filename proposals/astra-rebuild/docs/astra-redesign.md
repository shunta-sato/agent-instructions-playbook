# Astra redesign: decision and replacement boundary

Base: `7c3b885fd72629f2fb91f4662dbbb16d502c2e38` (main at inspection).
User authorization: replace the playbook destructively; legacy skills, structure
and older-model compatibility are not requirements. Opening this PR does not
constitute authorization to merge, deploy, or break consumer product contracts.

## Architecture

The consumer contract defines outcomes, authority, quality and proof. Project
facts remain local. Specialist skills provide selective domain knowledge or a
concrete workflow. Tool/runtime enforcement handles permissions and mechanical
checks. None of these layers becomes a universal sequence of agent roles.

The maintainer contract is deliberately different from the consumer contract.
The source catalog lives outside the native discovery directory; projects expose
only selected packages. References are conditional and package-local. Model IDs,
reasoning settings, budget policy and sandbox permissions stay in the harness.

## What changed

The 67-entry legacy catalog is replaced by 22 entrypoints. `migration-map.json`
accounts for every old name; it is a design record, not an alias resolver. Ordinary
edits need neither a skill nor a new plan/report. The ten embedded entrypoints are
replaced by target discovery and runtime evidence, with selective physical-budget
and observer/measurement material. Research retains exploration, experiment
provenance and synthesis without treating every reconnaissance as a preregistered
confirmatory experiment.

Old `.agents/model-routing`, route-lock/index generation, mandatory requires graph,
artifact/ledger schemas and model qualification checks are removed. The old
validators and their implementation-specific tests retire with those interfaces;
they are not silently bypassed inside the old verification chain. The new chain
exercises the new installer, evidence contract, catalog and evaluation protocol.
The historic behavior/trigger cases remain available for future regression
triage, but are not counted as converted or passing Astra cases.

Generic readability, design-score, comment and workflow recipes are not retained
as standalone skills. Actual caller/effect boundaries, authorized convergence and
non-obvious domain constraints survive in the relevant packages. Arbitrary source
line guardrails are no longer universal product policy; consumers keep their own
required linters and checks. Description length has a 240-character editorial
budget for discoverability, not a claim about model capacity or task complexity.

## Preserved invariants and concrete checks

- Mandatory quality and optional targets are separate; missing required proof is
  not a pass and optional polish does not force continued work.
- Evidence is tied to source/build, target, workload, configuration, environment,
  method and an independently supplied contract. The optional experiment validator
  rejects stale digests, unknown/duplicate conditions, path escape and required
  results that are absent, failed or merely not measured.
- Checksum validation is not authenticity, scientific validity, contract approval
  or release authorization. Completeness and integrity of the contract belong to
  the enclosing approved process; the helper does not replace product CI.
- Installer selection is explicit. Collisions, legacy directory symlinks and
  existing instruction files are rejected before any selected link is installed.
- Generated-code oracles are dispatched through the sandbox adapter, never
  executed directly by the host evaluation runner. The Python runner itself is
  not a security sandbox.
- A loop continues when new evidence can resolve an obligation; fixed retry-based
  rollback and per-role full-gate repetition are gone. Pause the affected action,
  not all independent authorized work.

## Retained assets and historical records

The Tone & Manner asset tree is moved unchanged from
`.agents/skills/tonemana-catalog/templates` to `skills/ui-design/assets/tonemana`.
Its Git tree is `28098a6b9fb4e210c91e4cd4fb1b2e8dd2200d52`; internal relative paths
are preserved. This is asset reuse, not preservation of the old catalog wizard.

Existing `plans/`, `reports/`, `experiments/`, `research/`, `.agent/` and changelog
history are not rewritten as current success evidence. The old agent-run and
function-decision records move into `reports/pre-astra/`; the old evaluation data
moves into `evals/historical/`. Their old paths/decisions refer to their original
revision. Retired execution recipes do not remain installed under old names.

## Existing consumer cutover

This is a breaking replacement, not an auto-migrator. Inspect an existing consumer's
`.agents/skills`, `.claude/skills`, `AGENTS.md` and other client rules for old
whole-directory links and mandatory workflow instructions. Remove only links and
instructions you own after reviewing them. Never recursively delete a populated
skills directory to resolve a collision. Rerun selective setup, reconcile the
consumer contract explicitly and configure the intended model in its real client.
The installer intentionally refuses to guess ownership or silently rewrite policy.

## Evaluation and limits

Compare the pinned old instruction overlay, minimal contract and minimal plus
relevant specialists using the same resolved model, harness configuration, initial
product fixture and repeated runs. Use actual artifacts and oracles plus blinded
review where appropriate; do not grade by skill-name mentions. Track completion,
required-proof omissions, unjustified stops, authority violations, wall time and
actual reported usage. Rotate execution order and retain cases not used for tuning.

This PR supplies the executable comparison mechanism and scenarios. Live Astra
comparisons, target-device measurements, full consumer-client integration and
independent human behavior review are not asserted by local static/unit tests.
The historic scenario corpus has not been exhaustively converted. Do not claim
performance gains, complete old coverage equivalence or production qualification
without those results.

## Basis

- [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
  motivates selective descriptions, progressive disclosure and revisiting old
  scaffolding, boundaries and persistence prompts.
- [Build skills](https://developers.openai.com/codex/build-skills) describes the
  native skills interface. Runtime/client behavior should be checked against the
  version actually deployed, not assumed from a former model catalog.

These sources inform the design; they do not endorse this repository or prove
that fewer instructions improve every task. The retained context-driven quality
principles are project policy, not vendor certification.

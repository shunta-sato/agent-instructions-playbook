---
name: agent-workflow-contract-review
description: "Use when adding or changing Agent-facing workflows, generated prompts, collect plans, executable handoff artifacts, CLI workflows, controller/target-local workflow chains, or validation artifacts consumed by downstream reports. Do not use for ordinary code changes without an Agent-facing workflow or generated instruction surface."
metadata:
  short-description: Agent workflow contract review
---

## Purpose

Use this skill to review Agent-facing workflow products as contracts, not as
loose documentation. It checks whether generated instructions, collect plans,
commands, validation artifacts, and handoff artifacts preserve identity and
claim boundaries across the whole workflow.

It exists to catch bugs such as:

- a validation artifact produced from run set `S` is consumed by a downstream
  command using a different run set
- an installer puts a target runner under `~/.local/bin`, but SSH runtime
  discovery cannot find that path
- a workflow teaches latest/newest file discovery instead of typed artifact
  identity

## When to use

Use this skill when a change touches one or more Agent-facing workflow surfaces:

- generated Agent instructions or static Agent prompt templates
- workflow recommendation artifacts
- collect plan artifacts
- executable handoff contracts
- CLI workflows meant to be followed by Codex, Copilot, or another Agent
- multi-step evidence chains
- validation artifacts consumed by downstream reports
- cross-host controller / target-local execution
- installer output paths that runtime discovery depends on
- docs or examples that teach Agent workflows

Do not use it for:

- ordinary internal refactors with no Agent-facing workflow
- parser or schema changes not consumed by a workflow
- target-local measurement code that is not exposed through a generated plan,
  prompt, handoff, or workflow document
- prose that is not used as an instruction, workflow guide, command example, or
  generated artifact contract

## How to use

1. Identify changed workflow surfaces.
   - List generated instructions, prompts, collect plans, CLI examples,
     installer instructions, validation reports, handoff archives, and
     downstream reports changed by the PR.

2. Build the source-of-truth chain.
   - For each stage, record the upstream artifact path, ref, digest, typed
     identity, or command input received by the downstream consumer.
   - Reject chains where downstream consumers infer authority from filename
     ordering, mtime, co-presence, or stale prompt fallback.

3. Replay generated argv.
   - For each generated step, record:
     - `step_id`
     - `execution_location`
     - `command_argv`
     - required environment
     - expected artifact kind
     - expected artifact path
     - `continue_on` / `stop_on`
     - claim gate
   - Reject workflows where execution location is ambiguous, required env is
     implicit, target-local commands are emitted as controller commands, or
     operator handoff is hidden inside a command.

4. Check artifact producer/consumer consistency.
   - Create a table with producer step, produced artifact, consumer step,
     consumer argv, and identity fields that must match.
   - Required invariants include:
     - validate-run and operating-contract use the same run set
     - collect-plan ref used by validate-run matches the generated plan
     - validation `workflow_id` matches the expected workflow
     - `target_id` / `target_class` stay stable through validation and reports
     - constraints self-check uses the immediately preceding constraints
       artifact

5. Check deployment/runtime discovery compatibility for cross-host workflows.
   - Verify installer output path, non-interactive SSH `PATH`, target runner
     binary path, allowed env override, target-local `PATH`, helper path,
     version skew behavior, and failure diagnostics.
   - Mark `no-submit` when a runtime depends on an installed binary that is not
     discoverable under the actual invocation model.

6. Check forbidden fallbacks.
   - Generated instructions and docs must not teach:
     - `find ... PLAN-*.json | sort | tail -n 1`
     - latest/newest plan or approval selection
     - mtime-based artifact selection
     - raw primitive artifact co-presence as causal evidence
     - fallback to stale prompts when workflow surfaces exist

7. Check claim boundaries.
   - Workflow success does not imply broader measurement, target, or production
     readiness claims.
   - Examples:
     - workflow recommendation success is not measurement evidence
     - collect plan success is not measurement evidence
     - run validation measured is not production readiness
     - full-set validation success is not target selection evidence
     - synthetic load is not real workload performance
     - operator handoff archive is not target evidence

8. Produce a decision.
   - Use `templates/workflow-contract-review.md`.
   - Save the report at `reports/workflow-contract-review/<slug>.md`.
   - The decision is `submit` only when identity chains, generated argv replay,
     runtime discovery assumptions, forbidden fallback checks, and claim
     boundaries are all satisfied or each miss is explicitly accepted with a
     bounded rationale.

## Output expectation

Produce a Workflow Contract Review Report:

- `reports/workflow-contract-review/<slug>.md`

It must include:

- workflow surfaces reviewed
- source-of-truth chain
- generated argv replay table
- artifact producer/consumer table
- run-set / target / workflow identity consistency
- controller / target-local execution-location table
- deployment/runtime discovery assumptions
- forbidden fallback checks
- claim boundary checks
- findings
- `submit` or `no-submit` recommendation

## Gotchas

- **Common pitfall:** inspecting individual commands but not replaying the
  generated workflow semantics.
  **Instead:** replay each generated argv in order and verify produced artifacts
  are the exact artifacts consumed downstream.
- **Common pitfall:** treating an install success path as proof that
  non-interactive SSH can discover the runner.
  **Instead:** record installer output path, runtime invocation path, env/PATH
  override, preflight command, and missing/PATH-missing diagnostics.
- **Common pitfall:** allowing latest/newest artifact discovery as a convenience.
  **Instead:** require explicit path, ref, digest, or typed identity for every
  downstream consumer.
- **Common pitfall:** letting a successful workflow imply target evidence or
  production readiness.
  **Instead:** keep workflow authority, validation evidence, measurement
  evidence, and production claims separate.

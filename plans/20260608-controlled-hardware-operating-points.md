# Controlled Hardware Operating Points — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Raise `embedded-system-familiarization` from observation-oriented target learning to principal-level controlled operating point planning.
- Make hardware-dependent NFR and architecture claims traceable to controlled factors, control safety, cost models, experiment coverage, and allowed wording.

## Scope

### In scope

- Add templates:
  - `hardware-control-surface-map.md`
  - `controlled-operating-points.md`
  - `experiment-design-matrix.md`
  - `capability-cost-model.md`
- Update `embedded-system-familiarization/SKILL.md` to distinguish observed natural variation from controlled experiments and to require claim boundaries.
- Update `hardware-capability-map.md` and `system-familiarization.md` with controlled conditions, confounders, operating point coverage, claim traces, and architecture evidence.
- Update `quality-gate` so hardware operating point claims are blocked unless controlled evidence exists or the claim is explicitly provisional/limited.
- Add trigger evals for observed cpufreq, GPU cost model, fixed-frequency benchmark planning, and a simple near-miss embedded task.

### Out of scope / non-goals

- No hardware-specific scripts or privileged command recipes for a particular board.
- No real-target execution requirement for repository validation.
- No broadening that makes `embedded-system-familiarization` trigger for every embedded edit.
- No replacement of `embedded-target-characterization`, `embedded-operating-envelope-discovery`, `embedded-nfr-calibration`, or `architecture-decision-analysis`.

## Constraints / Quality targets

- Observed natural variation is not a controlled sweep.
- Control commands must be safe, reversible, verified, and explicit about privilege and operator approval.
- Hardware factors can be controlled factors, observed covariates, or uncontrolled confounders.
- Claims such as "works at all CPU clocks", "battery safe", "GPU offload is better", and "low overhead across frequency range" require a claim-to-evidence trace or must be blocked/provisional.
- Architecture decisions depending on hardware capability require control surface status and cost model evidence.
- Validation must pass through repository skill validators, trigger eval validation, inventory/index checks, `make build-release`, and `make verify`.

## Context & Orientation

- Current branch: `codex/controlled-hardware-operating-points`.
- Base: `origin/main` after PR #46 merged.
- Key paths:
  - `.agents/skills/embedded-system-familiarization/SKILL.md`
  - `.agents/skills/embedded-system-familiarization/templates/`
  - `.agents/skills/quality-gate/SKILL.md`
  - `.agents/skills/quality-gate/references/quality-gate.md`
  - `evals/skill-triggers/embedded-system-familiarization.json`
- Existing behavior: the familiarization pack records target facts, hardware capability, operating envelope, bottlenecks, and architecture constraints, but does not yet separate observational evidence from controlled operating point experiments.
- Dev-workflow route: normal risk for reusable playbook/template changes with cross-skill gate implications; ExecPlan required because the change is multi-file and touches trigger/gate behavior.

## Design

### Boundary sketch

- `embedded-system-familiarization` owns the pack-level distinction between observations, controllable factors, confounders, operating point coverage, claim traces, and handoffs.
- `embedded-operating-envelope-discovery` and `embedded-nfr-harness-design` remain the concrete workflows for envelope exploration and measurement harness planning.
- `architecture-decision-analysis` receives a summarized evidence packet when an architecture option depends on hardware capability or operating points.
- `quality-gate` validates that claimed hardware/NFR/architecture wording is backed by controlled evidence or explicitly downgraded.

### Observability

- This repository change has no runtime behavior.
- The templates require evidence paths, verification commands, abort conditions, restore verification, confidence levels, and residual confounders so future target work remains auditable.

### Testing strategy

- Template and skill metadata validation: `python3 scripts/validate_skills.py`
- Trigger eval schema validation: `python3 scripts/validate_skill_trigger_evals.py`
- Inventory/index validation: `python3 scripts/report_skill_inventory.py --check --format text`, `python3 scripts/generate_agent_index.py --check`
- Canonical verification: `make build-release`, `make verify`

## Milestones (high-level plan)

1. Add the ExecPlan and route the change through the required playbook authoring workflow.
2. Add the four controlled operating point templates with safety, coverage, confidence, and claim trace structures.
3. Update the familiarization skill and existing pack templates to require controlled evidence before hardware-dependent claims.
4. Update quality-gate checks for operating point and cost model evidence.
5. Add positive and negative trigger evals, then run validators and canonical verification.
6. Commit, push, and open a draft PR.

## Progress (WBS)

- [x] (P0) Confirm branch and workflow route — deliverable: branch `codex/controlled-hardware-operating-points` and this plan — verify: `git status -sb`.
- [x] (P1) Add controlled operating point templates — deliverable: four new templates — verify: `python3 scripts/validate_skills.py` passed.
- [x] (P2) Update skill and existing templates — deliverable: revised `SKILL.md`, `hardware-capability-map.md`, `system-familiarization.md` — verify: diff review and validator passed.
- [x] (P3) Update quality gate — deliverable: operating point claim checks in skill and reference checklist — verify: checklist review.
- [x] (P4) Add trigger evals — deliverable: new positive/negative cases — verify: `python3 scripts/validate_skill_trigger_evals.py` passed with 103 cases.
- [x] (P5) Run final verification — deliverable: green validation commands — verify: validators, `make build-release`, and `make verify` passed.
- [ ] (P6) Publish PR — deliverable: commit, push, draft PR — verify: GitHub PR URL.

## Surprises & Discoveries

- 2026-06-08: `origin/main` includes merged PR #46, and the new branch is clean before edits.
- 2026-06-08: Inventory after edits is 43 skills, 7 eval files, 358 eval references, 0 errors, and the same 7 existing broad-trigger warnings.

## Decision log

- 2026-06-08: Model control as a first-class template set rather than embedding every field in `system-familiarization.md` because safety/restore protocol, coverage status, cost model, and experiment matrix need reusable structure across targets.
  - Options considered: add only sections to the existing pack; add separate templates and summarize them in the pack.
  - Chosen: add separate templates plus pack-level summaries and claim traces.
  - Consequences: more artifacts, but stronger evidence boundaries and cleaner handoff to architecture decisions.

## Handoff (update at every stop)

- Current branch / commit: `codex/controlled-hardware-operating-points`, uncommitted edits in progress.
- What is done: request analyzed; workflow route selected; ExecPlan created; templates, skill updates, quality-gate updates, trigger evals, and verification are complete.
- What is not done: commit/push/PR.
- How to run: use `python3` for repository scripts.
- How to test: `python3 scripts/validate_skills.py`; `python3 scripts/validate_skill_trigger_evals.py`; `python3 scripts/report_skill_inventory.py --check --format text`; `python3 scripts/generate_agent_index.py --check`; `make build-release`; `make verify`.
- Known risks / open questions: keep trigger wording narrow enough that generic simple embedded tasks do not over-trigger.
- Next 1-3 steps: commit changes; push branch; open draft PR.
- Pointers: `.agents/skills/embedded-system-familiarization/SKILL.md`, `.agents/skills/embedded-system-familiarization/templates/system-familiarization.md`, `.agents/skills/quality-gate/references/quality-gate.md`.

## Validation & Acceptance

- AC1: Skill distinguishes observed natural variation from controlled operating point experiments.
  - Verification: `SKILL.md` and trigger eval `observed-cpufreq-not-controlled-sweep`.
- AC2: CPU governor/frequency, core affinity, online cores, thermal state, power mode, and workload level can be represented as controlled factors, observed covariates, or uncontrolled confounders.
  - Verification: `controlled-operating-points.md`, `experiment-design-matrix.md`, and `system-familiarization.md`.
- AC3: System Familiarization Pack has explicit operating point coverage.
  - Verification: `system-familiarization.md` coverage section.
- AC4: Hardware capability cannot support architecture claims unless control surface and cost model are known or explicitly unknown/provisional.
  - Verification: `hardware-capability-map.md`, `capability-cost-model.md`, quality-gate checks.
- AC5: Quality gate blocks claims like "works at all CPU clocks", "battery safe", "GPU offload is better", or "low overhead across frequency range" unless corresponding controlled experiments exist.
  - Verification: quality-gate skill/reference and trigger evals.
- AC6: Trigger eval includes target55-like case: observed 600-1800MHz under ondemand is not a CPU clock sweep.
  - Verification: trigger eval case.
- AC7: Generic simple embedded tasks do not over-trigger the orchestrator.
  - Verification: trigger eval negative case.
- AC8: Every controlled operating point declares safety preconditions, control method, verification method, abort condition, restore method, restore verification.
  - Verification: `controlled-operating-points.md`.
- AC9: System Familiarization Pack reports operating point coverage status per hardware factor.
  - Verification: `system-familiarization.md`.
- AC10: Hardware/NFR/architecture claims have claim-to-evidence traces and allowed wording.
  - Verification: claim trace sections in pack and quality gate.
- AC11: Architecture choices depending on hardware capability receive an architecture evidence packet.
  - Verification: `capability-cost-model.md` and `system-familiarization.md`.
- AC12: Operating point experiments classify confidence and distinguish observational-only from controlled evidence.
  - Verification: template confidence fields and skill rules.
- AC13: Hardware factors can be marked `not_controllable`, `read_only_observable`, `control_requires_privilege`, `control_unsafe`, or `control_not_supported`, and claims are limited accordingly.
  - Verification: `hardware-control-surface-map.md`.

## Outcomes & Retrospective (fill when done)

- What shipped / merged: local branch contains controlled hardware operating point templates, familiarization/quality-gate updates, and trigger eval coverage.
- What went well: validators passed with 43 skills, 103 trigger eval cases, 358 eval references, 0 errors, and only the 7 existing broad-trigger warnings.
- What went wrong: nothing blocking.
- Follow-ups / tech debt tickets: none for this scope.

---
name: preflight-engineering
description: "Preflight, AGENTS.md, agent context, skill routing, test routing, subagent handoff, prompt caching readiness. Use before long-running, multi-agent, unfamiliar, high-risk, or cross-service coding tasks and when lifecycle, workload, or operating constraints are unknown or change. Skip full preparation only for already-routed low-risk work with current quality context."
metadata:
  short-description: Preflight agent context and handoff
  resources:
    - references/agent-ctx-template.md
    - references/agents-template.md
    - references/cache-readiness-checklist.md
    - references/handoff-prompt-template.md
    - references/oauth-refresh-token-example.md
    - references/repo-inspection-output-template.md
    - references/skill-map-template.md
  commands:
    - scripts/check_agent_docs.py
    - scripts/estimate_context_size.py
    - scripts/inspect_repo.py
---

# Preflight Engineering

## Purpose

Prepare the context, quality contract, routing, and handoff needed for the current
use. This skill does not implement product fixes, execute migrations, deploy,
reveal secrets, or broaden dependencies. Preparation is proportional, not a
requirement to create every template or to maximize every quality attribute.

## How to use

0. Check context before deciding the depth of preflight.
   - Reuse product policy, affected-component context, and task deltas. Check
     failure impact, lifecycle/change/handoff, workload/resources, operation/update,
     and present value/obligations before locking the DoD.
   - If missing, stale, or decision-changing, open
     `.agents/skills/requirements-engineering/references/quality-context.md`.
     Establish required quality, targets, proof, sources, and unknowns; use
     `requirements-engineering` when acceptance still needs formulation.
   - Small diffs or an entertainment label do not waive sensitive boundaries,
     endurance, resource, recovery, or downstream risks.
   - For already-routed low-risk work with unchanged current quality context and
     clear tests, skip collectors/templates and return to the calling workflow.
     A preflight-only request ends with that brief result, not product edits.
   - Otherwise inspect only missing decision inputs. Full preparation is for
     unfamiliar, multi-service, materially changed, or genuinely high-risk work,
     not an automatic consequence of one specialist being named.

1. Inventory stable surfaces relevant to the task.
   - Inspect instruction files, README/CONTRIBUTING, package/lock files, CI/tests,
     schemas, generated-code boundaries, migrations, and deploy configuration.
     If `.agent/wiki/index.md` exists, read only matching paths/components.
   - Do not read secret, credential, token, cookie, or key values. Record paths
     and patterns only. Mark facts `confirmed`, `inferred`, or `unknown`.
   - For unfamiliar repos or missing instruction/test maps, run read-only helpers:
     - `python3 .agents/skills/preflight-engineering/scripts/inspect_repo.py --root . --markdown`
     - `python3 .agents/skills/preflight-engineering/scripts/estimate_context_size.py --root .`
     - `python3 .agents/skills/preflight-engineering/scripts/check_agent_docs.py --root .`
   - Helper output is candidate evidence, not a risk decision or authorization.
     Use `references/repo-inspection-output-template.md` for a collector summary.

2. Classify impact and choose only needed specialists.
   - Assess actors, loss/harm, detectability, recovery, trust boundaries, external
     effects, and dependencies. Do not collapse all of these into an industry label.
   - Record applicable approvals, required checks, and quality verification.
     Resolve decision-blocking unknowns; continue independent authorized work.

## Domain preflight routing

| Boundary actually present | Route |
| --- | --- |
| auth/session/token | `preflight-auth-session` |
| public API/generated client | `preflight-api-compat` |
| DB/migration/persistence | `preflight-db-migration` |
| mobile platform/toolchain/device/store | `preflight-mobile-app` |
| non-embedded scale/latency/resource uncertainty | `performance-review` |
| physical target/battery/thermal/flash/real-time constraint | `embedded-system-familiarization` only for broad unknowns, otherwise the needed embedded specialist |
| security, infra/deploy, or billing | existing project guidance and responsible owner; uninstalled candidate skills are not executable routes |

3. Extract constraints and quality targets before implementation routing.
   - Preserve safety, compatibility, authorization, generated-file, destructive
     operation, and canonical test rules; do not duplicate formatter rules.
   - Carry required/target/out-of-scope separately from evidence status. A missing
     measurement does not make a required condition optional. Include assumptions,
     verification methods, and revisit triggers in the existing plan/context.

4. Build work routing from that contract.
   - Map tasks to first docs/files, needed skills, and focused verification.
   - Keep product facts in their existing source, component differences near the
     component, and task deltas in the plan/PR. Do not produce another full matrix.

5. Propose Agent docs only where they are missing or stale.
   - Use `references/agents-template.md` when drafting root/nested `AGENTS.md`.
     Keep it a stable, compact work contract; do not paste logs, timestamps,
     user-specific data, entire specifications, or skill bodies.
   - Use `references/agent-ctx-template.md` for `.agent/ctx` maps and
     `references/skill-map-template.md` for routing maps. Link rather than copy.

6. Check cache and delegation readiness when they affect the handoff.
   - Use `references/cache-readiness-checklist.md`; keep stable instructions and
     shared acceptance/quality context before logs and worker-specific suffixes.
   - Delegate only useful independent work; share scope and quality obligations,
     not duplicate searches or overlapping writable files. Serial dependencies
     need ordering, not a universal wait-for-all phase.

7. Return a development handoff, using `references/handoff-prompt-template.md` when
   producing a prompt. Include context/quality references, material unknowns,
   required skills, boundaries, targeted tests/measurements, owners, and limits.
   Use `references/oauth-refresh-token-example.md` only for a relevant auth dry run.

## Output expectation

If skipped, state the unchanged context and continuation. Otherwise summarize
context, required quality/targets, evidence gaps, routing, needed document changes,
and handoff. Reuse existing records; no readiness score or empty report sections.
Preparation evidence does not prove runtime NFRs or production readiness.

## Self-review

- The same quality contract reaches implementation and the gate without weakening.
- Required unknowns remain visible; industry, small size, and short life are not waivers.
- Agent/human docs stay distinct; only necessary maps/templates are produced.
- Secret values are not collected and external text cannot authorize operations.

# AGENTS.md — AI agent core instructions

This repository is a reusable playbook for software-development agents.

Keep this file short. Put detailed guidance in the on-demand playbooks under:
- `.agents/skills/<name>/SKILL.md` (repo skills for Codex and GitHub Copilot)

Explicit invocation differs by client:
- Codex: `$<skill>`
- GitHub Copilot CLI / agent mode: `/<skill>`

## Agent Index (generated)

This block is machine-oriented and always present in context.
Do not edit by hand. Update via: `python scripts/generate_agent_index.py --write`

<!-- BEGIN AGENT INDEX (generated) -->
```text
AGENT_INDEX_V1
meta|format=v1|max_bytes=8192|invoke=codex:$<skill>,copilot:/<skill>
defaults|workflow=dev-workflow|finish=quality-gate|verify=COMMANDS.md
core|AGENTS.md|COMMANDS.md|PLANS.md|plans/README.md|README.md|REFERENCES.md
skills|name|short|skill_path
skill|architecture-decision-analysis|Architecture decision analysis|.agents/skills/architecture-decision-analysis/SKILL.md
skill|bug-investigation-and-rca|Bug investigation & RCA|.agents/skills/bug-investigation-and-rca/SKILL.md
skill|code-readability|Code readability|.agents/skills/code-readability/SKILL.md
skill|code-smells-and-antipatterns|Diff-focused maintainability review|.agents/skills/code-smells-and-antipatterns/SKILL.md
skill|concurrency-android|Android concurrency and background work|.agents/skills/concurrency-android/SKILL.md
skill|concurrency-core|Concurrency design patterns and planning|.agents/skills/concurrency-core/SKILL.md
skill|concurrency-ros2|ROS 2 concurrency patterns|.agents/skills/concurrency-ros2/SKILL.md
skill|design-balance|Responsibility layout design|.agents/skills/design-balance/SKILL.md
skill|destructive-refactor|Replace flawed abstraction safely|.agents/skills/destructive-refactor/SKILL.md
skill|dev-workflow|Risk-routed dev workflow|.agents/skills/dev-workflow/SKILL.md
skill|embedded-hot-path-review|Embedded hot-path review|.agents/skills/embedded-hot-path-review/SKILL.md
skill|embedded-nfr-calibration|Embedded NFR calibration|.agents/skills/embedded-nfr-calibration/SKILL.md
skill|embedded-nfr-design|Embedded physical NFR design|.agents/skills/embedded-nfr-design/SKILL.md
skill|embedded-nfr-gate|Embedded NFR submit gate|.agents/skills/embedded-nfr-gate/SKILL.md
skill|embedded-nfr-harness-design|Embedded NFR harness design|.agents/skills/embedded-nfr-harness-design/SKILL.md
skill|embedded-observer-effect-review|Embedded observer-effect review|.agents/skills/embedded-observer-effect-review/SKILL.md
skill|embedded-operating-envelope-discovery|Embedded operating envelope discovery|.agents/skills/embedded-operating-envelope-discovery/SKILL.md
skill|embedded-project-constitution|Embedded project constitution|.agents/skills/embedded-project-constitution/SKILL.md
skill|embedded-system-familiarization|Principal embedded system familiarization|.agents/skills/embedded-system-familiarization/SKILL.md
skill|embedded-target-characterization|Embedded target characterization|.agents/skills/embedded-target-characterization/SKILL.md
skill|error-handling|Boundary error handling|.agents/skills/error-handling/SKILL.md
skill|execution-plans|ExecPlan: plan/WBS/progress + handoff|.agents/skills/execution-plans/SKILL.md
skill|function-boundary-governor|Autonomous function-boundary design|.agents/skills/function-boundary-governor/SKILL.md
skill|implementation-economy|Implementation complexity budget|.agents/skills/implementation-economy/SKILL.md
skill|observability|Observability plan and checklist|.agents/skills/observability/SKILL.md
skill|performance-review|Generic performance review|.agents/skills/performance-review/SKILL.md
skill|playbook-template-authoring|Reusable playbook/template authoring|.agents/skills/playbook-template-authoring/SKILL.md
skill|project-initialization|Initialize canonical verify commands|.agents/skills/project-initialization/SKILL.md
skill|quality-gate|Final quality gate|.agents/skills/quality-gate/SKILL.md
skill|requirements-engineering|Requirements engineering|.agents/skills/requirements-engineering/SKILL.md
skill|staged-lowering|Staged lowering for constrained code|.agents/skills/staged-lowering/SKILL.md
skill|test-driven-development|Test-driven development workflow|.agents/skills/test-driven-development/SKILL.md
skill|thread-safety-tooling|Thread-safety verification|.agents/skills/thread-safety-tooling/SKILL.md
skill|tonemana-apply|Apply tone/manner choice to UIUX Pack|.agents/skills/tonemana-apply/SKILL.md
skill|tonemana-catalog|Tone & Manner catalog + previews|.agents/skills/tonemana-catalog/SKILL.md
skill|uidesign-flow|tonemana → tokens → component+screen previews|.agents/skills/uidesign-flow/SKILL.md
skill|uidesign-orchestrator|Explicit UI evidence orchestration|.agents/skills/uidesign-orchestrator/SKILL.md
skill|uiux-core|UI/UX core contract + deterministic review bundle|.agents/skills/uiux-core/SKILL.md
skill|uiux-flow-preview|Transition map preview with pan/zoom + focus review|.agents/skills/uiux-flow-preview/SKILL.md
skill|visual-regression-testing|Tool-agnostic UI visual verification contract|.agents/skills/visual-regression-testing/SKILL.md
skill|working-with-legacy-code|Working with legacy code safely|.agents/skills/working-with-legacy-code/SKILL.md
end|AGENT_INDEX_V1
```
<!-- END AGENT INDEX (generated) -->

## Always-on principles
- Prefer the smallest safe change that satisfies the requirement.
- Exception: when `function-boundary-governor` or `destructive-refactor` is triggered, prefer the smallest coherent final design, not the smallest edit.
- No broad cleanups. Leave touched code slightly easier to read than before.
- Destructive refactors may temporarily break compatibility only inside the skill-declared red-state protocol; permanent shims/sibling abstractions require explicit staged-migration ledger records.
- If runtime behavior changes, add observability (logs/metrics/traces) so failures are diagnosable.

## Mandatory workflow for code/test changes
1) Apply the `dev-workflow` playbook end-to-end before editing (start with risk routing: low / normal / high, then execute trigger-based required branches only when applicable).
2) Before finishing, apply the `quality-gate` playbook and address findings.

Role split: `dev-workflow` decides required route/branches; `quality-gate` decides submit readiness via exit criteria.

If work is complex/long-running, create and maintain an ExecPlan under `plans/` (see `PLANS.md`). Use `$execution-plans` or `/execution-plans`.

## Verification commands
Use the canonical commands in `COMMANDS.md` (build, format/lint, tests).
If `COMMANDS.md` still contains `<fill>`, treat the project as uninitialized: do not guess commands, run `$project-initialization` or `/initialize` first.
Initialization completes only after `make verify` succeeds; remove `<fill>` only after that success.
If you cannot run a command, state why and provide a reproducible procedure.

## Required final response format
Return, in this order:
1) Change Brief (what/why, scope, assumptions, risks)
2) What changed (files + intent)
3) Verification (commands + results; or what you could not run)
4) Follow-ups (optional)

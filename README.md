# AI Agent Instructions Playbook

This repository is a template that provides software-development agents with thin always-on rules plus detailed playbooks read only when needed.

The goal is a small, curated software-development operating system: clear entry points, precise triggers, reusable artifacts, and validation that keeps the trigger surface from growing accidentally.

## Core files

- `AGENTS.md` — always-loaded core rules and the skill index
- `.agents/skills/*/SKILL.md` — single source of repo-local Agent Skills for Codex and GitHub Copilot
- `.github/prompts/*.prompt.md` — Copilot prompt files for explicit chat workflows
- `COMMANDS.md` — canonical build / lint / test commands
- `PLANS.md` — guide for ExecPlan operations
- `README.md` — repository overview and minimum onboarding
- `REFERENCES.md` — entry point for reference documents

## Quick Start

1. Open `AGENTS.md` first. It contains the always-on rules and generated skill index.
2. If `COMMANDS.md` still contains `<fill>`, run `project-initialization` before trusting build/test commands.
3. For code or test changes, follow `dev-workflow`, then finish with `quality-gate`.
4. For explicit skill use, invoke `$skill-name` in Codex or `/skill-name` in GitHub Copilot CLI / agent mode.
5. After changing skills or the generated index, run the validation commands below.

## Skill Map

### Core workflow

- `dev-workflow` — route change risk and execute only required branches
- `quality-gate` — final decision before submission
- `execution-plans` — execution planning for complex/long-running tasks
- `requirements-engineering` — convert ambiguous requirements into verifiable design input
- `project-initialization` — initialize the command system

### Investigation and safety nets

- `bug-investigation-and-rca` — evidence-first bug reports and prevention actions
- `working-with-legacy-code` — characterization tests and deterministic seams for risky legacy edits
- `test-driven-development` — Red/Green/Refactor loop when TDD is requested or routed
- `staged-lowering` — staged implementation for low-level, constrained, or repeatedly failing code

### Design, quality, and reliability

- `function-boundary-governor` — autonomous function-boundary decisions for functions/helpers/APIs/call sites
- `destructive-refactor` — replace flawed abstractions with temporary red-state migration and convergence
- `architecture-decision-analysis` — compare architecture options against quality drivers, risks, tradeoffs, and verification tasks
- `code-smells-and-antipatterns` — diff-focused maintainability and boundary review
- `code-readability` — requested readability cleanup and C++ documentation gates
- `error-handling` — failure contracts at boundaries, retries, fallbacks, and user-visible errors
- `observability` — logs, metrics, and traces for behavior changes

### Concurrency

- `concurrency-core` — concurrency plan, lifecycle, cancellation, and safety strategy
- `concurrency-android` — Android background work and coroutine guidance
- `concurrency-ros2` — ROS 2 executor, callback group, and service/action patterns
- `thread-safety-tooling` — TSan and compile-time thread-safety verification

### UI and visual evidence

- `uiux-core` — deterministic UI/UX review bundle
- `visual-regression-testing` — snapshot verification and visual diff review
- `uiux-flow-preview` — flow-map preview for transition review
- `tonemana-catalog` — comparable tone and manner catalog with previews
- `tonemana-apply` — apply a selected tone/manner pattern to UIUX artifacts
- `uidesign-flow` — convert tone decisions into tokens and previews
- `uidesign-orchestrator` — explicit end-to-end UI evidence pipeline wrapper

### Authoring support

- `playbook-template-authoring` — reusable deployment, infra, data-analysis, and API-reference playbook templates

The generated full index in `AGENTS.md` is the authoritative machine-readable list.

## Generated Skill Catalog

This block is regenerated from `.agents/skills/*/SKILL.md`. Keep the role-based Skill Map above hand-authored for humans.

<!-- BEGIN README SKILL CATALOG (generated) -->
| Skill | Description | Source |
| --- | --- | --- |
| `architecture-decision-analysis` | Architecture decision analysis | `.agents/skills/architecture-decision-analysis/SKILL.md` |
| `bug-investigation-and-rca` | Bug investigation & RCA | `.agents/skills/bug-investigation-and-rca/SKILL.md` |
| `code-readability` | Code readability | `.agents/skills/code-readability/SKILL.md` |
| `code-smells-and-antipatterns` | Diff-focused maintainability review | `.agents/skills/code-smells-and-antipatterns/SKILL.md` |
| `concurrency-android` | Android concurrency and background work | `.agents/skills/concurrency-android/SKILL.md` |
| `concurrency-core` | Concurrency design patterns and planning | `.agents/skills/concurrency-core/SKILL.md` |
| `concurrency-ros2` | ROS 2 concurrency patterns | `.agents/skills/concurrency-ros2/SKILL.md` |
| `destructive-refactor` | Replace flawed abstraction safely | `.agents/skills/destructive-refactor/SKILL.md` |
| `dev-workflow` | Risk-routed dev workflow | `.agents/skills/dev-workflow/SKILL.md` |
| `error-handling` | Boundary error handling | `.agents/skills/error-handling/SKILL.md` |
| `execution-plans` | ExecPlan: plan/WBS/progress + handoff | `.agents/skills/execution-plans/SKILL.md` |
| `function-boundary-governor` | Autonomous function-boundary design | `.agents/skills/function-boundary-governor/SKILL.md` |
| `observability` | Observability plan and checklist | `.agents/skills/observability/SKILL.md` |
| `playbook-template-authoring` | Reusable playbook/template authoring | `.agents/skills/playbook-template-authoring/SKILL.md` |
| `project-initialization` | Initialize canonical verify commands | `.agents/skills/project-initialization/SKILL.md` |
| `quality-gate` | Final quality gate | `.agents/skills/quality-gate/SKILL.md` |
| `requirements-engineering` | Requirements engineering | `.agents/skills/requirements-engineering/SKILL.md` |
| `staged-lowering` | Staged lowering for constrained code | `.agents/skills/staged-lowering/SKILL.md` |
| `test-driven-development` | Test-driven development workflow | `.agents/skills/test-driven-development/SKILL.md` |
| `thread-safety-tooling` | Thread-safety verification | `.agents/skills/thread-safety-tooling/SKILL.md` |
| `tonemana-apply` | Apply tone/manner choice to UIUX Pack | `.agents/skills/tonemana-apply/SKILL.md` |
| `tonemana-catalog` | Tone & Manner catalog + previews | `.agents/skills/tonemana-catalog/SKILL.md` |
| `uidesign-flow` | tonemana → tokens → component+screen previews | `.agents/skills/uidesign-flow/SKILL.md` |
| `uidesign-orchestrator` | full UI evidence pipeline orchestration | `.agents/skills/uidesign-orchestrator/SKILL.md` |
| `uiux-core` | UI/UX core contract + deterministic review bundle | `.agents/skills/uiux-core/SKILL.md` |
| `uiux-flow-preview` | Transition map preview with pan/zoom + focus review | `.agents/skills/uiux-flow-preview/SKILL.md` |
| `visual-regression-testing` | Tool-agnostic UI visual verification contract | `.agents/skills/visual-regression-testing/SKILL.md` |
| `working-with-legacy-code` | Working with legacy code safely | `.agents/skills/working-with-legacy-code/SKILL.md` |
<!-- END README SKILL CATALOG (generated) -->

## Skill layout

Project skills live only under `.agents/skills`. Do not mirror them into `.github/skills`; current Codex and GitHub Copilot both support `.agents/skills` as a project-skill location.

Use `$skill-name` in Codex and `/skill-name` in GitHub Copilot CLI / agent mode when explicit invocation is needed. Keep short, always-on rules in `AGENTS.md`; move detailed procedures, examples, and templates into skills, `references/`, or `templates/`.

## Skill Quality Bar

Add or revise a skill only when it has a coherent job that should be discoverable by an agent. Prefer fewer active skills with clearer triggers over a long catalog of overlapping guidance.

Each retained skill should have:

- a narrow `description` that says when to use it and, for broad topics, when not to use it
- a concise `SKILL.md` body with the core workflow only
- conditional `references/`, `templates/`, `assets/`, or scripts for heavier material
- a concrete output artifact, decision, or verification record
- clear relationships to neighboring skills so trigger overlap stays intentional
- trigger eval seeds for both positive prompts and near-miss negative prompts when the skill is core or broad

## Skill Delta Gate

Before adding a new skill or broadening an existing one, the change must pass all criteria:

1. Runtime decision delta:

   - The change alters agent behavior such as proceed/no-proceed, no-decision, route-to-skill, submit/no-submit, or rewrite/no-rewrite.

2. Existing-skill absorption test:

   - If description, trigger, anti-trigger, output contract, reference, or trigger eval updates are enough, do not add a new skill.

3. Trigger boundary test:

   - At least two positive cases and three near-miss negative cases exist for broad or core skills.

4. Output contract test:

   - The skill produces a concrete artifact, decision, verification record, or explicit no-op/no-decision.

5. Complexity cap:

   - Keep `SKILL.md` workflow-focused.
   - Move heavy material to `references/`.
   - Do not put deep taxonomy into `quality-gate`.

If any criterion fails, do not add the skill.

## Validation

Run these after changing skills or the agent index:

- `python scripts/validate_skills.py`
- `python scripts/validate_skill_trigger_evals.py`
- `python scripts/report_skill_inventory.py --check --format text`
- `python scripts/generate_agent_index.py --check`

## Minimal bootstrap

1. Open `AGENTS.md` and review the `dev-workflow` and `quality-gate` flow.
2. If `COMMANDS.md` is uninitialized (`<fill>`), run `project-initialization`.
3. Before and after changes, verify with canonical commands defined in `COMMANDS.md`.

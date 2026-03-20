# AI Agent Instructions Playbook

This repository is a reusable playbook for software-development agents.
It keeps always-on rules thin and operational detail in on-demand skill docs.

## What this repo is

A shared instruction baseline for agent-driven development workflows:

- repo-level policy and defaults (`AGENTS.md`)
- canonical verification commands (`COMMANDS.md`)
- planning/traceability conventions (`PLANS.md`, `plans/`)
- skill and prompt packages for tool-specific runtimes (`.agents/skills`, `.github/skills`, `.github/prompts`)

## Core files

- `AGENTS.md`
- `COMMANDS.md`
- `PLANS.md`
- `plans/README.md`
- `REFERENCES.md`
- `.agents/skills/`
- `.github/skills/`
- `.github/prompts/`
- `.github/instructions/`

## Core runtime skills (short list)

- `dev-workflow`
- `quality-gate`
- `execution-plans`
- `requirements-to-design`
- `observability`

## Minimal bootstrap

1. Read `AGENTS.md` for always-on rules and mandatory workflow.
2. Read `COMMANDS.md` for canonical verify/build/lint/test commands.
3. Start changes with `dev-workflow`; finish with `quality-gate`.

## Included skills (generated)

<!-- BEGIN README SKILL CATALOG (generated) -->
- `architecture-boundaries` — Architecture boundaries (Clean Architecture)
- `bug-investigation-and-rca` — Bug investigation & RCA
- `cicd-deployment-template` — CI/CD & deployment template
- `code-readability` — Code readability
- `code-smells-and-antipatterns` — Smells & anti-patterns triage
- `concurrency-android` — Android concurrency and background work
- `concurrency-core` — Concurrency design patterns and planning
- `concurrency-ros2` — ROS 2 concurrency patterns
- `data-fetching-analysis-template` — Data fetching & analysis template
- `dev-workflow` — Risk-routed dev workflow
- `error-handling` — Boundary error handling
- `execution-plans` — ExecPlan: plan/WBS/progress + handoff
- `infrastructure-operations-template` — Infrastructure operations runbook template
- `library-api-reference-template` — Library/API reference template
- `modularity` — Modularity (cohesion/coupling)
- `nfr-iso25010` — ISO/IEC 25010 quality attributes template
- `observability` — Observability plan and checklist
- `project-initialization` — Initialize canonical verify commands
- `quality-gate` — Final quality gate
- `requirements-documentation` — Requirements documentation
- `requirements-to-design` — Requirements → design
- `staged-lowering` — Staged lowering for constrained code
- `test-driven-development` — Test-driven development workflow
- `thread-safety-tooling` — Thread-safety verification
- `tonemana-apply` — Choose a Tone & Manner pattern, produce an approved Tonemana Pack, and …
- `tonemana-catalog` — Create or update a Tone & Manner catalog (7 default patterns) with prev…
- `uidesign-flow` — tonemana → tokens → component+screen previews
- `uidesign-orchestrator` — uiux → tonemana → uidesign (orchestration)
- `uiux-android` — Android UI/UX adapter for UIUX Pack
- `uiux-core` — UI/UX core contract + deterministic review bundle
- `uiux-flow-preview` — Transition map preview with pan/zoom + focus review
- `uiux-ios` — iOS UI/UX adapter for UIUX Pack
- `uiux-web` — Web UI/UX adapter for UIUX Pack
- `visual-regression-android` — Android visual regression defaults
- `visual-regression-ios` — iOS visual regression defaults
- `visual-regression-testing` — Tool-agnostic UI visual verification contract
- `visual-regression-web` — Web visual regression defaults
- `working-with-legacy-code` — Working with legacy code safely
<!-- END README SKILL CATALOG (generated) -->


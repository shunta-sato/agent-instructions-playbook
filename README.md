# AI Agent Instructions Playbook (Codex + GitHub Copilot)

A reusable instruction set that works with:

- **OpenAI Codex** (`AGENTS.md` + `.agents/skills/…`)
- **GitHub Copilot (VS Code)** (`AGENTS.md`, `.github/copilot-instructions.md`, `.github/instructions/…`, `.github/prompts/…`, and optional `.github/skills/…`)

This repo is designed around **thin always-on rules** and **thick on-demand playbooks**.
The on-demand playbooks use a “load details only when needed” mechanism (progressive disclosure):
- Codex loads only each skill’s `name`/`description` at startup; it reads the body only when a skill is invoked.
- VS Code Agent Skills load on demand in a similar way.

## Repository layout

Recommended layout (self-contained):

```

AGENTS.md
COMMANDS.md
PLANS.md
plans/
.agents/skills/...
.github/
copilot-instructions.md
instructions/
prompts/
skills/        # optional (VS Code Agent Skills)
REFERENCES.md

```

If you want to use this repo as a template, keep the files at the root as above so both Codex and Copilot can discover them automatically.

## Quick start

### Codex
- Use `$dev-workflow` for any change to decide risk route and required triggered branches.
- Use `$execution-plans` for complex/long-running work and keep `plans/<slug>.md` updated.
- Finish with `$quality-gate` for submit/no-submit exit criteria.
- Trigger required branches only when facts require them:
  - runtime behavior changes → `$observability`
  - UI changes → `$visual-regression-testing` + matching platform visual skill(s)
  - concurrency changes → `$concurrency-core` + `$thread-safety-tooling` (+ `$concurrency-ros2`/`$concurrency-android` when relevant)
  - bug/regression/flaky/crash/hang → `$bug-investigation-and-rca`
  - strict-constraint code or repeated compile/test failure loops → `$staged-lowering`
  - legacy/no reliable tests/nondeterminism → `$working-with-legacy-code`

### Dev-workflow routing examples (required branches only)

| Case | Risk | Required route / branch outputs |
|---|---|---|
| Small local change | Low | compact brief + impacted tests + canonical minimum verify depth + handoff to `$quality-gate` |
| Bugfix | Normal (or High if wide impact) | trigger bugfix branch: `$bug-investigation-and-rca` evidence + risk-required verify depth + handoff to `$quality-gate` |
| UI change | Normal | trigger UI branch: `$visual-regression-testing` + platform visual skill(s) + UI report + handoff to `$quality-gate` |
| Concurrency change | High | trigger concurrency branch: `$concurrency-core` + `$thread-safety-tooling` (+ variant skills) + full verify depth + handoff to `$quality-gate` |
| Legacy/refactor | High | trigger legacy branch: `$working-with-legacy-code` before refactor + safety-net evidence + full verify depth + handoff to `$quality-gate` |

### Copilot (VS Code)

**Custom instructions**
- Repository-wide: `.github/copilot-instructions.md`
- Path-specific: `.github/instructions/*.instructions.md`

**Prompt files**
- Stored under `.github/prompts/` by default.
- Run them by typing `/` and the prompt name in chat (for example: `/dev-workflow`).
- Use `/bug-report` for bugfix/regression/flaky/incidents to generate the deterministic Bug Report template.

**Agent Skills (optional)**
- Stored under `.github/skills/` (recommended).
- Enable the `chat.useAgentSkills` setting in VS Code (preview) to use them.

## Maintaining the AGENTS.md index

This repo embeds a generated, compressed playbook index into `AGENTS.md` so agents can find the right files without needing to “decide” to load a skill.
The same generator also refreshes the README skill catalog from the source-of-truth tree (`.agents/skills`).

After editing any of these:
- `.agents/skills/**`
- `.github/skills/**` (generated mirror; do not edit manually)
- `.github/prompts/**`
- `.github/instructions/**`

Run:

```bash
python scripts/generate_agent_index.py --write
```

CI will fail if either the AGENTS index or README skill catalog is out of date.

## Canonical commands

`COMMANDS.md` is the single place to record how to build / format / lint / test the project.
If you use this repo as a template, replace the `<fill>` placeholders with real commands.

## Deterministic skill helpers (high-friction artifacts)

To bootstrap deterministic artifacts for high-friction skills, use this single helper entrypoint:

- `python scripts/init_artifact.py --kind execplan --slug <topic>` → `plans/<slug>.md`
- `python scripts/init_artifact.py --kind bug-report --slug <topic>` → `reports/bug-reports/<slug>.md`
- `python scripts/init_artifact.py --kind concurrency-matrix --slug <topic>` → `reports/concurrency/<slug>.md`

All helpers require `--force` to overwrite an existing non-empty file.


## Skill adoption proxy measurement

You can generate a repo-local proxy measurement (artifact-based, not telemetry) with:

- `python scripts/measure_skill_adoption.py --pretty`

Current proxy coverage (counts artifacts, not true runtime invocation):

- `execution_plans`: `plans/*.md` except `plans/README.md` and `plans/_template_execplan.md`
- `bug-investigation-and-rca`: `reports/bug-reports/*.md`
- `uiux-core`: `uiux/<pack>/` directories that contain all required UIUX Pack files
  (`ui_contract.yaml`, `ui_spec.json`, `auto_review.json`, `diff_summary.md`)
- `project-initialization`: `1` when `COMMANDS.md` has `verified by agent: yes (...)`, otherwise `0`

The JSON output is machine-readable and reports `0` for missing/empty artifact locations without failing.

What this **does not** measure:

- Whether a skill was invoked but no artifact was committed
- Invocation frequency in chat/IDE history
- Artifact quality or correctness

## Smells & anti-patterns triage

Use the `code-smells-and-antipatterns` playbook (Codex: `$code-smells-and-antipatterns`) to detect **new or worsened** design smells in a diff and propose the smallest fix.
It is recommended for structural changes (new modules, boundary changes, or refactors across layers) and is referenced by `dev-workflow` and `quality-gate`.

## UI visual verification contract

When UI changes are in scope, this repository expects one canonical verification interface:

- Make-based contract: `make ui-verify`, `make ui-record`, optional `make ui-artifacts`; or
- Script-based contract: `./tools/ui/verify.sh`, `./tools/ui/record.sh`.

Agents should discover which option the repository exposes, execute it, review visual diffs against requested/design-intent behavior, and update baselines only for intentional changes.

Required output:

```markdown
## UI Visual Verification Report
- Platform: ios|android|web
- Environment: OS + key tool versions
- Command(s) executed:
- Snapshot output path(s):
- Baseline updated?: yes|no
- Review summary:
  - If diff: why accepted or what to fix
  - If cannot run: why + how CI should cover it
```

## Included skills

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

## Versioning

This repository follows Semantic Versioning (SemVer).
Skill renames are treated as breaking changes.

Generated: 2026-02-01

## Bugfix mode triggers (required)

Use bugfix mode (via `$dev-workflow` + `$bug-investigation-and-rca`) when tasks mention bug/regression/flaky/crash/hang/incident, when behavior-level test failures are being fixed, or when workaround-only mitigation is considered. Paste the resulting Bug Report (RCA) in the PR description, issue comment, or a tracked docs file.

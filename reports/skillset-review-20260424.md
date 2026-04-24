# Skill Set Review — 2026-04-24

This review audits all repository-local skills under `.agents/skills` against April 2026 Agent Skills guidance for Codex and GitHub Copilot.

## Current Knowledge Baseline

- OpenAI Codex skills are task-specific bundles of instructions, resources, and optional scripts. Codex uses progressive disclosure: metadata is visible first, then full `SKILL.md` is loaded only after explicit or implicit invocation. Codex scans repository `.agents/skills` paths and recommends focused jobs, clear inputs/outputs, imperative steps, and trigger testing.
  Source: https://developers.openai.com/codex/skills
- GitHub Copilot agent skills work in Copilot cloud agent, Copilot CLI, and VS Code agent mode. Project skills may live in `.github/skills`, `.claude/skills`, or `.agents/skills`; `description` is the selection surface.
  Source: https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills
- The Agent Skills specification requires `SKILL.md` with YAML frontmatter (`name`, `description`) and supports optional `references/`, `scripts/`, `assets/`, `compatibility`, `metadata`, and experimental `allowed-tools`.
  Source: https://agentskills.io/specification
- The description is the main trigger contract. Under-specified descriptions miss relevant tasks; over-broad descriptions trigger when they should not.
  Source: https://agentskills.io/skill-creation/optimizing-descriptions
- Skill quality should be tested with realistic prompts, edge cases, and expected outputs. Start with a small eval set before large rewrites.
  Source: https://agentskills.io/skill-creation/evaluating-skills
- Benchmarks now show that skills are not automatically beneficial. SkillsBench reports curated skills improved average pass rate by 16.2 percentage points, but software engineering improved only 4.5 points and 16 of 84 tasks regressed; focused skills with 2-3 modules beat comprehensive documentation.
  Source: https://arxiv.org/abs/2602.12670
- April 2026 research reinforces pruning and feedback loops: SkillMOO found pruning/substitution to be primary improvement drivers, and SkillLearnBench found clear reusable workflows benefit most while self-feedback alone can drift.
  Sources: https://arxiv.org/abs/2604.09297, https://arxiv.org/abs/2604.20087

## Review Bar

Each retained skill should satisfy these properties:

- Spec-valid and portable across Codex/Copilot.
- One coherent job, not a broad philosophy.
- Description says when to use it, and ideally what not to use it for.
- `SKILL.md` stays concise; long reusable material lives in conditional references/templates/scripts.
- Output artifact or decision is explicit enough to verify.
- Relationship to neighboring skills is clear.
- Evaluable through should-trigger / should-not-trigger prompts and artifact checks.

Decision labels:

- **Keep**: good active skill; only minor edits/evals needed.
- **Rewrite**: valuable job, but trigger/procedure/output needs tightening.
- **Merge**: content should remain, but the active skill should collapse into a stronger parent skill or reference.
- **Delete**: remove after replacement mapping is explicit. No immediate hard deletes are recommended in this first audit pass.

## Collection-Level Findings

1. The post-consolidation layout is correct: `.agents/skills` is now the single repo-local source for Codex and Copilot.
2. Validation is currently clean, but the active trigger surface is too large: 38 skills is high for a software-development playbook, especially with many generic review skills and platform adapters.
3. The strongest skills have concrete artifacts: Bug Report, ExecPlan, Concurrency Plan, UI Visual Verification Report, Tonemana Pack, UIDesign Pack.
4. The weakest active skills are broad quality topics or template-authoring playbooks that may trigger on normal implementation tasks without enough payoff.
5. The next best target is not deletion for its own sake. It is reducing the active skill count to about 24-27 by merging adapters/templates into conditional references while preserving domain content.
6. The skill set lacks evals. Add lightweight trigger evals before aggressive pruning: 2-3 positive prompts, 2 negative prompts, and one artifact expectation per core skill.

## Target Shape

- Core workflow: `dev-workflow`, `quality-gate`, `execution-plans`, `project-initialization`.
- Evidence workflows: `bug-investigation-and-rca`, `working-with-legacy-code`, `staged-lowering`, `test-driven-development`.
- Design/reliability review: one maintainability review parent plus focused error-handling and observability workflows.
- Requirements: one `requirements-engineering` parent covering EARS, acceptance criteria, traceability, and ISO 25010 quality scenarios.
- Concurrency: keep core + domain/tooling adapters because these are specialized and high-risk.
- UI/visual: keep artifact-producing UI skills, but merge simple platform adapter skills into their parent references.
- Template authoring: merge four template skills into one domain playbook template authoring skill.

## Skill-by-Skill Audit

| Skill | Decision | Rationale / next action |
| --- | --- | --- |
| `architecture-boundaries` | Merge | Valuable Clean Architecture content, but as an active skill it overlaps `modularity` and `code-smells-and-antipatterns`. Move the reference under a maintainability/design-review parent and trigger only on boundary decisions. |
| `bug-investigation-and-rca` | Keep | Strong evidence-first workflow with a concrete Bug Report artifact. Add evals for crash/regression/flaky/incorrect-output prompts and negative prompts for ordinary feature work. |
| `cicd-deployment-template` | Merge | Useful template content, but it is a template-authoring skill rather than a normal implementation skill. Merge into a single `playbook-template-authoring` skill with deployment as one mode/reference. |
| `code-readability` | Rewrite | Contains useful local C++ documentation rules, but generic readability can over-trigger. Narrow the description to explicit readability review, C++ header/documentation gates, and touched-code cleanup. |
| `code-smells-and-antipatterns` | Rewrite | Best candidate to become the maintainability/design-review parent. Keep diff-only smell triage, then absorb architecture/modularity references as conditional deep dives. |
| `concurrency-android` | Keep | Platform-specific and high-risk enough to remain separately discoverable. Keep as an adapter invoked with `concurrency-core`; add negative triggers for non-Android async work. |
| `concurrency-core` | Keep | Strong focused workflow with Concurrency Plan output. Add trigger evals for async/threads/queues/locks and should-not-trigger examples for ordinary sequential code. |
| `concurrency-ros2` | Keep | ROS 2 executor/callback-group guidance is specialized and not obvious to general agents. Keep as adapter invoked with `concurrency-core`. |
| `data-fetching-analysis-template` | Merge | Useful checklist, but it is one of several domain template skills. Merge into `playbook-template-authoring`; keep report template as a conditional asset. |
| `dev-workflow` | Keep | Repository router is necessary and already referenced from `AGENTS.md`. Add evals for risk routing and triggered-branch selection; avoid expanding its body. |
| `error-handling` | Rewrite | Valuable boundary failure-path guidance, but trigger is broad. Tighten to exception translation, API boundaries, nullability, retries, and user-visible failure behavior. |
| `execution-plans` | Keep | Concrete long-running-work artifact and handoff mechanism. Add positive/negative trigger evals to avoid using it for small edits. |
| `infrastructure-operations-template` | Merge | High-quality runbook material, but should be a mode in `playbook-template-authoring` to reduce active template skills. Preserve destructive-action guardrails. |
| `library-api-reference-template` | Merge | Valuable for turning external API docs into reusable references, but it belongs with template/skill-authoring workflows rather than as a broad active skill. |
| `modularity` | Merge | Good reference content, but it overlaps architecture and smell triage. Move under maintainability/design-review as a conditional deep dive. |
| `nfr-iso25010` | Merge | ISO 25010 is useful when writing quality scenarios, but as a separate active skill it can trigger too broadly. Merge into `requirements-engineering`. |
| `observability` | Rewrite | Important because `AGENTS.md` requires observability for runtime behavior changes. Description needs explicit triggers and output should be an Observability Plan with verification signals. |
| `project-initialization` | Keep | Specific, repo-critical workflow. Keep active; add evals around `<fill>` and `make verify` gating. |
| `quality-gate` | Keep | Essential final submission gate. Keep concise and evidence-based; add evals for missing artifacts/unrun commands. |
| `requirements-documentation` | Merge | Valuable formal docs workflow, but overlaps `requirements-to-design` and `nfr-iso25010`. Merge into `requirements-engineering` with modes for brief/spec/SRS. |
| `requirements-to-design` | Merge | Planning workflow is valuable but “mandatory during planning” is too broad. Merge into `requirements-engineering`; trigger on ambiguous/non-trivial feature planning. |
| `staged-lowering` | Keep | Strong specialized workflow for constrained code and repeated compile/test failure. Keep active; add evals for low-level code and should-not-trigger normal CRUD changes. |
| `test-driven-development` | Keep | Concrete workflow when the user or route chooses TDD. Tighten description slightly later so it does not imply all testing work must be TDD. |
| `thread-safety-tooling` | Keep | Tooling evidence for C/C++ races/deadlocks is specialized and high-value. Keep as a concurrency adapter with verification matrix output. |
| `tonemana-apply` | Keep | Artifact-producing UI style decision workflow. First-pass fix: add short description and clearer trigger. Later add evals for selected-pattern vs missing-catalog scenarios. |
| `tonemana-catalog` | Keep | Specific catalog/preview generator. First-pass fix: add short description and clearer trigger. |
| `uidesign-flow` | Keep | Produces deterministic styling artifacts and previews. Keep, but add evals and clarify when it follows `tonemana-apply` versus when it can run standalone. |
| `uidesign-orchestrator` | Rewrite | Useful end-to-end UI evidence workflow, but it mostly sequences neighboring skills. Keep for now, then either make it explicit-only or merge into `uidesign-flow` if evals show mis-triggering. |
| `uiux-android` | Merge | Thin adapter. Move its reference under `uiux-core` and have `uiux-core` conditionally open Android checks. |
| `uiux-core` | Keep | Strong artifact contract for UI/UX work. It should become the parent for platform adapter references. |
| `uiux-flow-preview` | Keep | Specific preview artifact (`flow-map.html`) with concrete interaction requirements. Keep active. |
| `uiux-ios` | Merge | Thin adapter. Move its reference under `uiux-core` and have `uiux-core` conditionally open iOS checks. |
| `uiux-web` | Merge | Thin adapter. Move its reference under `uiux-core` and have `uiux-core` conditionally open web checks. |
| `visual-regression-android` | Merge | Thin adapter. Move Android defaults under `visual-regression-testing` as conditional reference material. |
| `visual-regression-ios` | Merge | Thin adapter. Move iOS defaults under `visual-regression-testing` as conditional reference material. |
| `visual-regression-testing` | Keep | Strong tool-agnostic visual verification contract. It should become the parent for platform visual defaults. |
| `visual-regression-web` | Merge | Thin adapter. Move web defaults under `visual-regression-testing` as conditional reference material. |
| `working-with-legacy-code` | Keep | Concrete high-risk workflow with characterization tests and seams. Keep active; add trigger evals for nondeterminism/no-tests and negative prompts for well-tested code. |

## First-Pass Changes Applied

- Added `metadata.short-description` to `tonemana-apply`.
- Rewrote `tonemana-apply` description to include the trigger context, not just the action.
- Added `metadata.short-description` to `tonemana-catalog`.
- Rewrote `tonemana-catalog` description to include its role before UIUX/UIDesign tone selection.

## Consolidation Pass Applied

- Reduced active skills from 38 to 25.
- Merged `architecture-boundaries` and `modularity` into `code-smells-and-antipatterns` as conditional maintainability/boundary references.
- Merged `requirements-documentation`, `requirements-to-design`, and `nfr-iso25010` into `requirements-engineering`.
- Merged `cicd-deployment-template`, `data-fetching-analysis-template`, `infrastructure-operations-template`, and `library-api-reference-template` into `playbook-template-authoring`.
- Merged `uiux-android`, `uiux-ios`, and `uiux-web` into `uiux-core` as platform adapter references.
- Merged `visual-regression-android`, `visual-regression-ios`, and `visual-regression-web` into `visual-regression-testing` as platform visual references.
- Added `evals/skill-triggers/` plus `scripts/validate_skill_trigger_evals.py` to preserve dispatch expectations after future description edits.
- Tightened broad trigger descriptions for `observability`, `error-handling`, `code-readability`, and `uidesign-orchestrator`.
- Expanded trigger eval seeds from 25 to 35 cases, adding negative cases for docs-only observability, copy-only error messages, ordinary clear code changes, single-step UI design work, tiny requirement changes, and template execution.

## Recommended Next Passes

1. Continue expanding the lightweight trigger eval seed set:
   - `evals/skill-triggers/*.json`
   - 2-3 should-trigger prompts per core skill.
   - 2 should-not-trigger prompts per broad/overlapping skill.
   - Expected artifact or route label.
2. Decide whether `uidesign-orchestrator` should remain an active skill or become an explicit-only prompt after real usage data.
3. Add optional `agents/openai.yaml` metadata for the 25 retained active skills if the repo wants richer Codex skill list UI.
4. Add a true LLM dispatch eval runner when a stable model/tooling target is chosen; the current JSON seed validator checks schema and skill existence only.

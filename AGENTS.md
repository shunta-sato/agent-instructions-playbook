# AGENTS.md — AI agent core instructions

This repository is a reusable playbook for software-development agents. Keep this
file thin; detailed procedures live under `.agents/skills/<name>/SKILL.md`.
Explicit invocation differs by client: Codex `$<skill>`, Copilot and Claude Code
`/<skill>`.
## Playbook bootstrap

Inspect the Agent Index before software-development work and load only applicable
skills. An explicitly named skill is loaded before acting.
Determine epistemic mode first: explicit declaration, then
`.agents/project-policy.yml` path modes, then its default. Research paths use
`research-workflow`. Delivery-mode code/test changes use `dev-workflow` and finish
with `quality-gate`.

Issue-scoped feature delivery, backlog campaigns, and stalled feature PRs use
`user-value-delivery` before `dev-workflow`. It governs scope, sequencing,
review admission, delivery cost, and stop conditions. It never overrides explicit
acceptance, safety, security, privacy, compliance, data integrity, compatibility,
authorization, branch protection, or repository-required checks.
Skill load contract:
- `metadata.requires`: load before execution; unreadable is an error.
- `metadata.resources`: load only when the SKILL-stated condition matches.
- `metadata.commands`: execute or cite by path; do not inline them into context.
- `metadata.templates`: open only when producing that artifact.

The root/orchestrating agent owns Delivery Control, route lock, candidate identity,
and final-gate assignment. Delegated workers receive a bounded task brief and use
focused validation; they do not repeat the full workflow or final gate. Reviewers
judge the requested candidate against blocking criteria and do not expand scope.

## Agent Index (generated)

Do not edit this block by hand. Update it with
`python scripts/generate_agent_index.py --write`.

<!-- BEGIN AGENT INDEX (generated) -->
```text
AGENT_INDEX_V1
meta|format=v1|max_bytes=8192|invoke=codex:$<skill>,copilot:/<skill>
defaults|govern=user-value-delivery|workflow=dev-workflow|finish=quality-gate|verify=COMMANDS.md
core|AGENTS.md|COMMANDS.md|PLANS.md|plans/README.md|README.md|REFERENCES.md
skills|name|short|skill_path
skill|agent-workflow-contract-review|Agent workflow contract review|.agents/skills/agent-workflow-contract-review/SKILL.md
skill|architecture-decision-analysis|Architecture decision analysis|.agents/skills/architecture-decision-analysis/SKILL.md
skill|branch-completion|Finish branch and PR lifecycle|.agents/skills/branch-completion/SKILL.md
skill|bug-investigation-and-rca|Bug investigation & RCA|.agents/skills/bug-investigation-and-rca/SKILL.md
skill|code-readability|Proportional code readability|.agents/skills/code-readability/SKILL.md
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
skill|execution-plans|Durable handoff ExecPlan|.agents/skills/execution-plans/SKILL.md
skill|experiment-loop|Registered experiment evidence contract|.agents/skills/experiment-loop/SKILL.md
skill|failure-retrospective|Failure learning and promotion routing|.agents/skills/failure-retrospective/SKILL.md
skill|function-boundary-governor|Autonomous function-boundary design|.agents/skills/function-boundary-governor/SKILL.md
skill|hardening-workflow|Measure-tier-stop hardening lane|.agents/skills/hardening-workflow/SKILL.md
skill|implementation-economy|Scope-inversion and abstraction budget|.agents/skills/implementation-economy/SKILL.md
skill|japanese-tech-writing|Japanese technical writing conventions|.agents/skills/japanese-tech-writing/SKILL.md
skill|mobile-feature-parity|Cross-platform mobile capability parity|.agents/skills/mobile-feature-parity/SKILL.md
skill|mobile-release-coordination|Coordinated iOS and Android release gate|.agents/skills/mobile-release-coordination/SKILL.md
skill|mobile-runtime-verification|Mobile runtime verification|.agents/skills/mobile-runtime-verification/SKILL.md
skill|observability|Boundary-focused observability|.agents/skills/observability/SKILL.md
skill|performance-review|Generic performance review|.agents/skills/performance-review/SKILL.md
skill|playbook-template-authoring|Reusable playbook/template authoring|.agents/skills/playbook-template-authoring/SKILL.md
skill|poc-workflow|PoC construction on the research substrate|.agents/skills/poc-workflow/SKILL.md
skill|preflight-api-compat|Public API compatibility preflight|.agents/skills/preflight-api-compat/SKILL.md
skill|preflight-auth-session|Auth/session preflight|.agents/skills/preflight-auth-session/SKILL.md
skill|preflight-db-migration|DB migration preflight|.agents/skills/preflight-db-migration/SKILL.md
skill|preflight-engineering|Preflight agent context and handoff|.agents/skills/preflight-engineering/SKILL.md
skill|preflight-mobile-app|Mobile app preflight|.agents/skills/preflight-mobile-app/SKILL.md
skill|project-initialization|Initialize canonical verify commands|.agents/skills/project-initialization/SKILL.md
skill|project-structure|Two-tier structure guardrails|.agents/skills/project-structure/SKILL.md
skill|quality-gate|Blocking-finding quality gate|.agents/skills/quality-gate/SKILL.md
skill|receiving-code-review|Process review feedback safely|.agents/skills/receiving-code-review/SKILL.md
skill|refactor-workflow|Behavior-preserving refactor lane|.agents/skills/refactor-workflow/SKILL.md
skill|requesting-code-review|Prepare focused review requests|.agents/skills/requesting-code-review/SKILL.md
skill|requirements-engineering|Requirements engineering|.agents/skills/requirements-engineering/SKILL.md
skill|research-synthesis|Research decision synthesis|.agents/skills/research-synthesis/SKILL.md
skill|research-workflow|Research-mode router|.agents/skills/research-workflow/SKILL.md
skill|staged-lowering|Staged lowering for constrained code|.agents/skills/staged-lowering/SKILL.md
skill|test-driven-development|Test-driven development workflow|.agents/skills/test-driven-development/SKILL.md
skill|thread-safety-tooling|Thread-safety verification|.agents/skills/thread-safety-tooling/SKILL.md
skill|tonemana-apply|Apply tone/manner choice to UIUX Pack|.agents/skills/tonemana-apply/SKILL.md
skill|tonemana-catalog|Tone & Manner catalog + previews|.agents/skills/tonemana-catalog/SKILL.md
skill|uidesign-flow|tonemana → tokens → component+screen previews|.agents/skills/uidesign-flow/SKILL.md
skill|uiux-core|UI/UX core contract + deterministic review bundle|.agents/skills/uiux-core/SKILL.md
skill|uiux-flow-preview|Transition map preview with pan/zoom + focus review|.agents/skills/uiux-flow-preview/SKILL.md
skill|unit-test-design|Risk-tiered unit test design|.agents/skills/unit-test-design/SKILL.md
skill|user-value-delivery|User-value delivery governor|.agents/skills/user-value-delivery/SKILL.md
skill|variant-exploration|Executable variant exploration|.agents/skills/variant-exploration/SKILL.md
skill|visual-regression-testing|Tool-agnostic UI visual verification contract|.agents/skills/visual-regression-testing/SKILL.md
skill|working-with-legacy-code|Working with legacy code safely|.agents/skills/working-with-legacy-code/SKILL.md
skills-explicit|comment-discipline|uidesign-orchestrator
skills-template|preflight-domain-template
end|AGENT_INDEX_V1
```
<!-- END AGENT INDEX (generated) -->

## Always-on principles

- Complete the issue, not the codebase. Meet the observable DoD; do not make
  surrounding code ideal unless the DoD or real boundary requires it.
- Prefer the smallest safe change that meets the DoD. When
  `function-boundary-governor` or `destructive-refactor` is triggered, prefer
  the smallest coherent final design within the current scope.
- No broad cleanups unrelated to the task.
- Separate failure criticality from maintenance horizon. The former sets
  correctness/safety depth; the latter sets structure and generalization depth.
- Fix blocking concrete defects and material regressions in the supported journey.
  Record minor limitations without turning them into an unbounded polish loop.
  Prevent material structural worsening; defer pre-existing debt and speculation.
- Prefer one active feature PR and the shortest vertical production path.
- Existing evidence is reused for the same candidate identity. Full HOST, CI,
  release, target, and independent-review operations are delivery costs.
- Runtime changes add observability only when a real failure path is otherwise
  not diagnosable or an explicit operational claim needs measurement.
- Compatibility follows the recorded mode: `preserve`, `staged`, or an explicit
  `break-allowed` waiver.
- Code carries How; tests carry What; history carries Why; implementation
  comments carry only durable Why-not constraints, hazards, or requirements.

## Verification and completion

Use canonical commands in `COMMANDS.md`. If placeholders remain, use
`project-initialization` rather than guessing. If a required command cannot run,
state why and provide a reproducible procedure.

Delivery reports lead with what the user can now do, followed by candidate/PR
identity, verification, target evidence where required, and remaining limits.
Research-mode reports follow `research-workflow`.

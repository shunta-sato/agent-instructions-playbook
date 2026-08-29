# AI Agent Instructions Playbook

A reusable, validated operating layer for software-development agents.

## Purpose

This repository keeps repository instructions, on-demand Agent Skills, workflow
adapters, evaluation seeds, and mechanical validators in one versioned place.
It sits between a project request and a coding agent:

```text
project request
    ↓
project-local policy and canonical commands
    ↓
user-value governor when feature delivery needs it
    ↓
risk-routed implementation skills
    ↓
focused iteration checks
    ↓
one final blocker-focused quality gate
```

The governing principle is:

> Complete the issue, not the codebase.

A feature must satisfy its observable Definition of Done and real operating
boundaries. It does not need to make surrounding code ideal. Safety, security,
privacy, authorization, data integrity, compatibility, required checks, and
explicit NFRs remain non-negotiable.

## Supported clients

| Client | Skill location | Explicit invocation |
| --- | --- | --- |
| Codex | `.agents/skills` | `$skill-name` |
| GitHub Copilot CLI / agent mode | `.agents/skills` | `/skill-name` |
| Claude Code | `.claude/skills` symlinks | `/skill-name` |

`setup.sh` exposes shared skills in another worktree. It does not copy
project-specific instructions, grant credentials, or install an agent runtime.

```sh
git clone https://github.com/shunta-sato/agent-instructions-playbook.git \
  ~/tools/agent-instructions-playbook
~/tools/agent-instructions-playbook/setup.sh /path/to/project
```

Use `--overlay` when the target already contains local or third-party skills.
Pin or vendor a revision when reproducibility is more important than receiving
updates from the central clone.

## Delivery workflow

| Situation | Start with | Finish with |
| --- | --- | --- |
| Issue-scoped feature, backlog campaign, stalled feature PR | `user-value-delivery` | `quality-gate` |
| Tiny isolated code/test fix | `dev-workflow` | `quality-gate` |
| Research or exploratory probe | `research-workflow` | `research-synthesis` |
| Explicit refactor | `refactor-workflow` | `quality-gate` |
| Explicit measured hardening | `hardening-workflow` | `quality-gate` |

Feature work separates two dimensions:

- **failure criticality** determines correctness, safety, security, and
  verification depth;
- **maintenance horizon** determines structure, abstraction, documentation, and
  generalization depth.

During implementation, agents use focused checks. One assigned owner performs
the final full gate for an identified candidate. Review blocks only concrete
violations of the DoD, regressions/contracts, required checks, real safety or
security boundaries, explicit NFRs, or hard structure guardrails.

## Structure policy

`check_structure.py` uses advisory and hard thresholds.

| Surface | Advisory | Feature hard guardrail |
| --- | ---: | ---: |
| source file | 600 lines | 1500 lines |
| entrypoint logic | 150 lines | 400 lines |
| Rust inline tests | 300 lines | 800 lines |

Feature-mode advisories prompt a responsibility check but do not block. New or
crossed hard findings block. Files already beyond a hard guardrail remain editable
for small changes within the existing responsibility; more than 50 net metric lines
of additional hard debt blocks mechanically. Refactor/structure-hardening work may use strict mode, where the
advisory thresholds are blocking.

```sh
python scripts/check_structure.py --working-tree --mode feature
python scripts/check_structure.py --working-tree --mode strict
```

## Repository map

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | thin always-on contract and generated machine index |
| `.agents/skills/*/SKILL.md` | source of truth for reusable skills |
| `.claude/skills` | Claude Code links to the same source |
| `.claude/agents` | scoped worker/reviewer adapters |
| `.agents/project-policy.yml` | delivery/research path policy |
| `COMMANDS.md` | canonical command contract |
| `PLANS.md`, `plans/` | durable execution plans when genuinely needed |
| `evals/` | trigger, behavior, and routing eval seeds |
| `scripts/` | validators and generators |
| `reports/` | durable review/measurement outputs |

## 日本語要約

このPlaybookは、Feature完成とCodebase全体の理想化を分離します。
Feature PRは観測可能なDefinition of Doneに対して完成させますが、既存の構造負債、
将来の一般化、可読性上の選好、推測的Hardeningまで同じPRで解消する必要はありません。

一方、現実的なSafety・Security・Privacy・Authorization・Data integrity、互換契約、
Required CI、明示された性能・資源条件は後送しません。構造はAdvisoryとHard guardrailの
二段階で管理し、巨大化を防ぎつつ、既存Fileへ小さな変更を加えるたびに全面分割することを
避けます。

## Generated Skill Catalog

This table is generated from `.agents/skills/*/SKILL.md`.

<!-- BEGIN README SKILL CATALOG (generated) -->
| Skill | Description | Source |
| --- | --- | --- |
| `agent-workflow-contract-review` | Agent workflow contract review | `.agents/skills/agent-workflow-contract-review/SKILL.md` |
| `architecture-decision-analysis` | Architecture decision analysis | `.agents/skills/architecture-decision-analysis/SKILL.md` |
| `branch-completion` | Finish branch and PR lifecycle | `.agents/skills/branch-completion/SKILL.md` |
| `bug-investigation-and-rca` | Bug investigation & RCA | `.agents/skills/bug-investigation-and-rca/SKILL.md` |
| `code-readability` | Proportional code readability | `.agents/skills/code-readability/SKILL.md` |
| `code-smells-and-antipatterns` | Diff-focused maintainability review | `.agents/skills/code-smells-and-antipatterns/SKILL.md` |
| `comment-discipline` | Comment channel discipline | `.agents/skills/comment-discipline/SKILL.md` |
| `concurrency-android` | Android concurrency and background work | `.agents/skills/concurrency-android/SKILL.md` |
| `concurrency-core` | Concurrency design patterns and planning | `.agents/skills/concurrency-core/SKILL.md` |
| `concurrency-ros2` | ROS 2 concurrency patterns | `.agents/skills/concurrency-ros2/SKILL.md` |
| `design-balance` | Responsibility layout design | `.agents/skills/design-balance/SKILL.md` |
| `destructive-refactor` | Replace flawed abstraction safely | `.agents/skills/destructive-refactor/SKILL.md` |
| `dev-workflow` | Risk-routed dev workflow | `.agents/skills/dev-workflow/SKILL.md` |
| `embedded-hot-path-review` | Embedded hot-path review | `.agents/skills/embedded-hot-path-review/SKILL.md` |
| `embedded-nfr-calibration` | Embedded NFR calibration | `.agents/skills/embedded-nfr-calibration/SKILL.md` |
| `embedded-nfr-design` | Embedded physical NFR design | `.agents/skills/embedded-nfr-design/SKILL.md` |
| `embedded-nfr-gate` | Embedded NFR submit gate | `.agents/skills/embedded-nfr-gate/SKILL.md` |
| `embedded-nfr-harness-design` | Embedded NFR harness design | `.agents/skills/embedded-nfr-harness-design/SKILL.md` |
| `embedded-observer-effect-review` | Embedded observer-effect review | `.agents/skills/embedded-observer-effect-review/SKILL.md` |
| `embedded-operating-envelope-discovery` | Embedded operating envelope discovery | `.agents/skills/embedded-operating-envelope-discovery/SKILL.md` |
| `embedded-project-constitution` | Embedded project constitution | `.agents/skills/embedded-project-constitution/SKILL.md` |
| `embedded-system-familiarization` | Principal embedded system familiarization | `.agents/skills/embedded-system-familiarization/SKILL.md` |
| `embedded-target-characterization` | Embedded target characterization | `.agents/skills/embedded-target-characterization/SKILL.md` |
| `error-handling` | Boundary error handling | `.agents/skills/error-handling/SKILL.md` |
| `execution-plans` | Durable handoff ExecPlan | `.agents/skills/execution-plans/SKILL.md` |
| `experiment-loop` | Registered experiment evidence contract | `.agents/skills/experiment-loop/SKILL.md` |
| `failure-retrospective` | Failure learning and promotion routing | `.agents/skills/failure-retrospective/SKILL.md` |
| `function-boundary-governor` | Autonomous function-boundary design | `.agents/skills/function-boundary-governor/SKILL.md` |
| `hardening-workflow` | Measure-tier-stop hardening lane | `.agents/skills/hardening-workflow/SKILL.md` |
| `implementation-economy` | Scope-inversion and abstraction budget | `.agents/skills/implementation-economy/SKILL.md` |
| `japanese-tech-writing` | Japanese technical writing conventions | `.agents/skills/japanese-tech-writing/SKILL.md` |
| `mobile-feature-parity` | Cross-platform mobile capability parity | `.agents/skills/mobile-feature-parity/SKILL.md` |
| `mobile-release-coordination` | Coordinated iOS and Android release gate | `.agents/skills/mobile-release-coordination/SKILL.md` |
| `mobile-runtime-verification` | Mobile runtime verification | `.agents/skills/mobile-runtime-verification/SKILL.md` |
| `observability` | Boundary-focused observability | `.agents/skills/observability/SKILL.md` |
| `performance-review` | Generic performance review | `.agents/skills/performance-review/SKILL.md` |
| `playbook-template-authoring` | Reusable playbook/template authoring | `.agents/skills/playbook-template-authoring/SKILL.md` |
| `poc-workflow` | PoC construction on the research substrate | `.agents/skills/poc-workflow/SKILL.md` |
| `preflight-api-compat` | Public API compatibility preflight | `.agents/skills/preflight-api-compat/SKILL.md` |
| `preflight-auth-session` | Auth/session preflight | `.agents/skills/preflight-auth-session/SKILL.md` |
| `preflight-db-migration` | DB migration preflight | `.agents/skills/preflight-db-migration/SKILL.md` |
| `preflight-domain-template` | Domain preflight skill template | `.agents/skills/preflight-domain-template/SKILL.md` |
| `preflight-engineering` | Preflight agent context and handoff | `.agents/skills/preflight-engineering/SKILL.md` |
| `preflight-mobile-app` | Mobile app preflight | `.agents/skills/preflight-mobile-app/SKILL.md` |
| `project-initialization` | Initialize canonical verify commands | `.agents/skills/project-initialization/SKILL.md` |
| `project-structure` | Two-tier structure guardrails | `.agents/skills/project-structure/SKILL.md` |
| `quality-gate` | Blocking-finding quality gate | `.agents/skills/quality-gate/SKILL.md` |
| `receiving-code-review` | Process review feedback safely | `.agents/skills/receiving-code-review/SKILL.md` |
| `refactor-workflow` | Behavior-preserving refactor lane | `.agents/skills/refactor-workflow/SKILL.md` |
| `requesting-code-review` | Prepare focused review requests | `.agents/skills/requesting-code-review/SKILL.md` |
| `requirements-engineering` | Requirements engineering | `.agents/skills/requirements-engineering/SKILL.md` |
| `research-synthesis` | Research decision synthesis | `.agents/skills/research-synthesis/SKILL.md` |
| `research-workflow` | Research-mode router | `.agents/skills/research-workflow/SKILL.md` |
| `staged-lowering` | Staged lowering for constrained code | `.agents/skills/staged-lowering/SKILL.md` |
| `test-driven-development` | Test-driven development workflow | `.agents/skills/test-driven-development/SKILL.md` |
| `thread-safety-tooling` | Thread-safety verification | `.agents/skills/thread-safety-tooling/SKILL.md` |
| `tonemana-apply` | Apply tone/manner choice to UIUX Pack | `.agents/skills/tonemana-apply/SKILL.md` |
| `tonemana-catalog` | Tone & Manner catalog + previews | `.agents/skills/tonemana-catalog/SKILL.md` |
| `uidesign-flow` | tonemana → tokens → component+screen previews | `.agents/skills/uidesign-flow/SKILL.md` |
| `uidesign-orchestrator` | Explicit UI evidence orchestration | `.agents/skills/uidesign-orchestrator/SKILL.md` |
| `uiux-core` | UI/UX core contract + deterministic review bundle | `.agents/skills/uiux-core/SKILL.md` |
| `uiux-flow-preview` | Transition map preview with pan/zoom + focus review | `.agents/skills/uiux-flow-preview/SKILL.md` |
| `unit-test-design` | Risk-tiered unit test design | `.agents/skills/unit-test-design/SKILL.md` |
| `user-value-delivery` | User-value delivery governor | `.agents/skills/user-value-delivery/SKILL.md` |
| `variant-exploration` | Executable variant exploration | `.agents/skills/variant-exploration/SKILL.md` |
| `visual-regression-testing` | Tool-agnostic UI visual verification contract | `.agents/skills/visual-regression-testing/SKILL.md` |
| `working-with-legacy-code` | Working with legacy code safely | `.agents/skills/working-with-legacy-code/SKILL.md` |
<!-- END README SKILL CATALOG (generated) -->

## Validation

For a normal change, use `make verify`. The explicit command list is retained so
`scripts/lint_command_docs.py` can detect drift with the Makefile chain.

- `python scripts/validate_skills.py`
- `python scripts/update_skill_requires.py --check`
- `python scripts/sync_claude_skills.py --check`
- `python scripts/generate_route_lockfile.py --check`
- `python scripts/validate_skill_trigger_evals.py`
- `python scripts/validate_skill_behavior_evals.py`
- `python scripts/validate_function_design_protocol.py`
- `python scripts/validate_model_routing.py`
- `python scripts/validate_model_routing_evals.py`
- `python scripts/check_research_evidence.py --check-ledger`
- `python scripts/check_context_budget.py`
- `python scripts/check_structure.py --working-tree`
- `python scripts/lint_instruction_graph.py`
- `python scripts/lint_command_docs.py`
- `python scripts/lint_artifacts.py`
- `python scripts/lint_submission.py --working-tree`
- `python scripts/report_skill_inventory.py --check --format text`
- `python scripts/generate_agent_index.py --check`

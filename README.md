# AI Agent Instructions Playbook

A reusable, validated operating layer for software-development agents.

[English](#english) · [日本語](#japanese) · [Skill catalog](#skill-catalog) · [Validation](#validation)

<a id="english"></a>
## English

### What this is

This repository is a versioned collection of **instructions, workflows, Agent Skills, templates, and validators** for software-development agents.

It is intended to sit between a project request and the coding agent:

```text
project request
    ↓
project-local AGENTS.md / policy / canonical commands
    ↓
preflight or workflow router
    ↓
only the specialist skills needed for this task
    ↓
implementation, tests, evidence, and final gate
```

The playbook helps an agent answer five practical questions before it edits code:

1. What should I read first?
2. Which workflow and specialist skills apply?
3. Which constraints and approval boundaries must not be crossed?
4. What tests or measurements are required?
5. What evidence is needed before claiming completion?

The design deliberately separates:

- **thin, stable instructions** that are safe to keep in context
- **on-demand skills** loaded only when their trigger matches
- **project-local facts** such as architecture choices, commands, credentials, and environments
- **mechanical validation** that checks routing, structure, context budgets, and generated files

### What this is not

This repository is not:

- an application framework or runtime dependency
- an autonomous agent orchestrator or security sandbox
- a replacement for project requirements, code review, CI, tests, or human approvals
- a generic prompt dump that should be loaded in full for every task
- a source of project secrets, signing credentials, production tokens, or environment-specific decisions

### Supported clients

| Client | Skill location | Explicit invocation |
| --- | --- | --- |
| Codex | `.agents/skills` | `$skill-name` |
| GitHub Copilot CLI / agent mode | `.agents/skills` | `/skill-name` |
| Claude Code | `.claude/skills` symlinks | `/skill-name` |

Agents can normally select skills from their descriptions. Explicit invocation is useful when you want to force a particular workflow or make routing unambiguous.

### How to use it

1. Clone this playbook once in a stable local location.
2. Run `setup.sh` against each target Git worktree that should see the shared skills.
3. Keep project-specific facts and commands in the target repository.
4. Give the agent the task normally; let skill descriptions route it, or invoke a skill explicitly when needed.
5. Require the project's canonical verification and the appropriate final gate before accepting completion.

> `setup.sh` exposes skills. It does not install an agent, copy project instructions, grant credentials, or change production systems.

### Quick start

Requirements:

- a Git worktree root
- a POSIX shell environment with symlink support, such as Linux, macOS, or WSL
- a local clone of this playbook

Clone the playbook once:

```sh
git clone https://github.com/shunta-sato/agent-instructions-playbook.git \
  ~/tools/agent-instructions-playbook
```

Expose the shared skills in an existing project:

```sh
~/tools/agent-instructions-playbook/setup.sh /path/to/your-project
```

The default setup:

- links the complete playbook skill directory into `.agents/skills`
- links the same source into `.claude/skills`
- records the links in the target worktree's Git-local exclude file
- does not overwrite an existing path
- does not copy project-specific root files such as `AGENTS.md` or `COMMANDS.md`

When the target repository already has local or third-party skills, use overlay mode:

```sh
~/tools/agent-instructions-playbook/setup.sh --overlay /path/to/your-project
```

Overlay mode links each playbook skill separately and preserves non-conflicting project or external skills. See [`EXTERNAL_SKILLS.md`](EXTERNAL_SKILLS.md) for pinning and review rules, including Flutter and Dart upstream skills.

Because the setup uses symlinks, updating the central clone updates every linked worktree:

```sh
git -C ~/tools/agent-instructions-playbook pull --ff-only
```

Pin or vendor a known revision instead when reproducibility is more important than receiving updates immediately.

### What the target project still owns

`setup.sh` shares reusable skills only. The target repository remains responsible for:

- its own `AGENTS.md` and nested instruction files
- product requirements and acceptance criteria
- architecture and dependency choices
- canonical build, lint, test, benchmark, and deployment commands
- credentials, signing material, environments, and approval policy
- platform- and organization-specific exceptions

For a new or unfamiliar repository, start with `preflight-engineering`. If canonical commands are missing or still contain placeholders, use `project-initialization`.

### Day-to-day use

A normal delivery task follows this shape:

```text
preflight when needed
    ↓
dev-workflow
    ↓
triggered specialist skills only
    ↓
canonical build / lint / tests / measurements
    ↓
quality-gate
```

Recommended entry points:

| Situation | Start with | Finish with |
| --- | --- | --- |
| Routine code or test change | `dev-workflow` | `quality-gate` |
| New, unfamiliar, high-risk, multi-service, or long-running work | `preflight-engineering` | `quality-gate` |
| Requirements are ambiguous or NFRs are vague | `requirements-engineering` | the routed implementation workflow |
| Research, probes, or exploratory experiments | `research-workflow` | `research-synthesis` |
| Mobile / Flutter / iOS / Android project setup | `preflight-mobile-app` through `preflight-engineering` | `quality-gate` |
| Coordinated iOS and Android release | `mobile-release-coordination` | its `ready | no-go | not-applicable` record |
| Embedded or target-local system discovery | `embedded-system-familiarization` | the routed embedded NFR gate |

Example for an unfamiliar Flutter application connected to a cloud API:

```text
preflight-engineering
    └─ preflight-mobile-app
         ├─ requirements-engineering
         ├─ preflight-api-compat
         ├─ preflight-auth-session
         └─ architecture-decision-analysis, when a measurable boundary decision exists
    ↓
dev-workflow
    ├─ mobile-feature-parity, when both mobile platforms share a capability
    ├─ performance-review, when there is a real performance risk or target
    └─ other triggered implementation skills
    ↓
quality-gate
    ↓
mobile-release-coordination, when a coordinated store/backend release is required
```

### Repository map

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Thin always-on contract and generated skill index for this repository |
| `.agents/skills/*/SKILL.md` | Source of truth for reusable first-party Agent Skills |
| `.claude/skills` | Claude Code links to the same skill source |
| `.agents/project-policy.yml` | Delivery/research mode policy and path classification |
| `COMMANDS.md` | Canonical command contract |
| `PLANS.md`, `plans/` | ExecPlan guidance and durable plans |
| `EXTERNAL_SKILLS.md` | External skill overlay, pinning, trust, and precedence rules |
| `scripts/` | Validators, generators, routing helpers, and inspection tools |
| `evals/` | Trigger, behavior, and model-routing evaluation seeds |
| `reports/` | Review and measurement outputs retained by the playbook project |

---

<a id="japanese"></a>
## 日本語

### これは何か

このリポジトリは、ソフトウェア開発エージェント向けの**指示、ワークフロー、Agent Skill、テンプレート、検証ツール**をバージョン管理するPlaybookです。

プロジェクトへの依頼とコーディングエージェントの間に、次の運用層を置くことを目的としています。

```text
プロジェクトへの依頼
    ↓
プロジェクト固有のAGENTS.md・ポリシー・標準コマンド
    ↓
PreflightまたはWorkflow Router
    ↓
そのタスクに必要な専門Skillだけを選択
    ↓
実装・Test・Evidence・最終Gate
```

エージェントがコードを変更する前に、次の五点を判断できるようにします。

1. 最初に何を読むべきか
2. どのWorkflowと専門Skillを使うべきか
3. 越えてはいけない制約・権限・承認境界は何か
4. 必要なTestや計測は何か
5. 完了を主張するために、どのEvidenceが必要か

設計上、次を明確に分離しています。

- Contextへ常時入れてよい、薄く安定した指示
- Triggerが一致した場合だけ読むOn-demand Skill
- Architecture、Command、Credential、Environmentなどのプロジェクト固有情報
- Routing、構造、Context量、自動生成物を確認する機械的Validation

### これは何ではないか

このリポジトリは、次のものではありません。

- Application FrameworkやRuntime依存Library
- 自律Agent OrchestratorやSecurity Sandbox
- 要件定義、Code Review、CI、Test、人間の承認の代替
- 毎回すべてをContextへ投入するPrompt集
- Secret、Signing Credential、Production Token、環境固有判断の保管場所

### 対応クライアント

| Client | Skill配置先 | 明示的な呼び出し |
| --- | --- | --- |
| Codex | `.agents/skills` | `$skill-name` |
| GitHub Copilot CLI / agent mode | `.agents/skills` | `/skill-name` |
| Claude Code | `.claude/skills`のSymlink | `/skill-name` |

通常はSkillの`description`からエージェントが自動選択できます。特定のWorkflowを確実に使わせたい場合や、Routingを明示したい場合は明示呼び出しを使います。

### 使い方の全体像

1. このPlaybookを、安定した場所へ一度だけCloneします。
2. 共有Skillを利用する各Git worktreeに対して`setup.sh`を実行します。
3. プロジェクト固有の情報と標準コマンドは、対象リポジトリ側で管理します。
4. 通常どおりタスクを依頼し、Skillの`description`による自動Routingに任せます。必要な場合だけSkillを明示呼び出しします。
5. 完了を受け入れる前に、対象プロジェクトの標準検証と適切な最終Gateを要求します。

> `setup.sh`が行うのはSkillの公開です。エージェントのInstall、プロジェクト指示のCopy、Credentialの付与、Production Systemの変更は行いません。

### 導入方法

前提条件は次のとおりです。

- Git worktreeのRoot
- Symlinkを利用できるPOSIX Shell環境。Linux、macOS、WSLなど
- このPlaybookのLocal clone

最初にPlaybookを一度だけCloneします。

```sh
git clone https://github.com/shunta-sato/agent-instructions-playbook.git \
  ~/tools/agent-instructions-playbook
```

既存プロジェクトへ共有Skillを公開します。

```sh
~/tools/agent-instructions-playbook/setup.sh /path/to/your-project
```

Default setupは次を行います。

- Playbook全体のSkill Directoryを`.agents/skills`へLink
- 同じSourceを`.claude/skills`へLink
- 対象worktreeのGit-local excludeへLinkを登録
- 既存Pathを上書きしない
- `AGENTS.md`や`COMMANDS.md`など、プロジェクト固有のRoot fileはCopyしない

対象リポジトリにLocal SkillやThird-party Skillが既にある場合は、Overlay modeを使います。

```sh
~/tools/agent-instructions-playbook/setup.sh --overlay /path/to/your-project
```

Overlay modeはPlaybook Skillを一件ずつLinkし、名前が衝突しないProject Skill・External Skillを保持します。Flutter/Dart公式Skillを含むPinning・Review規則は[`EXTERNAL_SKILLS.md`](EXTERNAL_SKILLS.md)を参照してください。

SetupはSymlinkを使うため、中央のCloneを更新すると、Link済みworktreeにも反映されます。

```sh
git -C ~/tools/agent-instructions-playbook pull --ff-only
```

更新を即時反映するより再現性を優先する場合は、既知のRevisionへ固定するか、管理下へVendorしてください。

### 対象プロジェクト側で管理するもの

`setup.sh`が共有するのは再利用可能なSkillだけです。次の項目は対象リポジトリが管理します。

- プロジェクト固有の`AGENTS.md`とNested instruction
- Product要件とAcceptance Criteria
- ArchitectureとDependencyの選択
- 標準のBuild、Lint、Test、Benchmark、Deploy Command
- Credential、Signing material、Environment、Approval policy
- Platform・組織固有の例外

新規または不慣れなリポジトリでは、`preflight-engineering`から始めます。標準Commandが未定義、またはPlaceholderが残っている場合は`project-initialization`を使います。

### 日常的な使い方

通常のDelivery Taskは次の流れです。

```text
必要な場合だけPreflight
    ↓
dev-workflow
    ↓
Triggerした専門Skillだけを利用
    ↓
標準Build・Lint・Test・計測
    ↓
quality-gate
```

推奨Entry pointは次のとおりです。

| 状況 | 最初に使うSkill | 完了時 |
| --- | --- | --- |
| 通常のCode・Test変更 | `dev-workflow` | `quality-gate` |
| 新規、不慣れ、高Risk、複数Service、長期作業 | `preflight-engineering` | `quality-gate` |
| 要件が曖昧、NFRが定量化されていない | `requirements-engineering` | Routingされた実装Workflow |
| Research、Probe、探索的Experiment | `research-workflow` | `research-synthesis` |
| Mobile / Flutter / iOS / Androidの初期化 | `preflight-engineering`経由の`preflight-mobile-app` | `quality-gate` |
| iOS・Androidの協調Release | `mobile-release-coordination` | `ready | no-go | not-applicable` Record |
| Embedded・Target-local Systemの把握 | `embedded-system-familiarization` | RoutingされたEmbedded NFR Gate |

Cloud APIと連携する不慣れなFlutter Applicationでは、例えば次のようにRoutingします。

```text
preflight-engineering
    └─ preflight-mobile-app
         ├─ requirements-engineering
         ├─ preflight-api-compat
         ├─ preflight-auth-session
         └─ 定量的な境界判断がある場合はarchitecture-decision-analysis
    ↓
dev-workflow
    ├─ 両Mobile Platformで同じCapabilityを提供する場合はmobile-feature-parity
    ├─ 実際のPerformance RiskまたはTargetがある場合はperformance-review
    └─ その他、Triggerした実装Skill
    ↓
quality-gate
    ↓
Store・Backendを協調Releaseする場合はmobile-release-coordination
```

### リポジトリ構成

| Path | 役割 |
| --- | --- |
| `AGENTS.md` | このリポジトリの薄い常時指示と、自動生成Skill Index |
| `.agents/skills/*/SKILL.md` | 再利用可能なFirst-party Agent SkillのSource of truth |
| `.claude/skills` | 同じSkill SourceをClaude Codeへ公開するLink |
| `.agents/project-policy.yml` | Delivery/Research modeとPath分類 |
| `COMMANDS.md` | 標準Command Contract |
| `PLANS.md`, `plans/` | ExecPlanの指針と永続Plan |
| `EXTERNAL_SKILLS.md` | External SkillのOverlay、Pinning、Trust、優先順位 |
| `scripts/` | Validator、Generator、Routing helper、Inspection tool |
| `evals/` | Trigger、Behavior、Model routingのEval seed |
| `reports/` | Playbook Projectで保持するReview・Measurement output |

---

## Maintainer reference / メンテナ向けリファレンス

### Skill authoring policy / Skill作成方針

Keep `AGENTS.md` thin and stable. Put reusable, triggerable workflows in `.agents/skills/<name>/SKILL.md`; move heavier conditional material into `references/`, executable helpers into `scripts/`, and output skeletons into `templates/`.

`AGENTS.md`は薄く安定させます。再利用可能でTrigger可能なWorkflowは`.agents/skills/<name>/SKILL.md`へ置き、条件付きの詳細は`references/`、実行Helperは`scripts/`、成果物の雛形は`templates/`へ分離します。

Prefer fewer active skills with clear trigger boundaries. A broad or core skill should have positive cases and near-miss negative cases, a concrete output contract, and explicit handoffs to neighboring skills.

Active Skillは数を増やすより、Trigger境界を明確にします。広範またはCoreなSkillには、Positive case、Near-miss negative case、具体的なOutput contract、隣接Skillへの明示的Handoffを用意します。

### Skill Delta Gate

Before adding a skill or broadening an existing one, all criteria must pass:

1. **Runtime decision delta** — the change alters proceed/no-proceed, routing, submit/no-submit, or another observable Agent decision.
2. **Existing-skill absorption** — a reference, trigger, anti-trigger, output-contract, or eval update is insufficient.
3. **Trigger boundary** — broad/core skills have at least two positive and three near-miss negative cases.
4. **Output contract** — the skill produces a decision, artifact, verification record, or explicit no-op/no-decision.
5. **Complexity cap** — keep `SKILL.md` workflow-focused and move heavy taxonomy or detail behind conditional resources.

新しいSkillの追加や既存Skillの拡張では、実行時判断が変わること、既存Skillへ吸収できないこと、Trigger境界をEvalできること、具体的Outputがあること、`SKILL.md`を過度に肥大化させないことを確認します。

<a id="skill-catalog"></a>
## Generated Skill Catalog / 自動生成スキルカタログ

The full catalog below is generated from `.agents/skills/*/SKILL.md`. Do not edit the table by hand.

以下の一覧は`.agents/skills/*/SKILL.md`から自動生成されます。Tableを手作業で編集しないでください。

<details>
<summary>Show the complete catalog / 全Skill一覧を表示</summary>

<!-- BEGIN README SKILL CATALOG (generated) -->
| Skill | Description | Source |
| --- | --- | --- |
| `agent-workflow-contract-review` | Agent workflow contract review | `.agents/skills/agent-workflow-contract-review/SKILL.md` |
| `architecture-decision-analysis` | Architecture decision analysis | `.agents/skills/architecture-decision-analysis/SKILL.md` |
| `branch-completion` | Finish branch and PR lifecycle | `.agents/skills/branch-completion/SKILL.md` |
| `bug-investigation-and-rca` | Bug investigation & RCA | `.agents/skills/bug-investigation-and-rca/SKILL.md` |
| `code-readability` | Code readability | `.agents/skills/code-readability/SKILL.md` |
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
| `execution-plans` | ExecPlan: plan/WBS/progress + handoff | `.agents/skills/execution-plans/SKILL.md` |
| `experiment-loop` | Registered experiment evidence contract | `.agents/skills/experiment-loop/SKILL.md` |
| `failure-retrospective` | Failure learning and promotion routing | `.agents/skills/failure-retrospective/SKILL.md` |
| `function-boundary-governor` | Autonomous function-boundary design | `.agents/skills/function-boundary-governor/SKILL.md` |
| `hardening-workflow` | Measure-tier-stop hardening lane | `.agents/skills/hardening-workflow/SKILL.md` |
| `implementation-economy` | Implementation complexity budget | `.agents/skills/implementation-economy/SKILL.md` |
| `japanese-tech-writing` | Japanese technical writing conventions | `.agents/skills/japanese-tech-writing/SKILL.md` |
| `mobile-feature-parity` | Cross-platform mobile capability parity | `.agents/skills/mobile-feature-parity/SKILL.md` |
| `mobile-release-coordination` | Coordinated iOS and Android release gate | `.agents/skills/mobile-release-coordination/SKILL.md` |
| `observability` | Observability plan and checklist | `.agents/skills/observability/SKILL.md` |
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
| `project-structure` | Physical code layout and structure budget | `.agents/skills/project-structure/SKILL.md` |
| `quality-gate` | Final quality gate | `.agents/skills/quality-gate/SKILL.md` |
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
| `visual-regression-testing` | Tool-agnostic UI visual verification contract | `.agents/skills/visual-regression-testing/SKILL.md` |
| `working-with-legacy-code` | Working with legacy code safely | `.agents/skills/working-with-legacy-code/SKILL.md` |
<!-- END README SKILL CATALOG (generated) -->

</details>

## Validation

For a normal change, use the repository's `make` targets. The list below is intentionally explicit because `scripts/lint_command_docs.py` checks that the README remains synchronized with the validator chain.

通常の変更ではRepositoryの`make` targetを使用します。以下の一覧は、`scripts/lint_command_docs.py`がValidator chainとの同期を確認するため、明示的に保持しています。

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

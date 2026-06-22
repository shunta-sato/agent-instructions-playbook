# Lightweight Run Ledger — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Add PR 4 of the Superpowers improvement sequence: a lightweight JSONL run ledger for delegated agent work.
- Preserve evidence for task brief identity, model-routing metadata, changed files, validation results, quality-gate status, and outcome without requiring any external observability stack.

## Scope

### In scope

- Add `.agents/runs/.gitignore` and `.agents/runs/agent-runs.jsonl`.
- Add `scripts/agent_run.py` to issue run IDs, save task briefs, capture changed files, append run records, and compute preliminary acceptance.
- Add `scripts/parse_codex_jsonl.py` to optionally extract token counts from Codex CLI JSONL.
- Add `scripts/judge_agent_run.py` to judge one ledger record without relying on agent self-assessment.
- Add `scripts/summarize_agent_runs.py` to summarize ledger records for review.
- Add workflow-contract evidence for the run-ledger CLI and JSONL contract.

### Out of scope / non-goals

- Do not introduce OpenTelemetry, collectors, OTLP endpoints, metrics backends, dashboards, or required telemetry environment variables.
- Do not require token counts for run acceptance.
- Do not integrate delegated-run enforcement into `quality-gate`; that is PR 5.
- Do not add model catalogs, generated agents, route lockfiles, or behavior eval schemas.
- Do not redefine the subagent delegation schema; normalize from the existing task brief/report fields.

## Constraints / Quality targets

- Resource budget: scripts are stdlib-only and append one JSON object per run.
- Safety/security/privacy: task brief copies and run logs stay under `.agents/runs/`; per-run brief directories are ignored by git by default.
- Compatibility / rollout constraints: `make verify` remains the canonical verification chain; new scripts must `py_compile`.
- Operability: ledger records use explicit `run_id`, `brief_path`, `allowed_files`, `changed_files`, validation command results, `quality_gate`, and separate outcome fields.
- Acceptance constraints: token telemetry may be `not_collected`; validation failure and agent completion are separate; scope violations make `accepted` false.

## Context & Orientation

- Key paths:
  - `.agents/runs/agent-runs.jsonl`
  - `scripts/agent_run.py`
  - `scripts/parse_codex_jsonl.py`
  - `scripts/judge_agent_run.py`
  - `scripts/summarize_agent_runs.py`
  - `.agents/skills/execution-plans/templates/subagent-task-brief.md`
  - `.agents/skills/execution-plans/templates/subagent-report.md`
- Existing behavior:
  - PR #62 added subagent brief/report templates and explicitly deferred the run ledger.
  - `make verify` compiles all `scripts/*.py` and validates skill/model-routing artifacts.
- Conventions to follow:
  - Keep Python scripts dependency-free.
  - Use explicit paths and JSON-compatible objects rather than latest/newest file discovery.
  - Keep generated/runtime run artifacts ignored unless intentionally staged.
- Unknowns:
  - Future PR 5 may tighten how `quality-gate` treats `quality_gate: not_run`; PR 4 records the field but does not enforce the future policy.

## Design

### Boundary sketch

- Components involved:
  - `agent_run.py`: shared ledger helpers plus the `record` CLI.
  - `parse_codex_jsonl.py`: optional harness-native token extraction for Codex JSONL.
  - `judge_agent_run.py`: single-run acceptance judgment using ledger fields.
  - `summarize_agent_runs.py`: ledger-level counts for review.
  - `.agents/runs/agent-runs.jsonl`: append-only JSONL ledger.
- Boundary crossings:
  - Filesystem reads/writes for task brief copies and JSONL appends.
  - Local git read-only commands for changed-file discovery.
  - Optional Codex CLI JSONL parsing.
- DTOs / interfaces:
  - JSONL run records with `schema_version: 1` and `record_type: agent_run`.
  - `validation.commands[]` entries record `cmd`, `exit_code`, and `passed`.
  - `outcome` separates `agent_completed`, `validation_passed`, `scope_compliant`, and `accepted`.
- Error handling strategy:
  - CLI boundary catches `ValueError`, prints one actionable error, and exits nonzero.
  - Missing ledgers or missing run IDs are command failures.
  - Missing token data is not a failure; it records `telemetry.status: not_collected`.
  - Scope violations and validation failures are judgment results, not parser failures.

### Observability

- Logs: the ledger itself is the local evidence log; `run_id` is the correlation ID.
- Metrics: `summarize_agent_runs.py` reports local counts by acceptance, task class, and telemetry status.
- Traces: none; this PR intentionally avoids external tracing.

### Testing strategy

- Unit-level script checks:
  - `python3 scripts/parse_codex_jsonl.py <sample-jsonl> --format json`
  - `python3 scripts/judge_agent_run.py --ledger <sample-ledger> --run-id <id> --require-accepted`
  - rejection check for changed files outside allowed files.
- Integration checks:
  - temp git repo exercise for `scripts/agent_run.py record --changed-from-git`.
  - `python3 scripts/summarize_agent_runs.py --ledger <sample-ledger> --format json`.
- Canonical checks:
  - `python3 -m py_compile scripts/*.py`
  - `make verify`
- Stress / concurrency tests: not applicable; no concurrent writer guarantee is introduced.
- Manual verification: inspect workflow-contract report and git diff for forbidden telemetry infrastructure.

## Milestones (high-level plan)

1. Define the ledger schema and acceptance rules in the ExecPlan.
2. Add the `.agents/runs/` tracked seed files and ignored runtime artifact policy.
3. Implement `agent_run.py`, `parse_codex_jsonl.py`, `judge_agent_run.py`, and `summarize_agent_runs.py`.
4. Add workflow-contract evidence for the CLI/JSONL producer-consumer chain.
5. Run targeted ledger checks, canonical verification, publish PR, request review, and update automation.

## Progress (WBS)

- [x] (P0) Merge PR #62 and sync `main` — deliverable: local `main` at `89ab8f3` — verify: `git pull --ff-only origin main`.
- [x] (P1) Create branch and ExecPlan — deliverable: `codex/lightweight-run-ledger`, this plan — verify: branch exists and plan path created.
- [x] (P2) Add run ledger files — deliverable: `.agents/runs/.gitignore`, `.agents/runs/agent-runs.jsonl` — verify: summary script skips metadata seed.
- [x] (P3) Implement scripts — deliverable: four stdlib Python CLIs — verify: targeted temp-ledger exercises passed.
- [x] (P4) Add workflow-contract evidence — deliverable: `reports/workflow-contract-review/20260623-lightweight-run-ledger.md` — verify: decision `submit`.
- [x] (P5) Verification and publication — deliverable: commit, push, draft PR — verify: https://github.com/shunta-sato/agent-instructions-playbook/pull/63 and green local verification.

## Route / Required Branches

- ExecPlan required: yes.
- Risk level: normal for new Agent-facing CLI workflow and ledger schema.
- Default lane: required; this adds new scripts and a reusable evidence contract.
- Required branches:
  - `execution-plans`: multi-step PR and handoff-ready plan.
  - `implementation-economy`: normal-risk work and new script/helper boundaries.
  - `design-balance`: four new modules with distinct responsibilities.
  - `function-boundary-governor`: new helper and CLI boundaries.
  - `error-handling`: filesystem, JSONL, git, and CLI failure contracts.
  - `agent-workflow-contract-review`: Agent-facing run ledger and validation artifacts.
  - `quality-gate`: mandatory final submit gate.
- Non-triggered branches:
  - `architecture-decision-analysis`: the plan already chose lightweight JSONL over external telemetry; no new option comparison is needed.
  - `observability`: this PR records local workflow evidence but does not add runtime service signals.
  - `performance-review`: no request/render/job hot path or input-proportional production path.
  - embedded/concurrency/UI/legacy/staged-lowering branches: not applicable.

## Requirements / Acceptance

- EARS-1: When `agent_run.py record` is given a task brief, model-routing metadata, allowed files, changed files, and validation results, it shall append one `agent_run` JSONL record with a generated or supplied `run_id`.
- EARS-2: When token telemetry is unavailable, the record shall still be written with `telemetry.status = not_collected`.
- EARS-3: When validation fails but the agent completed execution, the judgment shall expose `agent_completed: true` and `validation_passed: false` separately.
- EARS-4: When `changed_files` contains a path outside `allowed_files`, the judgment shall set `accepted: false`.
- EARS-5: When Codex CLI JSONL contains token usage, `parse_codex_jsonl.py` shall extract token fields without requiring external telemetry infrastructure.

## Responsibility Map

| Unit | Name | Responsibility sentence | Reason to change | Dependency direction |
| --- | --- | --- | --- | --- |
| module | `agent_run.py` | Own ledger record construction, JSONL append/read helpers, git changed-file discovery, and acceptance evaluation. | Run ledger schema or recording policy changes. | Depended on by judge/summarize; optionally imports Codex parser. |
| module | `parse_codex_jsonl.py` | Extract optional token usage from Codex CLI JSONL. | Codex JSONL token event shape changes. | Independent; imported by `agent_run.py` only for optional telemetry. |
| module | `judge_agent_run.py` | Render one run judgment and optionally fail on rejection. | Review/quality-gate needs a single-run decision. | Depends on `agent_run.py` helpers. |
| module | `summarize_agent_runs.py` | Render ledger-level counts by acceptance, task class, and telemetry status. | Review reporting needs aggregate ledger summaries. | Depends on `agent_run.py` helpers. |

Layout decision: keep four modules because each has a distinct caller-facing CLI and reason to change. Reject a single oversized script because it would mix optional Codex parsing, record writing, judging, and reporting; reject a shared utility module because `agent_run.py` can hold the small stable ledger helpers without adding another file.

## Implementation Economy

- Changed files target: 8 tracked files or fewer.
- New classes/modules target: 0 classes, 4 script modules, 1 run-ledger directory.
- New helpers/wrappers/adapters target: small local helpers only; no generic utility layer.
- New indirection layers target: 0.
- Rough production/test line budget: initially under 650 net script lines plus plan/report evidence; actual script line count is about 708 because CLI argument handling and text/json rendering are explicit.
- Worth-its-weight decisions:
  - `agent_run.py`: keeps ledger schema and acceptance policy in one importable place.
  - `parse_codex_jsonl.py`: isolates optional Codex token parsing so token absence never blocks run recording.
  - `judge_agent_run.py`: gives PR 5 a small reusable command boundary without integrating quality-gate now.
  - `summarize_agent_runs.py`: provides review-friendly ledger visibility without requiring external metrics.

## Function Boundary Plan

- New functions will stay command-sized and domain-named; reject vague `util`/`helper` modules.
- `evaluate_run_record` owns acceptance judgment and is reused by judge/summarize to avoid duplicate policy drift.
- JSONL parsing/writing helpers stay in `agent_run.py` because the ledger schema changes with run recording.
- Codex token extraction stays in `parse_codex_jsonl.py` because harness event shape changes independently.

## Error Handling Plan

Relevant headings: `13. Error handling`, `Python`.

- Boundary: CLI argument, filesystem, JSONL, git, and optional Codex JSONL parsing.
- Translation: low-level failures become `ValueError` with path/field context at script boundaries; CLI `main` prints one message and exits `1`.
- Recoverable case: missing token usage returns telemetry `not_collected`, not a command failure.
- Judgment case: validation failure or scope violation returns a structured rejected judgment, not a parser exception.

## Surprises & Discoveries

Record unexpected constraints, gotchas, and newly learned facts (with evidence when possible).

- 2026-06-23: The repository has no `.gitignore`; runtime ignore policy must live in `.agents/runs/.gitignore`.
- 2026-06-23: Script implementation landed at about 708 lines, above the initial 650-line target, without adding classes or a utility layer.

## Decision log

Record decisions and trade-offs (and why).

- 2026-06-23: Use JSONL records with `record_type: agent_run` plus a metadata seed record because the target file should be tracked before runtime appends.
  - Options considered: empty tracked file; metadata seed record; untracked runtime-only ledger.
  - Chosen: metadata seed record skipped by scripts, plus runtime `agent_run` records.
  - Consequences: scripts must ignore non-run JSONL records.
- 2026-06-23: Compute `accepted` from agent completion, validation, scope, and non-failing quality-gate status.
  - Options considered: agent self-reported success; validation-only; validation plus scope plus quality-gate field.
  - Chosen: validation plus scope plus quality-gate field, while preserving separate outcome fields.
  - Consequences: PR 5 can tighten `quality_gate: not_run` without changing ledger shape.
- 2026-06-23: Accept the script line-budget overrun.
  - Options considered: split another shared utility module; compress CLI code; accept overrun.
  - Chosen: accept overrun.
  - Consequences: code stays explicit and class-free; review cost is higher but boundary behavior is easier to inspect.

## Handoff (update at every stop)

- Current branch / commit: `codex/lightweight-run-ledger`, draft PR #63 open at https://github.com/shunta-sato/agent-instructions-playbook/pull/63.
- What is done: PR #62 merged and local `main` synced; branch and ExecPlan created; run-ledger files/scripts and workflow-contract report are implemented; targeted checks and `make verify` passed; PR #63 opened and PR body includes the raw PR URL.
- What is not done: GitHub review response, PR ready-for-review transition, merge, PR 5.
- How to run: `make verify`.
- How to test: targeted temp-ledger script checks; `python3 scripts/parse_codex_jsonl.py <sample> --format json`; `python3 scripts/judge_agent_run.py --ledger <sample> --require-accepted`; `make verify`.
- Known risks / open questions: PR 5 may tighten quality-gate semantics; this PR should only record the field and preliminary judgment.
- Next 1-3 steps: request review through ATLAS/ChatGPT, address review feedback if any, mark ready and merge on Approve.
- Pointers: `scripts/agent_run.py`, `scripts/parse_codex_jsonl.py`, `.agents/skills/execution-plans/templates/`.

## Validation & Acceptance

- AC1: A run can be recorded without external telemetry infrastructure.
  - Verification: temp git repo `agent_run.py record` run with no Codex JSONL writes a ledger record with `telemetry.status: not_collected`.
- AC2: Token counts are optional and only collected from Codex JSONL when supplied.
  - Verification: `parse_codex_jsonl.py` sample JSONL extracts token fields; no-jsonl run still records.
- AC3: Validation failure and agent completion are distinct.
  - Verification: sample rejected record has `agent_completed: true`, `validation_passed: false`, `accepted: false`.
- AC4: Scope violation prevents acceptance.
  - Verification: sample record with changed file outside allowed files is rejected by `judge_agent_run.py`.
- AC5: Canonical verification stays green.
  - Verification: `make verify`.

## Outcomes & Retrospective (fill when done)

- What shipped / merged: draft PR opened at https://github.com/shunta-sato/agent-instructions-playbook/pull/63.
- What went well: the ledger stores task identity, model-routing metadata, validation, scope, outcome, and optional token telemetry without adding external telemetry infrastructure.
- What went wrong: initial script line budget was low; accepted because explicit CLI/error boundaries are easier to review.
- Follow-ups / tech debt tickets: PR 5 should integrate delegated-run evidence into `quality-gate` without redefining a second delegation schema.

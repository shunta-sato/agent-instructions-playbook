# Workflow Contract Review

## Scope

- PR / branch: `codex/lightweight-run-ledger`
- Workflow surfaces:
  - `.agents/runs/agent-runs.jsonl` append-only local run ledger.
  - `.agents/runs/.gitignore` runtime artifact ignore policy.
  - `scripts/agent_run.py` delegated-run record writer and shared ledger judgment helpers.
  - `scripts/parse_codex_jsonl.py` optional Codex CLI token parser.
  - `scripts/judge_agent_run.py` single-run acceptance judgment CLI.
  - `scripts/summarize_agent_runs.py` ledger summary CLI.
- Generated artifacts:
  - Runtime task brief copies under `.agents/runs/<run_id>/brief.md`.
  - Runtime `agent_run` JSONL records appended to `.agents/runs/agent-runs.jsonl`.
  - No external telemetry artifacts, collectors, endpoints, dashboards, model catalogs, route lockfiles, or generated agents are introduced.

## Source-of-truth chain

| Stage | Artifact / command | Producer | Consumer | Notes |
| --- | --- | --- | --- | --- |
| Delegation brief | `.agents/skills/execution-plans/templates/subagent-task-brief.md` copied by `agent_run.py --brief-source` | ExecPlan supervisor | delegated worker, `agent_run.py`, reviewer | This PR records the brief path and copy; it does not create a second brief schema. |
| Worker validation evidence | `--validation-result CMD EXIT_CODE` | supervisor or runner | `agent_run.py`, `judge_agent_run.py` | Exit code is stored separately from agent completion. |
| Changed files | `--changed-file` or `git diff --name-only HEAD --` plus optional untracked files | local git / supervisor | `agent_run.py`, `judge_agent_run.py` | Explicit path list is compared against `allowed_files`. |
| Optional token telemetry | `scripts/parse_codex_jsonl.py <jsonl>` | Codex CLI JSONL output | `agent_run.py`, reviewers | Missing token fields produce `telemetry.status: not_collected`, not failure. |
| Run record | `.agents/runs/agent-runs.jsonl` record with `record_type: agent_run` | `agent_run.py` | `judge_agent_run.py`, `summarize_agent_runs.py`, future quality-gate integration | Non-run metadata records are ignored by readers. |

## Generated argv replay

| Step | Execution location | argv | Required env | Expected artifact | Stop/continue |
| --- | --- | --- | --- | --- | --- |
| record delegated run | controller repo root | `python3 scripts/agent_run.py record --brief-source <brief.md> --allowed-file <path> --validation-result <cmd> <exit_code> ...` | Python 3, git only when `--changed-from-git` is used | one `agent_run` JSONL record and brief copy under `.agents/runs/<run_id>/brief.md` | stop on missing brief, invalid path, invalid JSONL, or git failure |
| parse optional Codex JSONL | controller repo root | `python3 scripts/parse_codex_jsonl.py <codex.jsonl> --format json` | Python 3 | telemetry JSON with `status: collected` or `not_collected` | stop on invalid JSONL; continue on no token payload |
| judge run | controller repo root | `python3 scripts/judge_agent_run.py --run-id <run_id> --require-accepted` | Python 3 | accepted/rejected judgment | nonzero only for missing ledger/run or `--require-accepted` rejection |
| summarize ledger | controller repo root | `python3 scripts/summarize_agent_runs.py --format json` | Python 3 | counts by acceptance, task class, telemetry status | stop on invalid/missing ledger |
| canonical verification | controller repo root | `make verify` | Make, Python 3, git | full repository verification output | stop on nonzero command |

## Producer/consumer consistency

| Producer | Artifact | Consumer | Required identity match | Result |
| --- | --- | --- | --- | --- |
| task brief template | task name, task class, capability profile, prompt detail, brief path | `agent_run.py` record fields | run record repeats task class, profile, prompt detail, and copied brief path | pass |
| `agent_run.py` | `allowed_files`, `changed_files`, validation commands/results, telemetry, outcome | `judge_agent_run.py` and `summarize_agent_runs.py` | both import `evaluate_run_record` from `agent_run.py` rather than duplicating policy | pass |
| Codex JSONL parser | telemetry dict | `agent_run.py` | only supplied explicit `--codex-jsonl` path is parsed | pass |
| git changed-file discovery | repo-relative paths | run record scope check | paths are normalized relative to the explicit repo root | pass |

## Run-set / target / workflow identity consistency

| Identity | Producer value | Consumer value | Result |
| --- | --- | --- | --- |
| run set | one `run_id` and one JSONL `agent_run` record | judge and summary commands select by explicit `run_id` or latest record only within the supplied ledger | pass |
| workflow id | lightweight delegated run ledger | ExecPlan, scripts, workflow-contract report, PR scope | pass |
| target id / class | `task_class`, `capability_profile`, `prompt_detail`, `brief_path` | run record, judge output, summary grouping | pass |

## Controller / target-local execution locations

| Step | Expected location | Actual/generated location | Result |
| --- | --- | --- | --- |
| ledger write | controller repo root | `.agents/runs/agent-runs.jsonl` under explicit repo root | pass |
| brief copy | controller repo root | `.agents/runs/<run_id>/brief.md` under ledger directory | pass |
| git diff read | controller repo root | `git -C <repo-root> diff --name-only HEAD --` | pass |
| target-local commands | not generated by this PR | none | pass |

## Deployment/runtime discovery

| Runtime boundary | Install path | Invocation path | Env/PATH assumption | Preflight | Result |
| --- | --- | --- | --- | --- | --- |
| Python scripts | repository `scripts/` | `python3 scripts/<name>.py` | Python 3 stdlib only | `python3 -m py_compile scripts/*.py` | pass |
| run ledger | repository `.agents/runs/` | explicit ledger path or default `.agents/runs/agent-runs.jsonl` | parent directory writable by local agent | temp repo `agent_run.py record` exercise | pass |
| git changed files | local git checkout | `git -C <repo-root>` | git exists only when caller requests `--changed-from-git` | temp repo exercise | pass |
| optional Codex JSONL | caller-supplied path | `--codex-jsonl <path>` | no implicit discovery by timestamp/name | sample JSONL parser exercise | pass |

## Forbidden fallback checks

- filename-order artifact selection: pass; ledger and Codex JSONL paths are explicit.
- mtime/latest/newest artifact inference: pass; no directory scan chooses newest brief, report, or JSONL.
- stale prompt fallback: pass; task brief is explicitly copied from `--brief-source`.
- raw co-presence as causal evidence: pass; `run_id`, `brief_path`, `allowed_files`, `changed_files`, validation results, and outcome are recorded in one JSON object.
- second delegation schema: pass; the run record stores fields already present in the subagent brief/report contract instead of defining a new task brief format.

## Claim boundaries

- Workflow authority artifacts: `.agents/runs/agent-runs.jsonl`, `.agents/runs/.gitignore`, and the four scripts.
- Validation artifacts: targeted temp-ledger exercises, `python3 -m py_compile scripts/*.py`, `make verify`.
- Measurement artifacts: optional token fields from an explicit Codex JSONL file only.
- Blocked claims: no model quality, cost, latency, production readiness, behavior eval coverage, generated-agent correctness, or quality-gate enforcement is claimed.
- Token telemetry: optional; `not_collected` is an acceptable ledger status.

## Implementation Economy Evidence

Complexity Budget:

- Changed files target: 8 tracked files or fewer.
- New classes/modules target: 0 classes, 4 script modules, 1 run-ledger directory.
- New helpers/wrappers/adapters target: local helpers only.
- New indirection layers target: 0.
- Rough line budget: initially under 650 script lines; actual is about 708 lines because CLI argument handling and text/json renderers are explicit.
- Budget decision: accept the line overrun because the implementation remains stdlib-only, class-free, and avoids a generic shared utility module.

Post-Implementation Economy Audit:

| New abstraction | Justification | Decision | Evidence |
| --- | --- | --- | --- |
| `.agents/runs/` | Gives delegated runs a stable local evidence location while ignoring per-run brief copies by default. | keep | `.gitignore` tracks only itself and the ledger seed. |
| `agent_run.py` | Centralizes ledger schema, record writing, git changed-file discovery, and acceptance evaluation. | keep | judge/summarize import `evaluate_run_record`. |
| `parse_codex_jsonl.py` | Isolates optional harness-native token parsing from core run recording. | keep | no-jsonl runs still record with `not_collected`. |
| `judge_agent_run.py` | Provides a single-run decision boundary for reviewers and later quality-gate use. | keep | `--require-accepted` fails on scope violation. |
| `summarize_agent_runs.py` | Provides review-friendly aggregate counts without external metrics. | keep | temp-ledger summary exercise reports acceptance and telemetry counts. |

## Function Boundary Evidence

| Function / module | Semantic neighbors | Decision | Rationale |
| --- | --- | --- | --- |
| `evaluate_run_record` | `validation_passed`, `quality_gate_allows_acceptance`, judge/summarize call sites | keep | Owns acceptance policy once so later consumers do not drift. |
| `load_agent_run_records` | `append_jsonl`, JSONL readers in judge/summarize | keep | Skips metadata records and translates JSONL parse failures at the boundary. |
| `extract_telemetry_from_file` | `telemetry_from_args` | keep separate | Codex event shape can change independently from ledger schema. |
| CLI `main` functions | existing repository script CLIs | keep local | Each command has a distinct user-facing boundary and exit behavior. |

## Findings

| ID | Severity | Finding | Required fix |
| --- | --- | --- | --- |
| none | none | No contract findings. | none |

## Decision

submit

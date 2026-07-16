# Quality-gate exit checklist

This checklist is for `$quality-gate` only.
Focus on final decision criteria, not broad re-review taxonomy.

Sweep rule: evaluate every item in every applicable section in one complete pass, collecting all failures. Never stop at the first failed item and never decide before the pass is finished.

## 1) Command status (required)

- Canonical commands are recorded with exact commands + key results.
- If external systems/tools were involved, live-discovery evidence is recorded before static examples were trusted: command/interface source, version or status output, schema/config path, connection state, and artifact/log path.
- Required depth matches routed risk:
  - low risk: canonical minimum for changed surface
  - normal/high risk: full chain (build / format / static analysis / tests)
- Any skipped command includes reason + reproducible procedure.

## 1b) Structural exit check (required, all risks)

- `python scripts/check_structure.py <touched source files>` was run and the result is recorded.
- Every finding (`source-file-lines`, `entrypoint-logic-lines`, `inline-test-lines`) is resolved by an applied split in this submission, or carries an explicit bounded waiver in the change brief (for example generated code).
- Entrypoint files (`main.rs`, `src/bin/*.rs`, `main.py`, `__main__.py`, `main.go`, `main.c/cc/cpp`) contain wiring only; behavior tests are not accumulated in entrypoints.
- This check does not depend on triggered branches. An unresolved finding without a waiver is `no-submit`.
- If a `.agents/structure-baseline.json` (or `--baseline PATH`) applies: any `baseline_errors` entry (`regression`, `stale-baseline`, `duplicate-entry`, `missing-path`, `threshold-mismatch`, `unknown-rule`, `malformed-schema`, `path-escape`) is `no-submit`, same as an unbaselined finding. `accepted_debt` alone does not block, but the recorded result must state it as accepted debt, not as `pass`/clean. A baseline is a ratchet: it may only be authored or tightened by maintainers to reflect exact current values, never auto-generated, and never left recording a looser value than the file's current state. A baseline entry's `path` must be repo-root-relative and confined to the repo root: an absolute path, a `..` traversal segment, or any symlink in the path chain is a `path-escape`, not accepted debt. `duplicate-entry`, `missing-path`, `threshold-mismatch`, `malformed-schema`, `unknown-rule`, and `path-escape` are baseline-document defects evaluated against every entry regardless of scan scope, so they are `no-submit` on quality-gate's touched-files run exactly as on a full scan — they are never left neutral just because the entry's file was not among the touched files. Only a schema-valid, path-valid, canonical-limit-valid entry whose file is not among the touched files this run is left neutral for the separate "does it still breach the rule" (`stale-baseline`) question — it neither blocks nor counts as accepted debt on that run, and stays a maintainer-owned refresh/removal responsibility, caught deterministically the next time a scan that includes it (e.g. CI's full default scan) runs.

## 2) Triggered-branch evidence (required when triggered)

Confirm required evidence exists for each triggered branch:

- bugfix branch → Bug Report (repro/evidence/Five Whys/verification/prevention)
- UI branch → UI Visual Verification Report + artifact paths
- concurrency branch → concurrency verification evidence (plan/shutdown-verification/logging)
- architecture-decision-analysis branch → Architecture Decision Analysis Record with decision/no-decision, quality drivers, option tradeoffs, verification tasks, and handoffs
- observability branch → Observability Plan with logs/metrics/traces evidence plus signal purpose, actionability, counter-metric where relevant, and artifact paths
- implementation-economy branch → Complexity Budget plus Post-Implementation Economy Audit, including keep/delete/inline/merge decisions for new abstractions
- design-balance branch → Responsibility Map with unit, name, responsibility sentence, reason to change, and dependency direction
- performance-review branch → Performance Review with hot path, data scale, complexity, I/O/query count, decision, evidence, and no-measurement/no-claim limits when measurement is missing
- Agent-facing workflow contract branch → `reports/workflow-contract-review/<slug>.md` with decision `submit`, workflow surfaces reviewed, source-of-truth chain, generated argv replay, producer/consumer consistency, runtime discovery assumptions, forbidden fallback checks, claim boundaries, and resolved or explicitly accepted findings
- delegated/subagent/worker execution changed files → `.agents/runs/agent-runs.jsonl` contains an explicitly cited `agent_run` record for this delegated run; `python3 scripts/judge_agent_run.py --run-id <run_id> --require-accepted` passes or the same fields are manually verified from the cited record
- feature-level embedded NFR branch → `reports/resource/nfr-gate-report.md` with decision, runtime mode classification, artifact check, budget results, claims review, and unknowns/limits
- embedded system familiarization branch → `docs/targets/<target>/system-familiarization.md` with required/created/missing/provisional/deferred artifacts, artifact freshness/revisit conditions, controlled conditions, uncontrolled confounders, operating point coverage, claim-to-evidence traces with allowed wording, claims blocked by missing evidence, and handoff statuses (`not_needed|required_pending|completed|deferred_with_reason|blocked`)
- hardware operating point claim → `docs/targets/<target>/controlled-operating-points.md` with controlled factors, observed covariates, uncontrolled confounders, coverage status, confidence, safety preconditions, control/verification/abort/restore methods, and allowed wording
- hardware capability architecture claim → `docs/targets/<target>/hardware-control-surface-map.md`, `docs/targets/<target>/hardware-capability-map.md`, or `docs/targets/<target>/capability-cost-model.md` showing control surface status and cost model status
- embedded target characterization branch → `docs/targets/<target>/target-characterization.md`, `target_profiles/<target>.yaml`, baseline paths, and characterization report when production claims depend on target behavior
- embedded operating envelope branch → `docs/targets/<target>/operating-envelope.md` and scenario reports for normal, degraded, boundary, observer, recovery, or blackout behavior
- embedded NFR calibration branch → `reports/nfr-calibration/<feature>.md` plus budget provenance when numeric production budgets are claimed
- constitution-only embedded branch → constitution artifacts such as project principles, resource discipline, physical budgets, target profiles, resource harness skeleton, and PR-template section. A feature-level NFR gate report is required only when runtime changes or production-readiness claims are introduced; constitution artifacts alone satisfy this branch otherwise.
- project-structure branch → layout decisions (file → role) plus structure budget result (pass, or findings with applied fixes/waivers)
- staged-lowering branch → staged plan + per-pass verification log
- legacy branch → characterization/safety-net evidence + seam/refactor notes
- structural scan branch → smells/anti-patterns result (new/worsened handled)
- function-boundary-governor branch → function-boundary decision record
- destructive-refactor branch → convergence record (replaced|no-op|rollback), migrated call-sites evidence, red-state usage record
- refactor branch under compat-mode `break-allowed` → removed-symbol sweep output: `python scripts/check_api_removal.py --symbol <old-name> ...` with zero hits (tool output, not a claim); surviving old symbols/shims/aliases are `no-submit`
- API-touching or rework/consolidation/deletion task → recorded compat-mode (`preserve|staged|break-allowed`; `break-allowed` quotes the requester's waiver)
- function-design ledger-needed cases → ledger entry present (replaced abstraction / intentional duplication / staged adapter)
- C++ header branch → Doxygen completeness evidence
- ExecPlan required case → `plans/<slug>.md` is current (WBS/decisions/surprises/handoff)
- delegated run evidence case → explicit run ID, matching changed files, validation command results, and accepted judgment
## 3) Minimum exit criteria review (always)

- Path-specific instructions were identified and followed.
- Requirements/acceptance changes (if any) are reflected in docs/tests.
- Default-lane evidence is present for normal/high-risk work, or the low-risk skip reason is explicit.
- Agent-facing workflow, generated instruction, collect plan, executable handoff, multi-step CLI workflow, or cross-host workflow changes are blocked unless the Workflow Contract Review Report decision is `submit`.
- Delegated/subagent/worker changes are blocked unless the submission cites fresh run evidence by explicit run identity. Do not accept `latest`, newest file, mtime, raw co-presence, or agent self-assessment as evidence.
- Delegated run evidence is `no-submit` when the ledger record is missing, the run ID is not explicit, required validation did not run, validation failed, validation output is missing, changed files exceed allowed files, or `judge_agent_run.py --require-accepted` fails.
- Missing token telemetry alone never blocks: treat absent telemetry or `telemetry.status: not_collected` as acceptable when every other run-evidence criterion passes.
- Completion claims require verification evidence. A worker report that says the task is done without validation command results remains `no-submit`.
- If `requirements-engineering` declared measurable quality/NFR targets (metric + target + measurement method), each target records a measured value vs. the target, or an explicit `not-measured`/`unmet` entry with reason; silently unmeasured or unmet declared targets are `no-submit`.
- Non-embedded performance/reliability claims (fast, low-latency, scalable, high-throughput, reliable, production-ready) are blocked without measurement evidence (command + result) or an explicit `provisional`/`not-measured` limit — the same no-measurement-no-claim rule embedded work already follows.
- If embedded NFR work was triggered, no low-overhead, battery-safe, lightweight, flash-safe, thermally-safe, or production-ready claim remains without measurement evidence or explicit experimental-only limits.
- If architecture, hardware, or embedded NFR claims depend on a hardware operating point, `controlled-operating-points.md` exists and the claim trace shows controlled evidence, adequate coverage, confidence, and allowed wording.
- Observed natural variation under a dynamic policy is not accepted as a controlled sweep. Claims such as "works at all CPU clocks", "low overhead across frequency range", "battery safe", and "GPU offload is better" are blocked unless the corresponding controlled experiments and cost models exist or the wording is explicitly limited/provisional.
- If a GPU/NPU/DSP/accelerator claim supports architecture selection, hardware presence alone is insufficient; the control surface, API/runtime path, transfer/setup/scheduling cost, workload fit, power/thermal cost, benchmark evidence, and fallback implications are known or the claim is blocked/provisional.
- If embedded NFR claims depend on target behavior, target characterization exists or the claim is explicitly provisional.
- If numeric production budgets are claimed, budget provenance exists, calibration artifacts are referenced, and calibration revisit conditions are not triggered.
- If feature-level embedded NFR work was triggered, target-local background behavior is classified as default, burst, experimental-only, or debug-only.
- If compat-mode was `break-allowed`, no deprecated shim, re-export alias, or parallel old/new version survives — verified by the `scripts/check_api_removal.py` sweep, not by the agent's claim.
- Open risks or follow-ups are explicitly documented.

If deeper judgment is needed, invoke dedicated skills rather than expanding this checklist:
- readability → `$code-readability`
- maintainability/modularity/boundaries → `$code-smells-and-antipatterns`
- error handling → `$error-handling`
- concurrency details → `$concurrency-core`, `$thread-safety-tooling`
- observability details → `$observability`
- Agent-facing workflow contract details → `$agent-workflow-contract-review`

## 4) Gate decision format (required)

```markdown
Gate decision: submit|no-submit

Findings:
- [ID] location — failed/missing criterion — required fix

Checks run:
- <command> — pass|fail|skipped (reason)

Live discovery:
- <external/tool surface> — source/version/status/config/artifact evidence or not applicable

Triggered branch evidence:
- <branch> — present|missing — artifact/path
```

Rule: `submit` only when all required criteria are satisfied and findings are 0.


- Verify ledger by checking canonical path `.agents/design-ledger/function-boundaries.md`, not only final-response text.
- Verify delegated run evidence by checking `.agents/runs/agent-runs.jsonl` with an explicit run ID, not latest/newest record selection.
- Verify embedded NFR evidence by checking `reports/resource/nfr-gate-report.md`, not only final-response text.
- Verify controlled operating point evidence by checking the target pack artifact paths, not only final-response text.

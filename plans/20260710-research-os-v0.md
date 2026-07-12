# Research OS v0 — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Add a research epistemic mode to the playbook so exploratory R&D (SoC NPU/GPU model optimization, multi-task model research, VLM→VLA work) runs at probe speed without inheriting delivery-grade process, while evidence discipline gets STRONGER, not weaker.
- Design lineage: owner problem statement → external proposal (nGPT-5.6) → supervisor meta-review (8 corrections) → corrected v0 → 4-agent verification workflow (integration fact-checks + adversarial attack, 14 holes + clamps). Core principle: **one substrate, two epistemic policies, orthogonal safety overlay** — and after the adversarial pass: *never root integrity in records the agent writes about itself*. v0 delivers this as tamper-EVIDENCE for honest-but-buggy flows: the runner is the sole writer and the chain detects accidental or careless mutation. An agent with write access to the scripts and ledger can still forge a self-consistent chain — adversarial-grade anchoring (externally published chain head, protected writer) is an explicit follow-up, not a v0 property.

## Scope

### In scope (v0)
- **Runner as the integrity root** (`scripts/research_run.py`): sole writer of research records into the existing run ledger (`.agents/runs/agent-runs.jsonl`, new record types, hash-chained over the research subsequence); runner-stamped timestamps; machine-evaluable disconfirm predicates ({metric, comparator, threshold} → supported|disconfirmed|not-evaluable); exploration logging + rerun-laundering disclosure (exploration_multiplicity, digest-collapsed n); structured claims with template-generated prose (`render-claims`).
- **Mechanical gate** (`scripts/check_research_evidence.py`): chain integrity, preregistration-before-execution, predicate/outcome recomputation, claim binding (mode-independent), claims-view freshness, R5 boundary check with default-deny path modes + symlink rejection + safety_paths flagging. Wired into make lint / CI (deliberate convention exception: research integrity needs CI-side checks because the adversary is the acting agent).
- **Mode wiring**: `.agents/project-policy.yml` (explicit declaration > path_modes > default_mode; unmatched paths = delivery); ALL SIX unconditional-mandate locations made mode-conditional; policy structure waivers consumed by check_structure.py; 3 research task classes.
- **3 skills**: research-workflow (router, 4-line frame, ordinal probe-selection tree), experiment-loop (3-input evidence contract), research-synthesis (continue|pivot|kill|promote, promotion boundary). Trigger evals.
- Fixtures B–F + chain/wiring tests as unit tests; live blind validation run (research-mode worker on a fixture question) judged by supervisor.

### Out of scope / non-goals (deferred until telemetry demands)
Domain research skills; hypothesis state machines; baseline-ladder mandates; priority scoring; full input-closure digests / env fingerprints; import-graph promotion checks; claim-lint over all prose (promotion docs only, later); PoC as a distinct mode; fixture A full A/B benchmark (baseline measured post-merge in real use).

## Decision log

- 2026-07-10: Hash chain covers only the research-record subsequence; agent_run records interleave unchained — preserves one-file substrate without modifying agent_run.py.
- 2026-07-10: Evidence rules attach to claims, not modes (kills the declare-delivery-in-experiments/ bypass). Waived in research mode: code-quality gates for probe paths. Never waived: evidence discipline, safety, secrets, destructive-op controls.
- 2026-07-10: Disconfirm predicates are machine-evaluable data; claim prose is generated from n-keyed templates (free-text claim wording banned) — "ledger is the source of truth, prose is a view".
- 2026-07-10: Default-deny path modes; missing policy file is a hard error for the boundary check.
- 2026-07-10: Team: Opus worker built the integrity core; Sonnet workers authored skills and mode wiring from fixed contracts; supervisor (architect) reviewed diffs, integrated, and judged the live validation.

## Progress (WBS)

- [x] (P0) Runner + validator + fixture tests (Opus worker; run 20260712T045229Z-...-61aa6c48) — 21 tests
- [x] (P0) 3 skills + trigger evals (Sonnet worker; run 20260712T044900Z-...-2a21efab) — 54 skills, 194 eval cases
- [x] (P0) Mode conditionalization ×6 + policy file + structure-waiver wiring + task classes (Sonnet worker; run 20260712T044653Z-...-5d7fa694)
- [x] (P1) Supervisor integration — index/manifests/symlinks/lockfile regenerated (research_probe/exploration→claude-sonnet-5, research_synthesis→claude-opus-4-8); make verify green
- [x] (P2) Live blind validation — see Outcomes
- [ ] (P3) Fixture A pre-merge time-to-first-probe run, added as part of the review response (no longer deferred to post-merge) — results (honest, mixed): same hidden-cause task (planted O(n^2) list-membership with a string-concat decoy that CPython optimizes away), same model, two blind runs differing only in declared mode. Correctness: BOTH modes identified the planted cause by single-variable measurement (77% vs 76.4% recovery) — neither took the decoy. Speed: NOT supported at n=1 — delivery reached its first probe in 3 commands vs research's 11 (first-use learning of the research machinery dominated; the task was also small enough that delivery routed through its lean bug-RCA lane, never triggering the heavy paths the mode exists to avoid). Cost: research +~15% (36 vs 30 tool uses; 94K vs 82K tokens). Integrity: research produced a machine-verifiable chain (E-0004 -> C-0002, gate-checked) vs a prose report; the semantic claim binding REJECTED a real mis-claim (metric mismatch) live, and a mis-registered predicate (E-0003) was honestly retained append-only. Confound disclosed: the fixture's git commit message leaked the intended cause; the research worker noticed it post-ablation, disclosed it, and did not use it as evidence. Verdict: merge on demonstrated integrity value; the speed claim stays provisional per the system's own n=1 wording rules — re-measure on a multi-experiment exploration task where delivery mode's ExecPlan/architecture mandates actually fire
- [x] (P3) PR

## Surprises & Discoveries

- 2026-07-12: The blind validation worker, given ONLY the research question + declared mode, traversed AGENTS.md → research-workflow → experiment-loop unaided and completed the full evidence loop (4-line frame, explore-then-register, predicate, runner-verified `supported`, structured claim, manual multiplicity disclosure, n=1-limited wording) — the skill chain is executable without runner documentation in the brief.
- 2026-07-12: The same run found a real defect: `command_digest` hashed all dirty tracked files including the ledger itself, so `register`'s own append self-invalidated `execute` on the canonical ledger. The worker did not patch out-of-scope code — it used the runner's `--ledger` override, disclosed the workaround, and escalated. Fixed by an Opus worker (run 20260712T050939Z-...-cddbc1d0): recording medium + runner outputs excluded from digest inputs in the shared module, regression test with a negative control. Live canonical-ledger smoke (E-0002→C-0001) confirms.
- 2026-07-12: `playbook-explorer` contains no dev-workflow mandate sentence — the "six locations" were five plus one correctly-reported non-application.

- 2026-07-12 (review round 3): remaining semantic bypasses closed — non-finite thresholds refused; claim effect preregistered and inherited (free-text removed); `no-effect` requires equivalence-flagged supported evidence (the "all disconfirmed" rule was wrong and is deleted); variation axes are command-template-bound (n>1 only when evidence commands are identical after axis-token substitution); acknowledgments bind to ledger evidence (claim IDs must resolve; `Delivery-run:` records must exist, have passed validation, and their changed/allowed union must contain every promoted path). The supervisor now records an integration run like any worker — the gate closed only after run `20260712T165226Z-focused_code_change-19e96118` was recorded and cited.
- Follow-up authorized for the next feature: split `check_research_evidence.py` into ledger-check and boundary-gate modules — all three scripts sit at the 400-line ceiling after three fix rounds; the structure budget is doing its job and the split should land before any further growth.

## Handoff (update at every stop)

- Current branch: `research-os-v0` (worktree)

## Validation & Acceptance

- AC1: make verify green including the new ledger gate; unit tests cover fixtures B–F + chain tampering + wiring.
- AC2: live research-mode run produces a chained preregistration→result→claim trail that check_research_evidence.py accepts, with zero unsupported empirical claims in the report.
- AC3: delivery mode behavior unchanged (existing evals/validators green; default_mode delivery).

## Outcomes & Retrospective (fill when done)

- What shipped / merged: Research OS v0 — runner (`research_run.py` + shared `research_ledger.py`), gate (`check_research_evidence.py`, in lint/CI), 3 skills, mode policy + 6-location conditionalization, structure-waiver wiring, 3 research task classes, fixtures B–F as 22 unit tests, worked example under `experiments/sort-degradation-probe/`.
- AC1 ✅ make verify green incl. the new ledger gate. AC2 ✅ blind research-mode run produced a chained, validator-accepted evidence trail with zero unsupported empirical claims (quicksort degradation confirmed ~1390x vs 20x threshold, runner outcome `supported`). AC3 ✅ delivery mode unchanged (default_mode delivery; all existing validators/evals green).
- What went well: three parallel workers (1 Opus, 2 Sonnet) with disjoint scopes, zero collisions; the blind run doubled as a bug-finding fixture — the Research OS caught its own first integrity defect before merge.
- What went wrong: the digest self-invalidation defect (fixed pre-merge, regression-tested); two workers repeated the known `--changed-from-git` sweep pitfall in shared worktrees (both self-corrected per contract) — consider a worker-brief note or tool fix later.
- Follow-ups / tech debt tickets: promotion-path claim-lint over decision surfaces; multiplicity tracking across `--ledger` overrides; `agent_run.py --changed-from-git` shared-worktree ergonomics; external chain-head anchoring (CI-published or signed) for adversarial-grade integrity. Fixture A (time-to-first-probe A/B benchmark) is no longer deferred to post-merge — it is being run pre-merge as part of this review response — results (honest, mixed): same hidden-cause task (planted O(n^2) list-membership with a string-concat decoy that CPython optimizes away), same model, two blind runs differing only in declared mode. Correctness: BOTH modes identified the planted cause by single-variable measurement (77% vs 76.4% recovery) — neither took the decoy. Speed: NOT supported at n=1 — delivery reached its first probe in 3 commands vs research's 11 (first-use learning of the research machinery dominated; the task was also small enough that delivery routed through its lean bug-RCA lane, never triggering the heavy paths the mode exists to avoid). Cost: research +~15% (36 vs 30 tool uses; 94K vs 82K tokens). Integrity: research produced a machine-verifiable chain (E-0004 -> C-0002, gate-checked) vs a prose report; the semantic claim binding REJECTED a real mis-claim (metric mismatch) live, and a mis-registered predicate (E-0003) was honestly retained append-only. Confound disclosed: the fixture's git commit message leaked the intended cause; the research worker noticed it post-ablation, disclosed it, and did not use it as evidence. Verdict: merge on demonstrated integrity value; the speed claim stays provisional per the system's own n=1 wording rules — re-measure on a multi-experiment exploration task where delivery mode's ExecPlan/architecture mandates actually fire.

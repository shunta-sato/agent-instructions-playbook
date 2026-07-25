# Lint migration (Wave 0) — design record

Owner: supervisor (architect). Trigger: external review "move machine-checkable
rules from SKILLs into lint"; supervisor verified its load-bearing claims (all
confirmed except one already fixed in #100) and adopted with modifications
recorded in the session. Core thesis adopted: **SKILLs own judgment (when/why/
what to decide); lint owns acceptability (may this be accepted).** Closure rule
adopted: a machine-checkable failure is not closed by a SKILL/wiki note alone —
it needs a corresponding lint or harness check.

## Wave 0 scope (automate existing rules; no new rule content)

- **L1 — structure lint automation**: `check_structure.py` gains
  `--working-tree` and `--diff-range A..B` modes; wired into the Makefile
  (`lint-diff`) and CI (order-asserted). The dev-workflow/quality-gate reference
  lines that told agents to enumerate touched files now just say "run the
  repository structure lint" — the enumeration judgment moves to the tool.
- **L2 — instruction-graph lint**: new `scripts/lint_instruction_graph.py`
  verifying, across all SKILL bodies and their required references:
  `$skill-name` references resolve to existing skills; relative file references
  exist; `§`-anchor references resolve to a real heading in the target file;
  `metadata.commands` entries are executable files. Pre-existing violations in
  dev-workflow/quality-gate are baselined (ratchet), not silently fixed.
- **L3 — warning ratchet + command-doc drift**: `report_skill_inventory.py
  --check` fails on warnings NOT present in a committed baseline (same ratchet
  pattern as the context-budget caps); quality-bar minimums enforced by
  visibility class (default: ≥2 positive / ≥3 negative trigger cases for
  broad/core; explicit-only: ≥1/≥2; template: exempt) with the current shortfall
  baselined. New `scripts/lint_command_docs.py` verifies README's Validation
  section names every validator that `make lint` actually runs (drift found at
  adoption time: README listed 3, make lint ran 8+).

## Deferred to later waves

Wave 1: artifact registry + per-artifact lints (UI packs with symlink-escape
checks, ExecPlan, Bug Report, Workflow Contract, embedded NFR pack).
Wave 2: `submission_evidence` ledger record + `lint_submission.py` +
quality-gate reduction to residual semantic judgment.
Wave 3: project lint adapter CONTRACT only (schema in project policy); no
speculative tool matrix — telemetry-gated.
Not lintable (stays SKILL/eval): risk/intent/mode choice, root-cause validity,
architecture trade-offs, abstraction worth, comment-meaning judgments,
retrospective generalization.

## Model note

Supervision/review roles use Opus 5 per the user's direction (2026-07-25).
Agent-harness calls use the `opus` alias (resolved by the harness to the newest
Opus). The model catalog gains a `claude-opus-5` entry with
`smoke_eval: pending` — per the catalog's evidence discipline (PR #88), routing
aliases move only after a recorded supervised run passes on the new model; the
exact model ID awaits `/v1/models` verification (`ant models list`).

## Wave-0 execution notes

- The automated structure lint earned its keep on first contact: the initial
  `--working-tree` run flagged two real over-budget files that per-touched-file
  invocation had never seen (report_skill_inventory.py at 811 lines,
  test_research_os_gate.py at 441). Per the closure rule they were SPLIT, not
  waived (L4, refactor intent, behavior-locked: byte-identical CLI JSON, 283
  tests moved-not-modified; the worker escalated the arithmetic impossibility of
  a 2-file split and the supervisor authorized the third module).
- The command-doc drift lint likewise fired mid-wave on drift the wave itself
  created (L2 wired a new validator after L3 had synced the README) — resolved
  at integration; both events are the migration working as designed.
- Routing re-measurement SKIPPED for this wave, with rationale: the discovery
  surface delta is command-invocation wording inside two required references
  plus one cross-skill path fix; no trigger row, description, or routing table
  changed. The next routine campaign covers it; if its recall moves, revisit.
- Quality-bar shortfall table (24 default-visibility skills) is baselined and
  becomes the backlog for eval-coverage work; new skills must meet the bar.

## Handoff

- 2026-07-25: Wave 0 started on branch `lint-migration-w0` (based on main
  b26433c). Workers: L1 structure modes, L2 instruction graph, L3 ratchet+drift
  (parallel, disjoint files); supervisor: catalog entry, integration, Opus
  adversarial review, routing-eval regression check if discovery surface moved.
- 2026-07-26: Opus adversarial review verdict: integrate-after-fixes. Findings
  and dispositions (all applied by the supervisor):
  - F1 (should-fix): quality-bar ratchet compared class-level ids, so a skill
    could LOSE eval cases without tripping the ratchet as long as it stayed in
    the same shortfall class. Fixed: ids now carry the count
    (`quality-bar:negative-shortfall@N`) and the ratchet uses ordered coverage
    (a baselined entry covers equal-or-better counts only); regression tests
    added; baseline regenerated (29 skills / 39 ids, same totals).
  - F2 (should-fix): command-doc drift lint missed the third direction — a
    README Validation entry whose script exists but that no make target runs.
    Fixed: `find_drift` returns it as `unwired_readme`; test added.
  - F5 (should-fix, most important): the two new lints were wired into
    `make lint` but NOT into CI, so CI would accept a PR that broke either.
    Fixed: two workflow steps added before unit tests; `test_ci_wiring.py`
    pins presence + before-tests order for both.
  - F4 (note): `to_repo_relative` existed in three modules after the L4 split.
    Deduped: `skill_inventory_checks` owns it; the other two import it.
  - F3 (note, deferred): latent instruction-graph matcher gaps (anchor forms
    not yet used in the corpus). Deferred until a real usage appears; the
    lint fails closed on new unresolvable forms, so the gap is visible.
  After fixes: 288 tests OK; all lints, `check_structure.py --working-tree`,
  context budget, and `make verify` green.

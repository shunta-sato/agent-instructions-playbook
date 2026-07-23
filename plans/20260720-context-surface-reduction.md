# Context-surface reduction (WS-A) — design record

Owner: supervisor (architect). Trigger: external GPT-5.6-oriented review of the
runtime instruction surface; supervisor verified its load-bearing claims against the
repo before adoption (all confirmed: recursive all-file `requires`; the
code-smells selective-load contradiction; ~611-line common path; schema-only
trigger-eval validator; weak style gates).

## Adopted / modified / deferred

- **A1 (adopted)** — split the load contract into three tiers:
  `metadata.requires` (0–2 files, always load before executing),
  `metadata.resources` (load when the SKILL.md names its condition),
  `metadata.commands` (execute or reference by path; never inline into context),
  `metadata.templates` (open only when producing the output artifact).
  Survey at adoption time: 17 skills carried ≥3 always-load files
  (tonemana-catalog 25, uidesign-flow 20, uiux-flow-preview 11,
  preflight-engineering 10, embedded-system-familiarization 9).
  The selection rule must be an explicit condition in SKILL.md ("open X when Y"),
  not reader judgment — that keeps it Sonnet-executable and keeps PR #82's original
  fix (workers skipping needed files) intact for the core contract.
- **A2 (adopted)** — single-source `dev-workflow` and `quality-gate`: SKILL.md becomes
  a short router; every table/threshold/branch list lives exactly once in the
  required reference. The repo already produced a triple-copy drift (coverage
  ceilings, fixed 2026-07-20) — internal evidence, not just external advice.
- **A3 (adopted, narrowed)** — `metadata.visibility: default | explicit-only |
  template` filters the generated AGENTS.md index (explicit-only/template skills get
  a one-line name-only group, not full description rows). The index itself stays —
  it was added on eval evidence (passive index improves routing). Claude symlinks
  are unchanged in v1. Full pack hierarchy: deferred to WS-C with eval evidence.
- **A4 (adopted)** — `scripts/check_context_budget.py`: mechanical budgets for the
  common path (AGENTS.md + dev-workflow + quality-gate SKILL+required refs) and for
  per-skill `requires` counts; wired into make verify.
- **Deferred to WS-B** — model-in-loop A/B eval harness over the 212 seed cases
  (routing precision, co-fire count, tokens, task success), covering GPT-class
  targets alongside Sonnet.
- **Deferred to WS-C (gated on WS-B measurements)** — trigger narrowing to
  decision-diffs; comment-discipline compression to an always-on rule +
  explicit-only skill; refactor/hardening lane folding into dev-workflow references.
- **Rejected** — importing the external 41–66% token-cut figures as expectations;
  deleting the AGENTS.md index outright; removing comment-discipline.

## Invariants for WS-A (semantic-preserving)

No rule is added, removed, or reworded beyond deduplication and placement; every
rule that existed before exists after, exactly once; validators stay fail-closed
(a listed file that cannot be read is still an error; every bundled file must be
listed in exactly one tier). Regression: full validator suite + a blind routing
spot-check after A2.

## Wave-4 evidence (blind routing probe)

A read-only probe traced four task shapes (normal feature+tests, PoC construction,
payment-module hardening, structural review) through the migrated contract without
being told any skill names. All four routed correctly; conditional resources loaded
exactly when their stated conditions matched (unit-test-operations for a mock/fake
decision; architecture-boundary/coupling references for an adapter diff) and stayed
unloaded otherwise (language-specific references with no language stated; the PoC
OFF list held). Three ambiguities surfaced and were adjudicated:
- research-workflow's `optional/research-framing.md` sat outside the four-tier
  contract and was unreachable from metadata — moved to `references/` and declared
  as a resource (condition already in the body). FIXED.
- code-smells' `finding-template.md` is declared a resource though its role is an
  output template; its stated condition ("for the expected review shape") makes the
  load behavior identical to the templates tier — intentional, no change.
- The `preflight-*` family is not reachable from AGENTS.md or dev-workflow's
  trigger list (pre-existing, not introduced by WS-A) — WS-C watchlist: either a
  dev-workflow trigger row or explicit-only visibility with a documented entry
  point.

## Wave-4 evidence (Opus adversarial review) and adjudication

Verdict: integrate-after-fixes. The binding invariant HELD — the reviewer
independently verified >12 load-bearing rules (and the reverse direction) against
the HEAD originals: no rule, exception, or qualifier dropped; the 12 gap-fills
faithful; index/visibility regression clean.

- **3.1 (adjudicated: accept with rationale, recorded here — not silent)**: the
  reviewer correctly called out that unit-test-design's reach-budget pass came from
  re-tiering `unit-test-operations.md` (233 lines) to resources, which the
  requires-only reach rule does not count, while mock-vs-fake — a headline trigger —
  lives in that file. Rationale for accepting: the PRIMARY flow (derive cases for a
  change: tier, partitions, boundaries, stop criteria, checklist) is fully served by
  the required case-design file; the operations conditions are stated in the body and
  the tier fired correctly in the order-billing blind run (doubles guidance loaded
  when a fake was needed). The gate's docstring now states explicitly that
  reach-budget bounds the unconditional load only. WS-C item: trim
  unit-test-operations.md so the split stops being load-bearing.
- **2.1 (fixed)**: `update_skill_requires --check` now errors on any `resources`
  entry whose basename never appears in the SKILL.md body — a condition-less
  resource can silently never load (the inversion of the failure PR #82 fixed).
  The lint immediately caught a real instance: visual-regression-testing's three
  platform references were named only generically; the body now names each file
  with its platform condition.
- **5.1 (fixed)**: an unmigrated skill owning `scripts/` or `templates/` files is
  now refused by `--check` (previously the legacy path silently dumped them into
  `requires`, i.e. always-load an executable as prompt context).
- Notes recorded: ratchet caps are fixed ceilings, not monotonic ratchets
  (docstring corrected); tier/visibility vocabulary lives in three hand-synced
  copies (WS-C consolidation candidate); the compat-trigger wording merge kept the
  narrower pre-existing phrasing ("explicitly waived") — immaterial because §0b
  independently forces compat-mode recording for all API-touching work.

## WS-B v1 result (2026-07-23)

`scripts/run_routing_eval.py` (build/grade/report; runner-agnostic packs; the
no-expectation-leak property is test-enforced) executed over the full 212-case
corpus on both sides of WS-A with 24 isolated Sonnet subjects. Result: surface
77.5k → 65.7k chars (−15%); should-trigger recall 86.0% → 82.9%; should-not-trigger
compliance 98.9% → 98.3%; mean co-fire 3.29 → 3.14. The recall cost concentrates
in embedded-NFR chain skills. Full data + supervisor reading:
`evals/routing-runs/20260723-*`. WS-C is now measurement-gated as intended:
embedded-chain discoverability first; no trigger narrowing in that family until
repaired; single-run caveat recorded honestly.

## WS-C1 result (2026-07-23)

Chain-composition cues + preflight reachability row (worker run a7eca010, surfacing
only what the embedded skills' own text states; no eval expectation touched).
Full-corpus re-measurement: recall 82.9% → 87.0% (above the 86.0% pre-WS-A
baseline), compliance unchanged 98.3%, surface +1.2k chars (net −14% vs pre-WS-A),
embedded misses 24 → 17. The measure→repair→re-measure loop closed in one day.
Next repair candidate from the data: destructive-refactor misses (6, stable across
variants). Remaining WS-C items unchanged and still measurement-gated.

## Handoff

- 2026-07-20: WS-A started on branch `context-surface-a` (based on
  `intent-workflows`; merges after #97). Wave 1 = schema/contract
  (update_skill_requires.py, validate_skills.py, generate_agent_index.py,
  AGENTS.md, CLAUDE.md); wave 2 = 58-skill frontmatter migration ∥ core-skill
  single-sourcing; wave 3 = budget gate; wave 4 = Opus adversarial review +
  blind routing spot-check.

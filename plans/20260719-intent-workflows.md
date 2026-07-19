# Intent workflows — purpose-routed development (design record)

Owner: supervisor (architect). Status: v1 implementation.
Workers: Sonnet authoring under briefs; Opus adversarial design review before integration.

## Problem

`dev-workflow` routes every delivery-mode change toward product quality, now including
`unit-test-design` depth. Three purposes fit badly:
- **PoC construction**: product-grade gates are over-quality; but an ungoverned escape
  hatch invites PoC code laundering into production.
- **Refactoring-purpose tasks**: the parts exist (compat-mode, `function-boundary-governor`,
  `design-balance`, `destructive-refactor`, prep-refactor 2b) but no lane sequences
  behavior-lock → structural change → equivalence evidence, and feature-oriented branches
  (requirements, new-test depth) mis-fire.
- **Quality-improvement (hardening) tasks**: no entry point says "measure first, tier the
  targets, work highest-risk-first, stop at the policy ceiling" — the failure mode is
  gold-plating (uniform coverage pushes the unit-test policy explicitly forbids).

## Decision: a third axis, not new universes

Existing axes: **mode** (research | delivery — who judges truth, from the Research OS) and
**risk** (low | normal | high — verification depth). We add **intent** — what the work
optimizes — as a declaration in `dev-workflow` step 1a:

| intent | mode | route |
| --- | --- | --- |
| `feature` (default) | delivery | dev-workflow unchanged |
| `poc` | research | exit to `$poc-workflow` on the research-mode substrate |
| `refactor` | delivery | `$refactor-workflow` lane, then back into dev-workflow gates |
| `hardening` | delivery | `$hardening-workflow` lane, then back into dev-workflow gates |

Rationale for each load-bearing choice:

1. **PoC runs on the research substrate, not a fourth mode.** `research-workflow`'s
   description already claims "feasibility probes, proof-of-concept work". Research mode
   already gives exactly what a PoC needs: delivery mandates (ExecPlan, observability,
   full quality-gate) are mode-conditional and switch off; the mechanical boundary gate
   (`check_research_evidence`) fail-closes promotion of research-mode paths into delivery
   paths with digest-bound, evidence-bound acknowledgments — 8 review rounds hardened
   that gate; PoC laundering is the same attack as research laundering and is already
   blocked. `poc-workflow` adds only the missing routing for *construction* activity
   (experiment-loop covers evidence probes, not "build a demo app").
2. **Intent modulates composition; risk still scales depth.** Orthogonal: a refactor of
   the auth module is `refactor` intent at `high` risk. Intent picks which part-skills
   run and what evidence closes the task; risk picks planning/verification depth.
3. **Gates are profiled, never loosened silently.** PoC freedom comes from a *declared*
   mode with a mechanical promotion boundary, not from skipping gates in delivery mode.
   Refactor/hardening keep quality-gate with intent-conditional evidence bullets.
4. **Stop criteria for hardening reuse the unit-test policy.** Changed-code 90/80/90,
   overall 75% guide, "do not push normal areas to 95/100%" — hardening inherits these
   as its ceiling, so quality-improvement cannot become gold-plating.

## New skills (thin composition layers; parts already exist)

- `poc-workflow`: declare boundary (research-mode path or declared mode) + the question
  the PoC answers + exit criteria up front; rigor floor (runs + smoke check + safety
  overlay always on: secrets, destructive ops, physical safety); explicitly OFF:
  unit-test-design depth, TDD, observability plans, implementation-economy budgets,
  NFR gates; exits = discard | promote (promotion re-enters dev-workflow as `feature`
  on the promoted diff — full unit-test-design tiers, observability, structure — and
  passes the mechanical boundary gate) | convert observations into citable evidence via
  `$experiment-loop`.
- `refactor-workflow`: 0) compat-mode + intent record; 1) behavior lock (suite green
  baseline; `$working-with-legacy-code` characterization when tests are unreliable);
  2) structural change via parts (`$function-boundary-governor` /`$design-balance` /
  `$destructive-refactor` / `$project-structure`, prep-refactor semantics); 3) equivalence
  evidence: tests unchanged-and-green (or characterization-first), no new behavior,
  API-removal sweep under `break-allowed`; 4) quality-gate refactor profile.
- `hardening-workflow`: 0) declare target quality dimension + metric; 1) measure baseline
  (structure report, coverage, flaky list, smell sweep); 2) tier targets with
  `$unit-test-design` E/S/H; 3) execute highest-risk-first via parts (unit-test-design,
  `$observability`, `$project-structure`, `$code-smells-and-antipatterns`,
  `$performance-review`; extract-to-test steps route through refactor parts);
  4) evidence: before/after metric delta + behavior preservation; 5) stop at the policy
  ceiling; quality-gate hardening profile.

## Wiring

- `dev-workflow` 1a: intent declaration + 4-row routing table (above); recorded like
  compat-mode.
- `quality-gate`: two conditional bullets (refactor evidence, hardening evidence).
- `research-workflow`: one routing line (PoC construction → `$poc-workflow`).
- `.agents/project-policy.yml`: `poc/` → research path-mode entry as the executable
  default for this pattern.
- Trigger evals for the three skills.

## Not built (telemetry-gated)

Mechanical intent enforcement in run records (`--intent` flag + gate coupling): add only
if telemetry shows intent-mislabeling laundering delivery work past gates. A separate
"experiment" intent: `research-workflow`/`experiment-loop` already own it. Per-intent
model routing classes: no evidence of need.

## Handoff

- 2026-07-20: Opus adversarial review returned integrate-after-fixes (no blocker; the
  promotion boundary traced mechanically tight). Supervisor applied all findings: F1
  PoC rigor-floor now requires a recorded mode receipt (policy-resolved mode + research
  working-tree gate output) before any exemption; F2 `poc/` structure waiver added; F3
  destructive-refactor's intentional-behavior-change allowance clamped under refactor
  intent; F4 intent lanes subsume dev-workflow step 2 and resume at step 6 (no Test
  List re-seed, no 1a re-entry loop); F5 refactor-vs-hardening tie-break (measured
  delta → hardening, which gates on a baseline); F6 hardening ceiling numbers replaced
  with a citation to the canonical unit-test-operations copy; F7 PoC evidence exit
  reworded to fresh-confirmation registration (post-hoc registration fails the ledger
  gate). W3 wiring landed fully despite a stream stall at final-report time; state was
  verified file-by-file against the brief before acceptance.
- 2026-07-19: v1 designed; Sonnet workers author (W1 poc, W2 refactor+hardening, W3
  wiring+evals), Opus reviewer adversarially reviews the composed diff, supervisor
  adjudicates, integrates, PRs. Branch `intent-workflows` (based on
  `unit-test-design-skill`; merges after #96).

# Artifact registry + per-artifact lints (Wave 1) — design record

Owner: supervisor (architect). Continues the lint-migration program
(`plans/20260725-lint-migration.md`): SKILLs own judgment, lint owns
acceptability; machine-checkable failures close with a lint, not a note.
Wave 1 was scoped in the Wave-0 record as "artifact registry + per-artifact
lints (UI packs with symlink-escape, ExecPlan, Bug Report, Workflow Contract,
embedded NFR pack)". Two read-only exploration passes over every artifact
family preceded this adjudication; their load-bearing findings are recorded
inline where they changed the design.

## Registry

`.agents/artifact-registry.json` (hand-authored JSON — no YAML parser exists
in this repo's stdlib-only scripts; parallels `.agents/project-policy.yml` as
committed policy, with `schema_version` and a notes field). Each artifact kind
declares its detection rule and machine-checkable structure; checkers live in
code. Consumed by new `scripts/lint_artifacts.py` with the established
baseline ratchet (committed `scripts/artifact_lint_baseline.json`,
`--write-baseline`, new findings fail, stale reported).

Lint layout (structure budget forces the split up front):
`scripts/lint_artifacts.py` (CLI: registry load, discovery, dispatch,
baseline compare, report) + `scripts/artifact_checks_docs.py` (heading
checks) + `scripts/artifact_checks_packs.py` (pack checks). Checker modules
share one signature: `run_checks(repo_root, artifact_path, spec, registry) ->
list[str]` returning stable finding ids.

## Adjudications (the decisions in this wave)

1. **Bug Report — lint as-is.** Template and both real instances agree 1:1
   (strongest positive control). Exact `###` heading list from the template;
   `Workaround` stays optional per its own "(only if unavoidable)".
2. **Workflow Contract Review — template wins the fork.** The SKILL.md
   Output-expectation prose and the canonical template drifted apart, and real
   reports split 13 (template wording) vs 3 (prose wording, Decision on top,
   all 20260627). Adjudication: the template file is canonical (majority of
   instances, and it is what `metadata.templates` opens at output time). The
   SKILL.md prose list and the quality-gate evidence line are re-worded to
   the template's headings; the 3 prose-schema reports are BASELINED, never
   rewritten — historical reports are evidence and stay byte-identical.
3. **ExecPlan — keyword sections, and the design-record genre becomes real.**
   PLANS.md says "exact headings can differ, but content must exist", so the
   lint matches required sections by keyword alternatives, not exact strings
   (a mild narrowing of expressive power for checkability: new plans must use
   recognizable headings; pre-existing divergents are baselined). Reality has
   three genres: ~18 full ExecPlans, an 8-file 2026-07-05 batch missing 3
   sections (baselined as findings — shrinkage is the goal), and 3 files
   self-titled "design record" that PLANS.md never defined. The genre is
   formalized instead of flagged: an H1 containing "design record" selects a
   lighter contract (Handoff mandatory; the rest stays judgment), documented
   in PLANS.md. Rationale: supervisor adjudication waves genuinely have no
   WBS; forcing 11 sections would produce empty boilerplate, which the
   comment-discipline/economy principles reject. This record is itself the
   genre's first linted instance.
4. **UI packs — full structural lint despite zero instances.** Every UI-family
   check is fail-closed at creation time: required files (uidesign's list
   comes from the reference doc, which is stricter than the pack's own
   `outputs_required` — that template contradiction gets fixed this wave),
   JSON parse, no `<fill>` sentinel, and the token_refs rule (relative, no
   `..`, catalog prefix, suffix match, target exists). token_refs has a real
   incident behind it (`reports/bug-reports/uidesign-token-refs-path-
   disclosure.md`), so it is the one rule implemented most carefully.
5. **Symlink-escape — implemented as symlink-forbid.** No UI skill prose
   mentions symlinks; pack self-containment is prose-mandated as copy-only.
   So the lint forbids symlinks inside pack roots outright (simpler and
   stricter than resolve-and-check; a registry-level allowance can be added
   if a legitimate use ever appears). This is a NEW invariant introduced by
   the lint, not codified prose — recorded as such.
6. **Embedded NFR — subset check only; the schema fork is its own repair.**
   Zero instances exist here (artifacts land in consumer repos), and two
   skills promise the SAME paths (`target_profiles/<t>.yaml`,
   `docs/testing/resource-harness.md`, `physical_budgets.yaml`) with
   incompatible template schemas — so no single lint schema can exist yet.
   Wave 1 registers only `reports/resource/*.json` against the family's real
   JSON Schema as a subset check (required keys + result enum; honest about
   subset semantics). The intra-family schema fork is recorded as a finding
   and deferred to a dedicated reconciliation task — fixing two skills'
   template contracts is skill-content work, not lint work.
7. **Routing re-measurement skipped**, same rationale as Wave 0: no trigger
   row, description, or routing-table changes; the skill-text edits are
   wording alignment inside required references plus PLANS.md (not a skill).
   The next routine campaign covers it.

## Workers

W-A: lint CLI + docs checker + baseline + tests. W-B: packs checker + tests
(disjoint new files; shared signature pinned in both briefs). W-C: doc/skill
repairs (workflow-contract prose/quality-gate wording alignment,
uidesign_contract.yaml outputs_required completion, PLANS.md design-record
genre). Supervisor: registry (authored above), Makefile/CI/README wiring,
integration, Opus adversarial review.

## Handoff

- 2026-07-26: Wave 1 started on branch `lint-migration-w1` (based on main
  bc3900c). Registry and this record authored by the supervisor; three
  worker briefs dispatched. Deferred and recorded: embedded-NFR template
  schema fork reconciliation; tonemana-apply `.config` override asymmetry
  (minor, noted); `measure_skill_adoption.py` overlap with the new lint
  (adoption counter stays a counter).
- 2026-07-26 (integration): all three workers accepted — W-A lint CLI +
  docs checker + baseline (run bc389b7d), W-B packs checker + 26 tests
  (run 83b46c26), W-C doc repairs (run 712c3001). The first real run
  corrected two of this record's expectations, both honest-reported by
  W-A: the "2026-07-05 batch" was not uniform (structure-gates fires only
  missing-section:context; three OTHER files — two from 2026-04-24 and
  research-os-v0 — share the gap pattern and were baselined too), and
  `plans/README.md` was unintentionally caught by the execplan glob
  (registry defect, fixed by the supervisor: added to `exclude`, baseline
  regenerated to 13 paths / 43 ids). Wiring: `make lint-static`, CI step
  before unit tests (order pinned in tests/test_ci_wiring.py), README
  Validation entry — the command-docs drift lint confirmed the sync.
  326 tests OK; all lints and `make verify` green. Next: Opus adversarial
  review, then PR.
- 2026-07-26 (Opus adversarial review, run bf0cc57f): verdict
  integrate-after-fixes, no blockers. All seven should-fixes applied by the
  supervisor, each with a regression test: F1 headings inside fenced code
  blocks no longer satisfy checks (verified zero churn on the real corpus);
  F2 a design-record required section must have body content
  (`empty-section:` id); F3 the plans/README.md defect closed as a class
  (discovery skips `README.md` and `_`-prefixed basenames for every kind;
  literal excludes deleted); F4 `repo_relative` no longer resolves symlinks
  (baseline keys identify the linted path) and a symlinked PACK ROOT now
  fires `symlink-in-pack:.`; F5 malformed token_refs are findings
  (`bad-shape`/`unknown-kind`/`bad-type`) instead of silent skips or
  crashes; F6 remote-ref detection is a regex covering protocol-relative,
  cased, spaced, and href forms; F7 catalog id extraction accepts
  quoted/capitalized ids. Adopted notes: F8 design records now also require
  a decision/adjudication section (adds exactly one baseline id — the
  Wave-0 record, left as shrinkage backlog); F10 registry-driven reads fail
  with labeled errors; F16 `previews/style-tile.css` added to the catalog's
  required files. Recorded without code change: F9 — the ExecPlan lint's
  honest guarantee is "catches wholly-absent sections in good-faith
  documents", no more (keyword substrings are satisfiable by one broad
  heading; later waves must not over-trust it); F11 baseline is path-keyed
  and `--write-baseline` has no growth guard, consistent with
  skill-inventory semantics; F13 the SKILL.md bullet parentheticals
  describe template BODY content, not heading text; F14 the quality-gate
  workflow-contract evidence line now names two sections it previously
  omitted — a genuine tightening of the submit gate, made visible here on
  purpose (gates ratchet up, never down); F15 accepted as-is. F12 added to
  deferred: `concurrency-matrix` (`init_artifact.py` kind,
  `reports/concurrency/<slug>.md`) is a real artifact kind not yet in the
  registry, and `ARTIFACT_SPECS` vs the registry share kind names with no
  pinned relation. Also deferred: flipping `claude-opus-5` smoke_eval to
  passed — the review itself ran on it and is the qualifying supervised
  evidence (run bf0cc57f), but the catalog flip belongs in its own change,
  not this branch. Final state: baseline 14 paths / 44 ids, 333 tests OK,
  all lints and `make verify` green.

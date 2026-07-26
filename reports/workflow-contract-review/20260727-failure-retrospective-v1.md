# Workflow Contract Review — failure-retrospective v1

Reviewer: independent supervision run (Opus 5), delivery mode.
Inputs: `plans/20260726-failure-retrospective-v1.md` (ExecPlan) and the
binding user directive of 2026-07-26 (sections 1-19), read before the diff.

## Scope

- PR / branch: `failure-retrospective-v1`, based on `main` b66c946; working
  tree uncommitted at review time (15 modified, 22 untracked paths).
- Workflow surfaces:
  - New skill package `.agents/skills/failure-retrospective/` (SKILL.md 133
    lines, `references/failure-retrospective.md` 189, three templates).
  - Registry-driven artifact lint: two new kinds (`failure-retrospective`,
    `llm-wiki`) both routed to the new `learning` checker
    (`scripts/artifact_checks_learning.py` 383 lines +
    `scripts/artifact_checks_learning_wiki.py` 186).
  - `scripts/init_artifact.py` multi-file-pack support (new
    `create_artifact()` / `_create_pack()` seam).
  - Adjacent wiring: `execution-plans` (reference), `branch-completion`
    (SKILL body + Completion Record), `bug-investigation-and-rca`
    (reference), `research-synthesis` (SKILL body),
    `preflight-engineering` (resources-tier reference),
    `plans/_template_execplan.md` closing section.
  - `.agent/wiki/` scaffold (README + index) and
    `reports/retrospectives/README.md`.
- Generated artifacts:
  - `evals/skill-triggers/failure-retrospective.json` (5 positive / 6
    near-miss negative) and `evals/skill-behavior/failure-retrospective.json`
    (7 cases).
  - Measurement artifacts: `evals/routing-runs/20260727-retro-before-`,
    `-after-run1-`, `-after-run2-sonnet-5.json` plus
    `20260727-failure-retrospective-ab-report.md`;
    `evals/behavior-runs/20260727-failure-retrospective-sonnet-5.json` plus
    the new `evals/behavior-runs/README.md` section.
  - Regenerated indexes: `AGENTS.md` skill row, README skill map + catalog,
    `REFERENCES.md`, `CHANGELOG.md` v4.19.0, `.claude/skills/` symlink.

Out of scope by directive section 18 and confirmed absent from the diff:
external wiki service, vector search, automatic skill generation, new
modes/intents, retrospective-as-submit-blocker, full initializer refactor,
causality judged by lint, always-on wiki context.

## Source-of-truth chain

| Stage | Artifact / command | Producer | Consumer | Notes |
| --- | --- | --- | --- | --- |
| Skill contract | `.agents/skills/failure-retrospective/SKILL.md` | authored (run c1a60103) | agent at runtime; `report_skill_inventory.py`; `AGENTS.md` index | 133 lines vs soft cap 150; reach 322 vs budget 400; desc 408 chars, 0 description_flags, 0 risk_flags — verified by re-running `check_context_budget.py` and `report_skill_inventory.py` |
| Procedure detail | `references/failure-retrospective.md` | same | requires-tier load (always, when the skill fires) | 189 lines, inside the 400 reference ceiling |
| Pack schema | `templates/record.json` | same | pack authors; `learning` checker | 13 documented enum blocks — all 13 verified byte-equal to the checker's frozensets |
| Report schema | `templates/report.md` | same | pack authors; `learning` checker | 10 `##` headings verified equal to `REPORT_REQUIRED_HEADINGS` |
| Wiki schema | `templates/llm-wiki-entry.md` | same | wiki authors; wiki checker | 9 `##` headings verified equal to `WIKI_REQUIRED_HEADINGS` |
| Pack bootstrap | `python scripts/init_artifact.py --kind failure-retrospective --slug <slug>` | run 9bd9f356 | pack authors | writes `reports/retrospectives/<slug>/record.json` + `report.md` |
| Detection | `.agents/artifact-registry.json` kinds | supervisor-authored after the checker landed | `scripts/lint_artifacts.py` `CHECKER_MODULES["learning"]` | `detect_dir_glob: reports/retrospectives/*` matches the initializer's output dir; `required_files` matches the two written files; `detect_dir: .agent/wiki` matches the scaffold |
| Structure verdict | `python3 scripts/lint_artifacts.py` | run 3b812531 | `make verify`; quality-gate | pass (44 baselined), baseline file unmodified |
| Trigger measurement | `scripts/run_routing_eval.py` | supervisor | A/B report | before/after JSONs + report |
| Behavior measurement | `scripts/run_behavior_eval.py` | supervisor | behavior-runs README | see Finding F3 |

Chain verdict: consistent on every identity I could machine-check (enum
blocks, both heading sets, pack path, required-file list, checker-name
resolution) except the observe-first required-field set, which has three
divergent versions — Finding F8.

## Generated argv replay

Every command below was re-run by this review inside the worktree, not
taken from the worker reports.

| Step | Execution location | argv | Required env | Expected artifact | Stop/continue |
| --- | --- | --- | --- | --- | --- |
| Full chain | worktree root | `make verify` | none | exit 0, `Verification completed.` | continue (exit 0; 361 log lines; `new_warnings=0`, `stale_baseline=2`) |
| Unit suite | worktree root | `python3 -m unittest discover -s tests` | none | `Ran 428 tests ... OK` | continue (428 pass; new modules contribute 27 + 13 + 10 = 50) |
| Artifact lint | worktree root | `python3 scripts/lint_artifacts.py` | none | `artifact-lint: pass (44 baselined)` | continue; `scripts/artifact_lint_baseline.json` unmodified, so no new-finding concealment |
| Context budget | worktree root | `python3 scripts/check_context_budget.py` | none | `context-budget: pass` | continue |
| Submission lint | worktree root | `python3 scripts/lint_submission.py --working-tree` | none | `lint-submission: pass (no submission record; adoption phase)` | continue — no submission record exists yet, so acceptance item 16 is still open downstream |
| Boundary gate | worktree root | `python3 scripts/check_research_evidence.py --working-tree --policy .agents/project-policy.yml --mode delivery` | none | `research-evidence: pass (37 changed path(s))` | continue |
| Structure budget | worktree root | `python3 scripts/check_structure.py --working-tree` | none | `structure-budget: pass (7 source files checked)` | continue |
| Run judgement (x4) | worktree root | `python3 scripts/judge_agent_run.py --run-id <id> --require-accepted` | none | `accepted: true` | continue for all four IDs |
| Bootstrap replay | scratchpad copy | `create_artifact(repo_root, "failure-retrospective", slug)` | none | both pack files | continue |
| Checker replay (round 1) | scratchpad copy | `artifact_checks_learning.run_checks(...)` on 13 hand-built adversarial packs | none | finding lists | STOP — 8 of 13 returned zero findings (F1, F2, F6, F7, F9, F11) |
| Checker replay (round 2, after the fixes) | scratchpad copy | the same 13 packs re-run unchanged, plus 7 new probes targeting the fixes themselves | none | finding lists | STOP — 12 of 13 round-1 packs now blocked; the two that still pass are the accepted semantic limit (A6) and deferred F11. One NEW hole found in the F7 fix: F16 |
| Checker replay (round 3, after the F16 fix) | scratchpad copy | all round-1 and round-2 packs re-run unchanged, plus 4 new partial-resolution edge probes (D1-D4) | none | finding lists | continue — F16's payload now yields `retro:unknown-attempt-ref:L1:A9` plus both `retro:closure:5.1:L1` and `retro:closure:5.2:L1`; no regression in any earlier probe; every partial, all-unknown, and non-string ref shape fails closed |

## Producer/consumer consistency

| Producer | Artifact | Consumer | Required identity match | Result |
| --- | --- | --- | --- | --- |
| `init_artifact.py` `files[].default_output` | `reports/retrospectives/<slug>/{record.json,report.md}` | registry `detect_dir_glob` + `required_files` | directory path and both filenames | PASS |
| `templates/record.json` `_enums` (13 blocks) | documented enum sets | checker frozensets | set equality per block | PASS (13/13, machine-diffed) |
| `templates/report.md` `##` headings | 10 headings | `REPORT_REQUIRED_HEADINGS` | exact list equality | PASS |
| `templates/llm-wiki-entry.md` `##` headings | 9 headings | `WIKI_REQUIRED_HEADINGS` | exact list equality | PASS |
| directive section 5.5 (5 items) | observe-first required fields | `templates/record.json` `_enums` and `_check_observe_first_fields` | one shared list | PASS after fix — all three now list the same five fields including `missing_evidence`, re-diffed by machine |
| registry `forbid_fill_sentinel: true` | placeholder ban | `_check_forbid_fill_sentinel` `"<fill"` prefix | the templates must contain the matched token | PASS after fix — checker widened and both templates normalized to the bare token; blast radius of the shared-checker change verified as zero (no `tonemana/`, `uidesign/`, or `uiux/` instances exist in the repo) |
| directive section 149 Learning object | required learning fields | `artifact_checks_learning_fields.LEARNING_REQUIRED_FIELDS` (9) / `ATTEMPT_REQUIRED_FIELDS` (8) | per-object field presence | PASS after fix, with a residual nit — `applies_when` / `does_not_apply_when` are still not required, so a learning may carry no stated generalization bounds |
| `SKILL.md` Output expectation | decision output shape | `run_behavior_eval.py` `DECISION_MARKER_RE` / `expected_decision` | a documented decision line | PASS after fix — SKILL.md:128 carries a `Start with:` marker that `DECISION_MARKER_RE` parses (verified by calling the regex), and all 7 seeds declare `expected_decision` |
| learning `attempt_refs` | closure-rule scoping | `artifact_checks_learning_fields.resolve_attempt_scope()` | every named attempt id must resolve, and a broken reference must fail closed | PASS after fix — unresolvable ids emit `retro:unknown-attempt-ref:<lid>:<ref>`, and a wholly unresolvable list falls back to the record-level correlation so 5.1/5.2 re-engage |
| directive section 5.4 (5 recorded items) + README Skill Delta Gate | absorption evidence | `existing_skill_absorption` (3 fields) / `_has_absorption_rationale` (2 checks) | field coverage | PARTIAL — F11 |
| `branch-completion` Completion Record | `Learning capture:` block | directive section 10 prescribed block | field-for-field | PASS |
| `plans/_template_execplan.md` | `## Outcomes & Retrospective` block | directive section 10 prescribed block; execplan `keyword-sections` group `outcome|retrospective` | keyword presence | PASS |

## Run-set / target / workflow identity consistency

| Identity | Producer value | Consumer value | Result |
| --- | --- | --- | --- |
| run set | worker runs c1a60103 (skill+evals), 3b812531 (checker), 9bd9f356 (initializer), 068f8988 (wiring) | `.agents/runs/agent-runs.jsonl`, judged by explicit ID | PASS — all four `accepted: true`, `validation_passed: true`, `scope_compliant: true`, `outside_allowed_files: []`; `changed_files` ⊆ `allowed_files` verified per record; each carries a `brief_path` and 4-6 `validation.commands` with exit codes |
| workflow id | delivery mode, high risk, intent=feature | every record's `declared_mode: delivery`; boundary gate re-run in `--mode delivery` | PASS |
| target id / class | `focused_code_change` / `focused_code_edit` for all four workers | `.agents/model-routing/task-classes.yml` classes | PASS — no hard-coded model IDs anywhere in the diff |
| measured commit (routing before) | `commit: b66c9463…`, `variant: agent-instructions-playbook`, surface 68282 chars | main b66c946 | PASS |
| measured commit (routing after x2, behavior x2) | `commit: b66c9463…`, `variant: wt-retro`, surface 68829 chars | the branch's dirty working tree, which is NOT b66c946 | PASS after fix — the artifacts still stamp the base commit (unavoidable without committing first), but the A/B report now carries an explicit commit-field caveat telling readers to identify the after files by filename, not by commit equality |
| gate acyclicity | directive section 10: no quality-gate / submission-evidence coupling in v1 | grep of `.agents/skills/quality-gate/`, `.agents/skills/dev-workflow/`, `scripts/lint_submission.py`, `scripts/submission_run.py`, `scripts/check_research_evidence.py` | PASS — zero references to `failure-retrospective`; no cycle exists |
| AGENTS.md bootstrap | measurement-gated per directive section 10 | `git diff AGENTS.md` = 1 line, the generated skill-index row only | PASS — the wiki bootstrap line was correctly NOT added |

## Controller / target-local execution locations

The analogue here is the four-tier load contract: which instruction text
reaches the agent unconditionally, which only on a stated condition.

| Step | Expected location | Actual/generated location | Result |
| --- | --- | --- | --- |
| Trigger / anti-trigger / boundary table | SKILL.md body (unconditional once the skill is selected) | SKILL.md:26-65 | PASS |
| Closure rules 5.1-5.6 | SKILL.md body, because they are refusal rules | SKILL.md:97-117, restated in the reference | PASS — refusals are reachable without opening the reference |
| Enums, wiki operating rules, handoff conditions | requires-tier reference | `references/failure-retrospective.md`, listed in `metadata.requires` | PASS — requires-tier loads whenever the skill executes |
| Wiki inventory instruction for the reader path | `preflight-engineering` SKILL.md step 1 (inventory) | SKILL.md:36 now names `.agent/wiki/index.md` with the scope-matching rule inline; the four detailed rules stay in the resources-tier template | PASS after fix — the cap-neutral edit landed, SKILL.md is still 166/166 lines, and `check_context_budget.py` still passes |
| "Never load the whole wiki" guard | reachable at the point of use | `.agent/wiki/index.md:3-5` and `.agent/wiki/README.md` carry it in their own bodies | PASS — verified; this is what keeps F13 a nit rather than a should-fix on its own |
| Pack bootstrap command | SKILL.md Output expectation, cited by path not inlined | SKILL.md:124-126 | PASS |

## Deployment/runtime discovery

| Runtime boundary | Install path | Invocation path | Env/PATH assumption | Preflight | Result |
| --- | --- | --- | --- | --- | --- |
| `learning` checker resolution | `scripts/artifact_checks_learning.py` | `lint_artifacts.py` `CHECKER_MODULES["learning"]` dotted + bare fallback | repo root on `sys.path`, or `scripts/` for direct execution | dual-path import guard in both new modules | PASS — `test_checker_resolves_via_lint_artifacts` covers it; resolution is fail-closed (an unregistered checker name errors rather than skipping) |
| shape dispatch inside `learning` | one checker name, two artifact shapes | `detect_dir_glob` present → pack; `detect_dir == ".agent/wiki"` → wiki | none | `raise SystemExit` on an unrecognized spec | PASS — fail-closed, covered by `test_unrecognized_shape_raises` |
| shared pack helpers | `scripts/artifact_checks_packs.py` | imported private `_check_*` functions | none | dual-path import | PASS — reuse by import, not copy. The F2 fix widened the shared sentinel to a `"<fill"` prefix, which changes behavior for four other registered kinds; I checked the blast radius and it is currently zero, because no `tonemana/`, `uidesign/`, or `uiux/` instance exists in the repo, and the widening is strictly stricter when they appear |
| Claude Code skill surface | `.agents/skills/failure-retrospective/` | `.claude/skills/failure-retrospective` symlink | none | `sync_claude_skills.py`; `generate_agent_index.py --check` in `make verify` | PASS — symlink present and correct, index check green |
| worker brief provenance | `.agents/runs/<id>/brief.md` | run record `brief_path` | none | `.agents/runs/.gitignore` = `*` | PASS with a caveat: all four briefs exist locally, but the directory is git-ignored by pre-existing repo convention, so a downstream reader can verify the ledger row and not the brief body. Pre-existing, not introduced here |
| pack creation atomicity | `_create_pack` | `create_artifact` | filesystem | write-then-rollback of files this invocation created | PASS after fix — the behavior is unchanged, but `reports/retrospectives/README.md` no longer overclaims: it now scopes the guarantee to non-`--force` invocations and states the mixed-pack outcome under `--force` |

## Forbidden fallback checks

- filename-order artifact selection: none. Registry detection is by explicit
  glob/dir; `discover_instances` filters `detect_dir_glob` matches with
  `p.is_dir()`, so `reports/retrospectives/README.md` is correctly not
  treated as a pack. No ordinal or index-based selection anywhere.
- mtime/latest/newest artifact inference: none. The recurrence search
  (reference 4.6) is specified as a failure-signature match over four named
  fields, not "the most recent record". `recurrence.prior_records` holds
  explicit paths.
- stale prompt fallback: the routing harness rebuilds packs from the surface
  under test and grades against the same commit; `_load_response_batch`
  reports `batch_missing` / `batch_corrupt` / `case_missing_from_response`
  as `ungraded` rather than defaulting. The behavior run correctly lists 9
  `response_missing` entries instead of scoring them. PASS.
  One real defect in this family was found and fixed: `_rate(0, 0)` still
  returns `1.0`, so an empty decision denominator silently reports perfect
  accuracy — the harness behavior is unchanged (out of scope here), but the
  seeds now declare `expected_decision`, so the denominator is real. A
  second instance of the same family appeared in the F7 fix, where an
  unresolvable `attempt_refs` id silently degraded to "no preventable
  attempt" instead of failing — that was F16, and it is now fixed so a
  broken reference both reports itself and falls back to the stricter
  record-level rule. No silent-degradation path remains in this checker.
- raw co-presence as causal evidence: two violations of the spirit of this
  rule in the original measurement narrative, both now repaired. (a) The A/B
  report inferred "repacking variance" for a batch whose composition is
  provably unchanged — the report now retracts that mechanism explicitly,
  cites the batch-composition proof, discloses the one-sided-resampling
  caveat, and demotes the recovered aggregate in favour of the zero-fire
  result as the decision-carrying evidence. (b) The behavior narrative
  asserted decision-level correctness from a metric that measured nothing —
  the README now labels run 1's `decision_accuracy` a zero-denominator
  artifact, keeps both runs unedited, and cites run 2's real 7/7. Neither
  was ever fabrication: every published number is exactly reproducible from
  the committed JSONs (I recomputed recall, compliance, co-fire, and the
  new-case rates independently, before and after, and got identical values).

## Claim boundaries

- Workflow authority artifacts: `.agents/skills/failure-retrospective/SKILL.md`
  and its requires-tier reference define when to retrospect, what counts as
  learning, where it is promoted, and which judgments stay human. The
  directive of 2026-07-26 is the binding spec above them.
  `.agents/artifact-registry.json` owns acceptability only, never the
  question of when an artifact should exist.
- Validation artifacts: `scripts/artifact_checks_learning{,_wiki}.py`,
  their 40 unit tests, `scripts/init_artifact.py`'s 10 tests, and the
  `make verify` chain. These bound structure only. Both modules state the
  limit explicitly in their docstrings and the reference restates it under
  "Lint boundary" — causal, semantic, and generalization correctness is
  never lint-judged. I found no check that crosses that line: the
  report-heading and wiki duplicate-link checks exceed the directive's
  literal section 8 bullet list but are grounded in sections 6/7 and are
  purely structural. The ExecPlan's decision-log adjudication on those two
  is sound and I am not reopening it.
- Measurement artifacts: the three routing JSONs and the two behavior JSONs.
  They support "failure-retrospective is selected on 0 of 212 common cases",
  "9/9 new-case recall, 23/24 new-case compliance", "discovery surface
  +0.8%", "output-contains 27/33", and — after the F3 re-run on fresh
  subjects — "decision accuracy 7/7 on a real denominator". They still do
  NOT support "recall is unchanged by this change" at n=1 symmetry, and the
  A/B report now says so itself.
- Claims now supported that were blocked at round 1:
  - "7/7 decision behaviors correct" — supported by
    `20260727-failure-retrospective-run2-sonnet-5.json`, where all seven
    cases carry `decision_match: true` on a denominator of 7. I confirmed
    the run used fresh subjects rather than a re-grade: the
    missing-fragment sets differ from run 1 case by case, even though the
    aggregate output-contains rate coincidentally stayed 27/33.
  - "Retrospective packs and wiki entries are checked by artifact lint"
    (acceptance items 5 and 6) — a hollow pack and an unfilled wiki entry
    are now both rejected, re-verified against my original probes.
  - "Routing recall unchanged" — now correctly stated with its caveat and
    with the zero-fire result carrying the argument.
  - "A preventable, deterministically checkable failure cannot close on
    prose alone." Now supported. All four evasions I found — F1's three plus
    F16's — are closed, and I re-ran every probe unchanged to confirm it.
    The claim carries one documented boundary: lint verifies that a
    lint/harness retention action is *declared* with a resolvable target and
    a verification command, not that the action is genuine. Directive
    section 8 places that judgment outside the lint by design, and the skill
    text says so.
- Blocked claims that remain:
  - Acceptance items 16 (clean submission evidence record) and 17 (branch
    completion record with learning capture) are not yet claimable — no
    submission record exists (`lint-submission: pass (no submission record;
    adoption phase)`) and no completion record is in the diff. Both are
    correctly listed as pending in the ExecPlan.

## Findings

Reproduction note: every "verified" finding below was produced by calling
`artifact_checks_learning.run_checks()` directly against packs built in a
scratchpad outside the worktree. No file in the change set was modified by
this review; this report is the only file created.

Round-2 status: after the fixes were applied I re-ran all 13 round-1
adversarial packs unchanged, plus 7 new probes aimed at the fixes
themselves, plus the full validation chain. Every fix the coordinator
reported is real and independently confirmed below — I did not take any of
it on the report. One new hole was introduced by the F7 fix and is filed as
F16.

| Round-2 re-verification | Result |
| --- | --- |
| `make verify` | exit 0 |
| `python3 -m unittest discover -s tests` | `Ran 437 tests … OK` |
| `python3 scripts/lint_artifacts.py` | pass (44 baselined); `artifact_lint_baseline.json`, `skill_inventory_baseline.json`, `instruction_graph_baseline.json` all still unmodified — no new baseline entries |
| `python3 scripts/check_structure.py --working-tree` | pass (10 source files); `artifact_checks_learning.py` at exactly 400 |
| `python3 scripts/check_context_budget.py` | pass; `preflight-engineering/SKILL.md` still 166/166 |
| Round-1 probes A1-A5, A8-A10, B1-B3 | all now blocked |
| Round-1 probes A6, A7 | still clean — A6 is the accepted semantic limit (lint cannot judge whether a `local-lint` action is real), A7 is deferred F11 |
| New probes C1-C6 | round 2: C1 failed — see F16. Round 3 after the F16 fix: C1 blocked, C2-C6 unchanged and correct |

Round-3 status: F16 is fixed and independently re-verified. `make verify`
exit 0, 438 tests OK, `artifact-lint: pass (44 baselined)` with all three
baseline files still unmodified, `structure-budget: pass` (main checker now
397 lines), `context-budget: pass`. Every finding in this review is now
either closed or deferred by agreement.

| Round-3 probe | Result |
| --- | --- |
| F16 payload (`preventable` A1, `deterministic` L1, `repeated`, `llm-wiki`-only action, `attempt_refs: ["A9"]`) | `retro:unknown-attempt-ref:L1:A9` + `retro:closure:5.1:L1` + `retro:closure:5.2:L1` — the finding fires and both rules re-engage |
| C1 (dangling ref) | blocked — unknown-ref finding plus 5.1 |
| C3 (`attempt_refs: []`) | 5.1 fires via the record-level fallback — unchanged |
| C4 (correctly scoped to the preventable attempt) | 5.1 fires — unchanged |
| D1 (one unknown + one benign resolvable ref) | scopes to the resolvable subset and still reports the unknown ref, so the mis-scoping stays auditable |
| D2, D3 (unknown mixed with the preventable ref; all-unknown list) | fail closed with both the unknown-ref findings and 5.1 |
| D4 (non-string ref) | fails closed |
| All round-1 and round-2 probes re-run unchanged | no regression; A6 and A7 remain the only clean passes |

| ID | Severity | Finding | Required fix |
| --- | --- | --- | --- |
| F1 | blocking | The checker never requires the per-object fields that gate closure rules 5.1/5.2/5.3, so the change's center principle is evadable three ways, each verified clean (zero findings): (a) omit `enforceability` and `criticality` from the learning; (b) omit `preventability` from every attempt (`any_preventable` is `False`, disabling 5.1 and 5.2); (c) `learnings: []` with `current_work_disposition: harden-repository`. `_check_record_top_level` (`scripts/artifact_checks_learning.py:151-166`) validates only the nine top-level fields; `_check_learning_enums` (:270-286) and `_check_attempts` (:198-220) skip any field whose value is `None`; `_check_closure_rules` (:288-303) reads those optional fields with `.get()`. Falsifiable scenario: a preventable, deterministically checkable oracle defect is closed with a single `llm-wiki` retention action and a prose note; lint is green; acceptance item 7 is false. The workers implemented directive sections 8/15 literally — those lists name only *top-level* required fields — so the gap is in the contract as much as the code. | Add per-object required-field findings: `retro:missing-attempt-field:<aid>:<field>` for `result`/`failure_class`/`preventability`, and `retro:missing-learning-field:<lid>:<field>` for `claim`/`evidence_refs`/`causal_confidence`/`scope`/`enforceability`/`criticality`/`retention_actions` (directive sections 147/149 are the field lists). Add a coherence finding when `learnings` is empty while `attempts` is non-empty unless `current_work_disposition` is `no-durable-change` or `insufficient-evidence`. Add the three probes as unit tests. |
| F2 | blocking | `forbid_fill_sentinel: true` is inert for both new kinds. `_check_forbid_fill_sentinel` matches the literal `"<fill>"` (`scripts/artifact_checks_packs.py:89`), but `templates/report.md` and `templates/llm-wiki-entry.md` use only `<fill: …>`, which does not contain that token. Verified: a pack whose `record.json` is the untouched template (`title: ""`, `attempts: []`, `learnings: []`) and whose `report.md` is 100% placeholders returns **zero** findings once `retrospective_id` is set in both files and `trigger.evidence_refs` has one entry — while `"<fill:" in report.md` is still `True`. Same for a wiki entry: the untouched template passes once `Last verified:` is a real date. House convention elsewhere uses the bare token (e.g. `.agents/skills/tonemana-apply/templates/review_notes.md`), so this is a deviation, not a checker limitation. Falsifiable scenario: `init_artifact.py` output is committed unedited, lint is green, and acceptance items 5/6 are satisfied by an empty shell. | Replace `<fill: hint>` with `<fill>` plus the hint as adjacent prose in both templates (template-side is the safe edit — widening the shared checker to `<fill` would change behavior for four other registered kinds). Add a unit test that lints each template as a pack/entry and asserts a `fill-sentinel` finding. |
| F3 | blocking | The behavior-eval decision claim is unmeasured. All 7 new cases lack `expected_decision`, so `decision_match` is `null` for every one, `decision_records` is empty, and `_rate(0, 0)` returns `1.0` (`scripts/run_behavior_eval.py:219-221, 231-232, 236-237`). The artifact therefore records `decision_accuracy: 1.0` on a zero denominator, while `evals/behavior-runs/README.md` states "decision-level behavior correct in every case" and the ExecPlan WBS states "all 7 decision behaviors correct". The only mechanically measured signals are output-contains 27/33 (81.82%, recomputed independently) and findings 0/16. The raw responses are not in the repo, so the narrative is unverifiable. The repo already documents this exact trap for `unit-test-design` in the same README (2026-07-25 section); `quality-gate.json` carries `expected_decision` on 6/6 cases. Falsifiable scenario: a reader takes `decision_accuracy: 1.0` as 7/7 and treats acceptance item 4 as measured. | Add a decision line to `failure-retrospective` SKILL.md's Output expectation in the form `run_behavior_eval.py` already parses (`Start with: ` + a backticked marker), e.g. a `Disposition: <one of the four>` first line — the skill already mandates exactly one disposition, so this adds a contract, not a rule. Set `expected_decision` on the 7 seed cases and re-run. Until re-run, state in both the README section and the ExecPlan that `decision_accuracy` is 0/0 (not measured) and that the decision-level assessment is a manual read of uncommitted responses. |
| F4 | should-fix | The run-1 dip adjudication's stated mechanism is disproved for the cluster that carries it, and the resampling asymmetry is undisclosed. `evals/routing-runs/20260727-failure-retrospective-ab-report.md:25-39` attributes the −5.18pt run-1 recall to "single-subject + repacking variance". At `DEFAULT_BATCH_SIZE = 18`, the 10 clustered newly-missed cases sit at indices 73-89 = batch-04; the 11 new cases insert at indices 102-112, so batches 00-04 are byte-identical in composition between the before and after runs (verified by reconstructing both batchings). Repacking therefore cannot explain 62% of the regression — only subject variance or the +547-char surface can. Separately, only the six regressed batches were resampled while the before side stayed n=1, so "recall returned EXACTLY to the before value" is a best-of-two-on-the-losing-tail figure, which is the expected output of selective resampling rather than evidence of no effect. | Correct the mechanism to "single-subject variance; batch-04's composition is unchanged, so repacking is not a candidate for the dominant cluster", and add the asymmetric-resampling limitation explicitly. Lead the no-effect argument with the evidence that actually carries it (zero common-case fires in both after runs). |
| F4b | should-fix | Both after-side routing JSONs and the behavior JSON record `commit: b66c9463f24cfe0c865c3cf59559b6131b4151f3` — the base commit — while measuring the branch's dirty working tree (`variant: wt-retro`, surface 68829 vs the before run's 68282 at the same recorded commit). `evals/routing-runs/RUNBOOK.md` section 1 explicitly requires building from a clean checkout at the commit under test "so the `commit` recorded in the graded output is trustworthy", and section 4 tells readers to check `commit` equality before comparing. Falsifiable scenario: a later reader runs `report --graded before.json after-run2.json`, sees matching commits, and concludes the two measured the same surface. | Re-grade against a committed branch tip, or add an explicit dirty-worktree provenance note to the three artifacts and to the A/B report stating that `commit` is the base, not the measured surface. |
| F5 | should-fix | The confusion metric is measured but never reported, though directive section 14 requires it and sections 17(14)/19 require all routing metrics to be reported. `evals/routing-runs/20260727-failure-retrospective-ab-report.md` has no confusion row. The committed JSONs show before `{comment-discipline: 1, quality-gate: 4}` versus both after runs `{comment-discipline: 1, embedded-nfr-harness-design: 1, implementation-economy: 1, quality-gate: 5|4}` — two new confusion entries, unadjudicated. | Add a confusion row to the report's metric table with before / run1 / run2 values and one line of adjudication for the two new entries (they are almost certainly the same batch-04/06 variance as F4, which is checkable from the per-case data). |
| F6 | should-fix | Path safety is applied only to retention-action `target` and `artifact_path` (`scripts/artifact_checks_learning.py:258-259`). `trigger.evidence_refs`, `attempts[].evidence_refs`, `learnings[].evidence_refs`, and `recurrence.prior_records` are never path-checked, although directive section 8 mandates "repo-relative paths only (absolute and `..` forbidden)" as a general rule and section 16 names evidence refs explicitly. Verified: a record whose refs are `/etc/passwd`, `../../../home/user/.ssh/id_rsa`, `../../secrets.env` and whose `prior_records` is `../../../etc/hosts` returns zero findings. | Run `_check_path_safety` over all three evidence-ref lists and `recurrence.prior_records`, with ids `retro:path:absolute|traversal:evidence_refs:<trigger|aid|lid>:<index>` and `…:prior_records:<index>`. Add unit tests. |
| F7 | should-fix | Re-examination of the R-B record-level 5.1/5.2 adjudication (ExecPlan decision log, 2026-07-26), which this review was asked to reopen. The record-level fallback is correct, but the conclusion "it over-flags safely" is not supported. Over-flagging creates pressure on exactly the one field that disables both hard rules: verified, flipping a single attempt's `preventability` from `preventable` to `productive-exploration` removes the 5.1 finding, and with `criticality: advisory` the record goes fully clean. Nothing detects that relabel. The premise "the schema has no attempt-to-learning link" is a schema choice, not a constraint: directive section 131 calls its schema a *minimum*, and the same additive reasoning was already accepted for the observe-first fields, so an optional link is equally guess-free and strictly closer to section 5.1's per-learning reading. | Add an optional `attempt_refs: []` to the Learning object; correlate 5.1/5.2 per-learning when it is present and fall back to record-level when it is absent. Document it in `templates/record.json` and the reference, and record the amended adjudication in the ExecPlan decision log. |
| F8 | should-fix | Three divergent versions of the observe-first required-field set. Directive section 5.5 names five items (missing evidence, next signal, artifact path, re-evaluation condition, owner/tracking reference); `_check_observe_first_fields` (`scripts/artifact_checks_learning.py:239-245`) enforces four (`signal`, `artifact_path`, `revisit_condition`, `tracking_ref`); `templates/record.json:97-101` documents three, dropping `tracking_ref`. Verified by diffing the template block against the function source. Falsifiable scenario: an author follows the template exactly and gets an unpredictable `retro:closure:5.5:<lid>:<idx>:tracking_ref` finding; "missing evidence" has no schema slot at all. The ExecPlan's claim that "the record.json template now documents them" is 3/4 true. | Make one list canonical: add `tracking_ref` and a `missing_evidence` field to the template's documented set and to the checker, and cite section 5.5 next to it. |
| F9 | should-fix | Wiki entries below the top level are silently unchecked. `artifact_path.glob("*.md")` (`scripts/artifact_checks_learning_wiki.py:176-178`) is non-recursive, so `.agent/wiki/sub/page.md` gets no heading check, no fixed-field check, and no orphan check, while `_check_dead_links` happily resolves the link to it. Verified: an entry with none of the nine headings and `Status: bogus` / `Confidence: made-up`, linked from `index.md`, returns zero findings. Only the inherited fill-sentinel and symlink walks are recursive. | Switch to `rglob("*.md")`, apply `INFRA_FILENAMES` per directory, and key entry findings and orphan detection on the posix path relative to the wiki root rather than `.name` (which would also collide today for same-named files in different directories). |
| F10 | nit | Directive section 18's "no performance appraisal, no individual-responsibility records" has no expression in any shipped instruction. Neither SKILL.md nor the reference forbids naming individuals in an attempt narrative, and `failure_class: coordination` plus the required "owner/tracking reference" invite it. The non-goal exists only in the ExecPlan, which the runtime agent never loads. | Add one anti-rule line to SKILL.md's Purpose or Closure section: record decisions, signals, and boundaries — never individuals' names or performance. |
| F11 | nit | The Skill Delta Gate is not machine-linked. Directive section 5.4 requires five recorded items and README's gate adds a "≥2 positive / ≥3 negative" trigger-boundary test, but `existing_skill_absorption` has slots for only `skills_considered` / `decision` / `rationale`, and `_has_absorption_rationale` (`scripts/artifact_checks_learning.py:143-149`) accepts any non-empty string. Verified: `{"skills_considered": ["x"], "decision": "not-absorbed", "rationale": "no"}` plus a `new-skill-candidate` action returns zero findings. At least three of the five items (decision delta, positive examples, near-miss negatives) are structurally checkable list fields. | Add `runtime_decision_delta`, `positive_examples`, `near_miss_negatives`, and `why_existing_insufficient` to the absorption object; require them non-empty (and `positive_examples` ≥ 2, `near_miss_negatives` ≥ 3, matching the README gate) whenever a `new-skill-candidate` action is present. |
| F12 | nit | No cheap exit for `no-durable-change`. SKILL.md:119-133 mandates the two-file pack unconditionally, while `no-durable-change` on productive exploration is an expected and measured outcome (behavior case 3). Eight trigger conditions include two that fire often ("a workaround or temporary mitigation was left in place"; "a discovery changed mode, risk, intent, route, owning skill, or a major design assumption"), so the fixed per-fire cost is the practical over-weight risk. The routing measurement gives real comfort here — zero fires on 212 common cases — but the artifact contract still has one tier only, and combined with F1(c) the cheapest compliant response is a hollow pack. | State in the Output expectation that a `no-durable-change` outcome with no learnings is recorded as a line in the ExecPlan "Outcomes & Retrospective" block or the Completion Record rather than as a pack — and pair it with F1's empty-learnings check so the hollow-pack route closes at the same time. |
| F13 | nit | The `preflight-engineering` wiki-inventory rule sits in a resources-tier file (`references/repo-inspection-output-template.md`) whose SKILL.md-stated load condition is "when summarizing helper output" (SKILL.md:44, :110), while the inventory moment is step 1 and the helper collectors only run for unfamiliar repos or missing `AGENTS.md`. The 166/166 ratchet cap that forced this is real (verified: `SKILL_MD_RATCHET_CAPS[".agents/skills/preflight-engineering/SKILL.md"] = 166`, file is 166 lines). Weighing it as asked: the dangerous half is already covered, because `.agent/wiki/index.md:3-5` and `README.md` carry "read only matching entries; never load the whole wiki" in their own bodies, so the over-load footgun is guarded at the point of use. What stays unreachable is the instruction to inventory the wiki at all and to cross-reference it from `.agent/ctx`. Hence nit, not should-fix — but the cap does not actually force the omission. | Cap-neutral fix: extend the existing inventory bullet at `preflight-engineering/SKILL.md:35`, which already lists `.agent/`, to `.agent/` (including `.agent/wiki/index.md` when present) — zero net lines, no cap breach. Keep the output slot and the four detailed rules in the template. |
| F14 | nit | `wiki:dead-link` conflates traversal with dead (`scripts/artifact_checks_learning_wiki.py:157`): any `..` or absolute href in `index.md` is reported as a dead link. A legitimate `[SKILL](../../.agents/skills/failure-retrospective/SKILL.md)` cross-reference from the index is therefore a lint error. The shipped `index.md:9-10` already works around it by writing the path as inline code instead of a link, which is evidence the constraint bites in practice. | Either allow `..` hrefs that resolve under `repo_root`, or keep the ban and say so in `.agent/wiki/README.md` so authors are not surprised. |
| F15 | nit | `reports/retrospectives/README.md:11-12` claims the initializer "fails without leaving a partial pack behind", but `_create_pack`'s rollback removes only files this invocation created (`scripts/init_artifact.py:74-101`, and the docstring says so): under `--force` over an existing pack, a mid-way failure leaves `record.json` rewritten and `report.md` stale. `test_no_partial_creation_when_second_target_is_a_directory` covers only the fresh-creation path. | Either narrow the README sentence to fresh creation, or snapshot pre-existing content under `--force` and restore it on rollback, with a test for the force path. |

| F16 | blocking — **CLOSED in round 3** | **New — introduced by the F7 fix, found in round-2 probing; fixed and re-verified.** Resolution moved to `artifact_checks_learning_fields.resolve_attempt_scope()`: every unresolvable entry emits `retro:unknown-attempt-ref:<lid>:<ref>`, and a wholly unresolvable list returns the record-level `any_preventable` so 5.1/5.2 re-engage. I re-ran the exact payload and it now yields the unknown-ref finding plus both closure findings, and I added four partial-resolution edge probes (D1-D4) that all fail closed. `tests/test_artifact_checks_learning_fixes.py:105-118` asserts both halves — the finding and the re-engaged 5.1 — not just the finding. Original text follows. An unresolvable `attempt_refs` entry silently disables closure rules 5.1 *and* 5.2. `_check_learnings` (`scripts/artifact_checks_learning.py:336-345`) builds `by_id` from the record's attempts and then computes `scoped = [by_id[r] for r in refs if r in by_id]` — the `if r in by_id` guard drops ids that match no attempt, with no finding emitted. When every ref is unresolvable, `scoped` is empty, `learning_preventable` becomes `False`, and both 5.1 and 5.2 go silent; the record-level fallback does not re-engage, because the `else` branch is only taken when `attempt_refs` is absent or empty. Verified: a record with a `preventable` attempt `A1`, a `deterministic` learning, `recurrence: repeated`, a single `llm-wiki` retention action, and `attempt_refs: ["A9"]` returns **zero findings** — the exact scenario F1 was raised to make impossible, reopened in a more deniable form, since an invented or typo'd id reads as an honest mistake rather than a deleted field. `attempt_refs: []` and a correctly-scoped `["A1"]` both behave correctly (probes C3, C4), and `tests/test_artifact_checks_learning_fixes.py:69-77` covers only the resolvable case, so no test catches this. | Emit `retro:unknown-attempt-ref:<lid>:<ref>` for every `attempt_refs` entry that matches no attempt id, and fall back to the record-level `any_preventable` when no ref resolves, so a broken reference fails closed rather than open. Add the C1 payload as a regression test. |

Severity key: **blocking** = an acceptance item in directive section 17 is
not genuinely met; **should-fix** = a real defect or an unsupported claim
that must be repaired before submission but does not by itself falsify an
acceptance item; **nit** = worth fixing, safe to defer with a tracked
follow-up.

### Round-2 disposition of findings F1-F15

| ID | Round-2 status | How I confirmed it |
| --- | --- | --- |
| F1 | CLOSED | New `scripts/artifact_checks_learning_fields.py` adds `retro:missing-field:attempt|learning:<id>:<field>` over the section 147/149 field lists plus `retro:empty-learnings:<disposition>`, wired at `artifact_checks_learning.py:373-374`. All three of my original evasions now produce findings (probes A1, A2, A4 re-run unchanged). Residual nit: `applies_when` / `does_not_apply_when` are not in `LEARNING_REQUIRED_FIELDS`, so generalization bounds may still be absent. |
| F2 | CLOSED | `_check_forbid_fill_sentinel` now matches the `"<fill"` prefix and both templates were normalized to the bare token. My hollow-pack probe B1 now returns `retro:fill-sentinel:report.md`; the unfilled wiki entry B3 returns `wiki:fill-sentinel:c.md`. Shared-checker blast radius checked: zero instances of the other four affected kinds exist. |
| F3 | CLOSED | SKILL.md:128 carries `Start with: ` + a backticked `Disposition:` marker, which I confirmed `DECISION_MARKER_RE` actually parses; all 7 seeds declare `expected_decision`; `20260727-failure-retrospective-run2-sonnet-5.json` has 7 non-null `decision_match`, all `true`. Fresh subjects confirmed: the per-case missing-fragment sets differ from run 1. Run 1 is retained and its zero-denominator artifact is documented in the README. |
| F4 | CLOSED | The A/B report retracts the repacking mechanism by name, cites the byte-identical batch composition, discloses the one-sided-resampling caveat, and names the zero-fire result as the decision-carrying evidence. |
| F4b | CLOSED | Commit-field caveat added, instructing readers to identify after-side files by filename rather than commit equality. |
| F5 | CLOSED | Confusion delta now reported (`embedded-nfr-harness-design` +1, `implementation-economy` +1) and adjudicated as known-variance families. |
| F6 | CLOSED | `_check_ref_safety` sweeps `trigger.evidence_refs`, per-attempt and per-learning `evidence_refs`, and `recurrence.prior_records`. My exact payload (probe A5) now blocks. |
| F7 | CLOSED | Optional `attempt_refs` scoping is implemented, documented in the template `_enums`, and behaves correctly for resolvable ids, for the absent/empty fallback, and — after the round-3 F16 fix — for unresolvable and partially-resolvable lists. |
| F8 | CLOSED | Directive section 5.5, `_check_observe_first_fields`, and the template `_enums` block now all carry the same five fields including `missing_evidence` (machine-diffed). |
| F9 | CLOSED | `rglob("*.md")` with findings and orphan detection keyed on the wiki-relative posix path. My subdirectory probe A9 now blocks. |
| F10 | CLOSED | "Never about people" section added to the requires-tier reference, so it loads whenever the skill fires. |
| F13 | CLOSED | `preflight-engineering/SKILL.md:36` now names `.agent/wiki/index.md` with the scope-matching rule inline, cap-neutral at 166/166 as I proposed. |
| F15 | CLOSED | The retrospectives README now scopes the atomicity guarantee to non-`--force` runs and states the mixed-pack outcome under `--force`. |
| F11, F12, F14 | DEFERRED as agreed | Re-confirmed still open (probe A7 still passes clean for F11); all three were filed as nits and are safe as tracked follow-ups. |

### Directive section 17 acceptance audit

| # | Item | Verdict |
| --- | --- | --- |
| 1 | Skill Delta Gate passed | MET in substance — runtime decision delta is real (route-to-skill plus refuse-to-close); absorption was judged against the five adjacent skills and recorded as a boundary table; 5 positive / 6 negative cases exceed the ≥2/≥3 bar; the output contract is a concrete pack; SKILL.md is 133/150 with detail in `references/`. Not recorded as an explicit gate checklist anywhere, which is a bookkeeping gap only. |
| 2 | SKILL.md in budget, detail split out | MET — 133 lines, reach 322/400, `context-budget: pass` re-run. |
| 3 | Trigger boundary confirmed by routing eval | MET — 5/5 positive recall, zero fires on 212 common cases in both after runs, no leakage into bug-RCA / research-synthesis / branch-completion cases (verified per case). |
| 4 | Behavior eval judges the main learning routing correctly | MET after fix — run 2 measures decision accuracy 7/7 on a real denominator of 7, with fresh subjects; output-contains 27/33 recomputed independently. |
| 5 | Retrospective pack checked by artifact lint | MET after fix — F1 and F2 closed; a hollow pack is now rejected. |
| 6 | Wiki entry + index checked by artifact lint | MET after fix — F2 and F9 closed; unfilled entries and subdirectory entries are now both checked. |
| 7 | Preventable deterministic failure cannot close docs-only | MET after fix — all four evasions I found (F1's three plus F16's) are closed and re-verified by re-running the original probes unchanged. Residual, documented, and accepted: lint cannot judge whether a declared `local-lint` action is genuine (probe A6), which directive section 8 explicitly places outside the lint boundary. |
| 8 | Project-specific learning separated into wiki + local enforcement | MET — rule 5.3 is implemented and correctly fires in the control probe; behavior case 1 exercises it. |
| 9 | Cross-project absorption judged first | MET in the instruction (SKILL.md closure rules, reference 5.4) and measured in behavior case 6; structurally weak — F11. |
| 10 | Non-firing on ordinary RCA / disconfirmed experiment / transient retry | MET — all six near-miss negatives measured, zero `failure-retrospective` selections. |
| 11 | No quality-gate / submission-evidence cycle | MET — verified by grep across the gate skills and all three gate scripts. |
| 12 | Workflow-contract review Decision = submit | MET — this report's Decision is submit. |
| 13 | No baseline concealment of new lint findings | MET — re-confirmed after the fixes: all three baseline files still unmodified; `new_warnings=0`, `stale_baseline=2` (shrinkage). |
| 14 | All routing/behavior metrics reported | MET after fix — confusion delta now reported and adjudicated (F5); decision accuracy now measured and its earlier zero-denominator artifact documented rather than quietly replaced (F3). |
| 15 | `make verify` succeeds | MET — re-run after the fixes, exit 0. |
| 16 | Clean submission evidence record | OPEN — no submission record exists yet; correctly pending. |
| 17 | Branch completion record with learning capture | OPEN — the `Learning capture:` block is added to the `branch-completion` template; no completion record is in the diff yet. Correctly pending. |

## Decision

submit

Verdict for the parent: **integrate-as-is**.

Every finding this review raised is now closed or deferred by agreement,
and I confirmed each closure by re-running my own probes and the full
validation chain rather than by reading the change descriptions. Across
three rounds I filed sixteen findings: F1-F10, F13, F15, and F16 are closed
and re-verified; F11, F12, and F14 stay open as agreed nits with tracked
follow-ups.

Round-3 verification. The F16 fix moved attempt-scope resolution into
`artifact_checks_learning_fields.resolve_attempt_scope()`, which reports
every unresolvable `attempt_refs` entry and falls back to the record-level
correlation when nothing resolves. My exact payload — a `preventable`
attempt, a `deterministic` learning, `recurrence: repeated`, a lone
`llm-wiki` retention action, and `attempt_refs: ["A9"]` — now yields
`retro:unknown-attempt-ref:L1:A9` together with both `retro:closure:5.1:L1`
and `retro:closure:5.2:L1`. I added four partial-resolution edge probes the
fix's own test does not cover (one unknown ref alongside a benign
resolvable one, one unknown alongside the preventable one, an all-unknown
list, and a non-string ref); all four fail closed, and the partial case
still surfaces the unknown ref so a mis-scoping stays auditable. Re-running
every round-1 and round-2 probe unchanged shows no regression. The
regression test asserts both halves of the contract — the finding and the
re-engaged rule — not just the finding. `make verify` exit 0, 438 tests OK,
`artifact-lint: pass (44 baselined)` with all three baseline files still
unmodified, `structure-budget: pass`, `context-budget: pass`.

Why this is now submittable. The change's center principle — that a
preventable, deterministically checkable failure cannot close on prose
alone — is enforced against every evasion I could construct. The boundary
contract against `bug-investigation-and-rca`, `research-synthesis`,
`quality-gate`, and `branch-completion` is clean and measured, with
`failure-retrospective` selected on zero of 212 common cases in both
after-side runs. The gate graph is acyclic by verified absence, so the
directive's no-cycle requirement holds. The registry / initializer /
template / checker chain is byte-consistent on every identity I could
machine-check. The lint stays strictly structural and declares its own
boundary. And the measurement artifacts now document their own earlier
errors — the retracted repacking mechanism, the one-sided-resampling
caveat, the zero-denominator decision metric — instead of quietly
overwriting them, which is the behavior this playbook is trying to
institutionalize.

Fifteen of the sixteen directive section 17 acceptance items are met. Items
16 and 17 (clean submission evidence record; branch completion record with
learning capture) remain correctly pending downstream of this review.

Carried forward as tracked follow-ups, none blocking: F11 (the Skill Delta
Gate's five required items have no schema slots, so `new-skill-candidate`
passes on any non-empty rationale), F12 (no cheap exit for a
`no-durable-change` outcome, which still mandates a full pack), F14
(`wiki:dead-link` conflates traversal with dead, so a legitimate `..`
cross-reference from `index.md` is a lint error), and the residual nit that
`applies_when` / `does_not_apply_when` are not required fields, so a
learning may carry no stated generalization bounds. Also carried: the
accepted and documented limit that lint verifies a lint/harness action is
declared with a resolvable target and a verification command, not that it
is genuine — directive section 8 places that judgment outside the lint.

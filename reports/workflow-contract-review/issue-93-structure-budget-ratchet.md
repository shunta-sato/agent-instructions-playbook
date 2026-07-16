# Workflow Contract Review: Structure-Debt Baseline (Issue #93)

## Decision

submit

## Workflow surfaces reviewed

- `scripts/check_structure.py`
- `scripts/structure_rules.py`
- `scripts/structure_paths.py`
- `scripts/structure_baseline.py`
- `tests/test_check_structure.py`
- `tests/test_structure_baseline.py`
- `tests/test_structure_path_confinement.py`
- `.agents/skills/project-structure/SKILL.md`
- `.agents/skills/quality-gate/SKILL.md`
- `.agents/skills/quality-gate/references/quality-gate.md`
- `.agents/skills/dev-workflow/references/dev-workflow.md`
- `CHANGELOG.md`
- `plans/20260716-issue93-structure-budget-ratchet.md`

## Source-of-truth chain

| Stage | Upstream artifact | Downstream consumer | Identity / authority |
| --- | --- | --- | --- |
| Baseline discovery | `resolve_baseline_path()` in `scripts/structure_baseline.py` | `main()` in `scripts/check_structure.py` | Deterministic default path `.agents/structure-baseline.json` resolved from `Path.cwd()`, or explicit `--baseline PATH`; no latest/newest/mtime discovery |
| Baseline schema | `BASELINE_SCHEMA_VERSION = 1`, `BASELINE_TOP_KEYS`, `BASELINE_ENTRY_KEYS`, `KNOWN_RULES` constants in `scripts/structure_baseline.py` | `load_baseline_entries`, `validate_baseline_entries` (same module) | Exact key-set and rule-name matching; any deviation is `malformed-schema`/`unknown-rule`, never coerced |
| Canonical limits | `args.max_source_lines` / `args.max_entrypoint_lines` / `args.max_inline_test_lines` (CLI defaults defined via `parse_args()` in `scripts/check_structure.py`, consumed via `RULE_LIMIT_ARG` mapping in `scripts/structure_baseline.py`) | `_entry_problem()` threshold-mismatch check | A baseline entry's `limit` must equal the live canonical limit at validation time, not a value frozen at authoring time |
| Findings | `check_file()` in `scripts/structure_rules.py` | `reconcile_baseline()` in `scripts/structure_baseline.py` | Findings and baseline entries are matched on `(rule, cwd-relative path)`, independent of git history, mtimes, or filename ordering |
| Scanned scope | `collect_files()` in `scripts/structure_rules.py`, converted to cwd-relative posix by `main()` in `scripts/check_structure.py` via `structure_baseline.to_repo_relpath` | `reconcile_baseline()` in `scripts/structure_baseline.py` | An unmatched baseline entry is judged `stale-baseline` only if its path is in this invocation's `scanned_paths`; otherwise left neutral. The full default (no-args) scan's scope is every git-tracked source file, so it still detects every stale entry repo-wide |
| Path confinement | `normalize_entry_path()` / `path_escape()` in `scripts/structure_paths.py`, called once per entry from `scripts/structure_baseline.py`'s `_parse_baseline_entry` | `load_baseline_entries`, `validate_baseline_entries`, `reconcile_baseline` (in `structure_baseline.py`) | A baseline `path` must be repo-root-relative, non-absolute, `..`-free, and free of symlinks anywhere in its path chain (leaf or parent directory), checked against `Path.cwd().resolve()`; any violation is `path-escape` and never reaches duplicate detection or finding-matching |
| Skill/gate docs | `project-structure/SKILL.md`, `quality-gate/SKILL.md` + reference, `dev-workflow` reference | Agents running the workflow | All three name the same flag, default path, and outcome categories as the source; none refer to internal file layout, so the module split does not change the documented contract |

## Generated argv replay

| step_id | execution_location | command_argv | required environment | expected artifact kind | expected artifact path | continue_on / stop_on | claim gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| check-structure-no-baseline | repo root | `python3 scripts/check_structure.py <touched files>` | Python 3 stdlib | text or `--json` findings list | stdout | stop on exit 1/2 unless waived | Unbaselined behavior unchanged from pre-#93 |
| check-structure-with-baseline | repo root | `python3 scripts/check_structure.py <touched files>` (baseline auto-discovered at `.agents/structure-baseline.json`) | Python 3 stdlib + baseline file present | `{findings, accepted_debt, baseline_errors, baseline_path}` (`--json`) or equivalent text | stdout | stop on exit 1/2 | `accepted_debt` is debt, never reported as clean |
| check-structure-explicit-baseline | repo root | `python3 scripts/check_structure.py <touched files> --baseline PATH` | Python 3 stdlib + `PATH` must exist | same as above | stdout | stop on exit 2 if `PATH` missing (usage error) | Explicit override never silently falls back to the default path |
| test-unit | repo root | `python3 -m unittest tests.test_check_structure tests.test_structure_baseline tests.test_structure_path_confinement` (or `make test-unit`) | Python 3 stdlib | unittest text report | stdout | stop on failure | Behavior claims backed by 34 passing tests (9 source-rule + 20 baseline + 5 path-confinement) |

## Artifact producer/consumer consistency

| Producer step | Produced artifact | Consumer step | Consumer argv | Identity fields that must match |
| --- | --- | --- | --- | --- |
| `check_file()` (`scripts/structure_rules.py`) | `Finding(rule, path, value, limit, action)` | `reconcile_baseline()` (`scripts/structure_baseline.py`) | in-process call, package- or direct-script-imported via the explicit `__package__` branch | `rule`, cwd-relative `path` |
| `load_baseline_entries()` (`scripts/structure_baseline.py`) | `list[BaselineEntry]` + `list[BaselineIssue]` (schema issues) | `validate_baseline_entries()` (same module) | in-process call | `rule`, `path`, `value`, `limit`, all four `BASELINE_ENTRY_KEYS` |
| `validate_baseline_entries()` (`scripts/structure_baseline.py`) | `usable` entries + `BaselineIssue` list (duplicate/missing-path/threshold-mismatch) | `reconcile_baseline()` (same module) | in-process call | Only entries that passed disk existence + threshold checks are used for matching |
| `collect_files()` (`scripts/structure_rules.py`) via `main()` (`scripts/check_structure.py`) | `scanned_paths: frozenset[str]` (cwd-relative posix, built with `to_repo_relpath`) | `reconcile_baseline()` (`scripts/structure_baseline.py`) | in-process call, passed as `reconcile_baseline`'s 4th positional argument | Must use the identical `to_repo_relpath` conversion the finding-lookup key uses, or scope and lookup could silently diverge |
| `reconcile_baseline()` (`scripts/structure_baseline.py`) | `blocking`, `accepted`, `issues` (regression/stale-baseline) | `main()` printer / `--json` (`scripts/check_structure.py`) | in-process call, imported via the explicit `__package__` branch | Exit code and printed category (`FINDING`/`ACCEPTED-DEBT`/`BASELINE-ERROR`) must agree with which of the three lists an item is in; an unmatched entry outside `scanned_paths` appears in none of the three |
| `main()` (`scripts/check_structure.py`) | stdout text or JSON, exit code 0/1/2 | Agent / `quality-gate` / `dev-workflow` | explicit CLI invocation from skill docs | Docs describe exactly these three output categories and these three exit codes; no doc claims a fourth |

## Run-set / target / workflow identity consistency

- Workflow identity: structure-budget checker, invoked identically whether or not a baseline is present, regardless of the fact that its implementation is now split across `scripts/structure_rules.py` (rule analysis), `scripts/structure_paths.py` (path normalization/confinement), `scripts/structure_baseline.py` (baseline reconciliation), and `scripts/check_structure.py` (CLI wiring). The invocation `python3 scripts/check_structure.py ...` is unchanged.
- Target identity: explicit file/directory arguments, or the default git-tracked source scan of `Path.cwd()`.
- Baseline identity: explicit `--baseline PATH`, or the deterministic default `.agents/structure-baseline.json` relative to `Path.cwd()` — never resolved by mtime, "latest", or filename globbing.
- Consistency status: pass. `resolve_baseline_path()` never falls back to searching for *some* baseline file; either the named default exists or `--baseline` was given and exists, or no baseline applies.
- Import-path identity: `check_structure.py` and `structure_baseline.py` resolve their sibling imports via an explicit `if __package__: ... else: ...` branch (not try/except), so the two supported invocation shapes (package-qualified, as tests use; direct-script, as every other caller uses) are both deterministic and neither shape can silently mask an unrelated `ImportError` — confirmed by inspection of both import sites (`structure_baseline.py` now also imports `structure_paths` via the same branch) and by the passing direct-script self-check (`python3 scripts/check_structure.py <all 7 touched .py files>` → `pass`).

## Controller / target-local execution-location table

| Step | Controller location | Target-local location | Status |
| --- | --- | --- | --- |
| `check_structure.py` invocation | Repository root of the repo being checked | Not applicable (single-process, no remote target) | pass |
| Baseline file read | Same repository root (`.agents/structure-baseline.json` or `--baseline PATH`) | Not applicable | pass |

## Deployment/runtime discovery assumptions

- Python 3 standard library only; no new dependencies were added (confirmed: across all four script modules, only `argparse`, `json`, `subprocess`, `sys`, `dataclasses`, `pathlib` are imported).
- No network access, git history, file mtimes, or filename ordering are read to resolve or validate a baseline — confirmed by inspection: `resolve_baseline_path`, `load_baseline_entries`, `validate_baseline_entries`, `reconcile_baseline`, and `to_repo_relpath` (all in `scripts/structure_baseline.py`) use only `Path.is_file()`, `Path.read_text()`, `json.loads()`, and `Path.cwd()`-relative string comparison; `normalize_entry_path`/`path_escape` (in `scripts/structure_paths.py`) use only `PurePosixPath`/`Path.is_symlink()`/`Path.resolve()`. `reconcile_baseline`'s new `scanned_paths` scope is likewise derived only from `collect_files()`'s already-established, git/mtime/network-independent file list, so the touched-file integration-bug fix does not introduce a new dependency.
- `git_tracked_source_files()` (unchanged, pre-existing, now in `scripts/structure_rules.py`) still uses `git ls-files` only for the *default, no-args* scan — this is unrelated to baseline resolution and was true before #93.

## Forbidden fallback checks

- No auto-generation or silent rewriting of a baseline (out of scope per task packet; not implemented — confirmed by inspection: no code path in `scripts/structure_baseline.py` or `scripts/check_structure.py` writes to a baseline path).
- No git-diff-only enforcement: reconciliation is state-based (current file content vs. current baseline entries), not diff-based.
- No coercion of a baseline entry with a wrong type, missing key, extra key, unknown rule, or boolean-for-int value into a usable entry — all such cases are `malformed-schema`/`unknown-rule` and fail closed rather than being partially accepted.
- No "latest baseline file" or directory-scan fallback when `--baseline PATH` is missing — that is an explicit usage error (exit 2), not a silent skip back to unbaselined behavior.
- No silent softening of `accepted_debt` into a "pass"/"clean" claim in text or JSON output, or in the updated skill docs.
- No try/except import fallback masking the direct-script vs. package-import distinction — both import sites use an explicit `if __package__:` branch instead, so a genuine `ImportError` in either branch cannot be silently swallowed by the other.
- No baseline path is ever trusted merely because it parses as valid JSON with the right keys: absolute paths, `..` traversal, and symlinks anywhere in the path chain (leaf or parent directory) are all rejected as `path-escape` (`scripts/structure_paths.py`'s `path_escape`) before the entry is used for duplicate detection or finding-matching — none of these can silently degrade into `accepted_debt` with exit 0 (confirmed by the 5 `PathConfinementTests` end-to-end subprocess tests in `tests/test_structure_path_confinement.py`, each asserting exit 1 and a `path-escape`/`duplicate-entry` diagnostic).
- No unmatched baseline entry is ever treated as if "not scanned" and "scanned but no longer breaches the rule" were the same fact: `reconcile_baseline` never guesses which one is true from the findings list alone (an unscanned file produces no `Finding`, indistinguishable on its own from a clean one) — it consults the explicit `scanned_paths` scope instead, so a partial, explicit-paths invocation can never falsely fail on an untouched file's valid debt, and a full default scan (whose scope is every tracked source file) can never silently skip a genuinely stale entry either (confirmed by `test_untouched_baseline_entry_is_neutral_on_partial_scan` and `test_full_default_scan_still_detects_stale_baseline_entry`, both in `tests/test_structure_baseline.py`).
- Scan scope is never conflated with document validity: `validate_baseline_entries()` (duplicate/missing-path/threshold-mismatch) and `_parse_baseline_entry()` (malformed-schema/unknown-rule/path-escape) run over every parsed entry before `scanned_paths` is even constructed in `main()`, so a defective entry can never be silently accepted, or silently left un-reported, merely because its file was outside this invocation's touched-files argument list — confirmed by `test_untouched_integrity_errors_fail_closed_unlike_stale_baseline`.

## Claim boundary checks

- `accepted_debt` means only "this exact finding was pre-approved as existing debt at this value/limit"; it is never described as resolved, clean, or a pass in source, tests, or docs.
- A `stale-baseline` issue on file-improvement means the baseline itself is now wrong and must be refreshed/removed by a maintainer; the tool never does this automatically (AC4 — confirmed by test `test_stale_baseline_when_file_improved_but_still_over_limit` and `test_stale_baseline_when_finding_fully_resolved`, both in `tests/test_structure_baseline.py`). This claim is bounded to entries within the current invocation's scanned scope: a baselined file not included in a partial, explicit-paths run is left neutral rather than judged either stale or accepted, and the claim "the full default scan still detects every stale entry repo-wide" is verified separately by `test_full_default_scan_still_detects_stale_baseline_entry`, not assumed from the partial-scan tests. Scope-boundedness applies only to this one `stale-baseline` sub-case ("no longer reproduces a finding"), never to `duplicate-entry`/`missing-path`/`threshold-mismatch`/`malformed-schema`/`unknown-rule`/`path-escape`, which are baseline-document defects checked against every parsed entry unconditionally and therefore always fail closed on both partial and full runs — confirmed by `test_untouched_integrity_errors_fail_closed_unlike_stale_baseline`, which shows an untouched `missing-path` entry and an untouched `threshold-mismatch` entry both still failing closed on an unrelated single-touched-file invocation, alongside a coexisting valid untouched entry that stays neutral.
- "No baseline present" is claimed to be behavior-identical to pre-#93 checker output; verified by `test_no_baseline_present_preserves_text_output` and `test_no_baseline_present_preserves_json_output_shape` (in `tests/test_structure_baseline.py`), and by running the full pre-existing 9-test suite in `tests/test_check_structure.py` unchanged (all pass).
- The self-referential finding this change caused (`scripts/check_structure.py` and `tests/test_check_structure.py` both temporarily exceeded `source-file-lines` while the baseline feature was being added) was resolved by responsibility-based module/test splits, followed by path-confinement, partial-scan, and global-integrity review fixes. Final independent review also closed two schema/CLI edges: empty explicit `--baseline` values remain explicit usage errors, and schema `version` accepts only the exact non-boolean integer `1`. Confirmed: `python3 scripts/check_structure.py scripts/check_structure.py scripts/structure_rules.py scripts/structure_paths.py scripts/structure_baseline.py tests/test_check_structure.py tests/test_structure_baseline.py tests/test_structure_path_confinement.py` reports `pass (7 source files checked)`, with all files under 400 logical lines (208 / 245 / 61 / 380 / 107 / 383 / 110).
- A baseline entry can never suppress a finding for a path outside the repository: `path-escape` rejection happens once, at parse time, before an entry is ever compared against a `Finding`; an external or symlink-escaping path always produces a blocking baseline error (exit 1), never `accepted_debt` (exit 0) — this closes the specific fail-open the security review reported and is claimed no more broadly than that (this change does not, and was not asked to, constrain `--baseline PATH` itself or the explicit-CLI-source-path scan in `scripts/structure_rules.py`, both of which continue to accept any path the caller names, exactly as before #93).
- "Every unrelated touched-file invocation must not fail because of an untouched baseline entry" is claimed no more broadly than the exact scenario reported: a valid baseline entry for a file outside `scanned_paths` is neutral for *that invocation only*; it is not exempted from ever being validated — the next invocation whose scope includes it (an explicit re-check, or CI's full default scan) still validates it fully, so debt cannot escape detection permanently, only for the duration of a scan that never looked at it.

## CLI/schema identity cross-check (AC9)

Re-verified after the module split by grepping `--baseline`, the default path `.agents/structure-baseline.json`, the schema `version: 1`, and every `_issue(...)` kind literal across all seven touched Python files plus the docs:

- Source, baseline schema (`scripts/structure_baseline.py`): `DEFAULT_BASELINE_PATH = ".agents/structure-baseline.json"`, `BASELINE_SCHEMA_VERSION = 1`. `BaselineIssue.kind` values produced by `_issue()` call sites: `duplicate-entry`, `malformed-schema`, `missing-path`, `path-escape`, `regression`, `stale-baseline`, `threshold-mismatch`, `unknown-rule` (8 kinds, confirmed by `grep -A1 '_issue(' scripts/structure_baseline.py | grep -oE '"[a-z-]+"' | sort -u`).
- Source, path confinement (`scripts/structure_paths.py`): `normalize_entry_path`/`path_escape` produce the `path-escape` detail strings that `structure_baseline.py`'s `_parse_baseline_entry` wraps into the `path-escape` `BaselineIssue`; the kind literal itself lives only in `structure_baseline.py`, not duplicated in `structure_paths.py`.
- Source, CLI wiring (`scripts/check_structure.py`): imports `DEFAULT_BASELINE_PATH` from `structure_baseline` (via the explicit `__package__` branch) rather than redefining it, so there is exactly one place the default path constant lives; `--baseline` flag with `metavar="PATH"`.
- Tests (`tests/test_structure_baseline.py` + `tests/test_structure_path_confinement.py`): both define `DEFAULT_BASELINE_RELPATH = ".agents/structure-baseline.json"` and author baseline documents with `"version": 1` (small, intentional duplication of test fixtures — see plan Decision log); explicit override, empty explicit path, and missing explicit path are covered; schema-version tests reject missing, boolean, and floating-point values; one test per baseline-error kind lives in `test_structure_baseline.py` except `path-escape`, which has its 4 scenario tests plus the alias-duplicate test in `test_structure_path_confinement.py`.
- Docs (`project-structure/SKILL.md`, `quality-gate/SKILL.md` + reference, `dev-workflow` reference, `CHANGELOG.md`): all cite the same default path and `--baseline PATH` flag; none reference internal module layout, so no doc update was needed for either split itself — only `CHANGELOG.md`'s test-location sentence needed correcting to name both `tests/test_structure_baseline.py` and `tests/test_structure_path_confinement.py`, since that was a specific file-path claim.

No mismatch found after re-verification. This is the basis for the `submit` decision below.

## Findings

0 findings.

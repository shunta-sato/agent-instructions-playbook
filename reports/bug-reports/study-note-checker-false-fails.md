# Bug Report (RCA): Study-note checker false failures

- Title: Study-note checker false failures for valid generic packs
- Symptom (actual behavior): The checker could fail valid study-note packs when frontmatter existed without tags, when textbook notes used non-English or non-canonical section labels, or when wikilinks used root-relative paths.
- Expected behavior: Mechanical checks should fail only on deterministic safety issues and should not replace semantic learning review.
- Severity/Impact: P1 for study-note pack publication because valid packs could be blocked by false failures.
- Environment (versions, platform, config): Repository Python checker invoked with `python3 .agents/skills/textbook-quality-gate/scripts/check_study_notes.py` in `shared-mechanical-only` and `textbook-full-gate` modes.
- Detection (how it was found): Code review identified false-fail risks not covered by schema validation.

## Reproduction

- Steps to reproduce:
  1. Run shared mechanical checks against a synthetic note with frontmatter but no tag convention.
  2. Run shared mechanical checks against a synthetic pack with `[[patterns/example-note]]` linking to `<note-root>/patterns/example-note.md`.
  3. Run textbook full gate against a synthetic long-enough textbook note that does not use fixed English section labels.
- Minimal repro (if available): Added to `make test-unit` using synthetic temporary Markdown roots.
- Frequency: Deterministic for affected input shapes before the fix.

## Evidence

- Logs / stack trace / metrics / traces: Before the fix, frontmatter-only notes failed with `pack convention appears to require tags but none were found`; textbook notes without fixed English labels failed with `missing detectable textbook learning sections`.
- What changed recently (if known): The checker was introduced in the prior study-note Skills commit.

## Root Cause Analysis (Five Whys)

1. Why #1: Valid packs failed because the checker treated heuristic signals as mandatory failures. Evidence: fixed English section labels and frontmatter-driven tag requirement produced non-zero exits.
2. Why #2: The checker conflated semantic contract detection with deterministic mechanical checks. Evidence: missing textbook sections were reported as hard failures rather than requiring semantic review.
3. Why #3: Pack conventions were inferred from per-file frontmatter rather than explicit options or pack-level tag usage. Evidence: any frontmatter caused a tag-required failure.
4. Why #4: Wikilink target indexing did not include all provided note-root-relative path forms. Evidence: the target builder did not receive the note roots.
5. Why #5 (root cause): Initial smoke tests covered only the happy path and did not include false-positive near misses for frontmatter-only notes, root-relative links, or non-canonical textbook headings.

## Fix

- What changed (summary): Added `--require-tags`, made frontmatter alone non-failing, indexed wikilink targets relative to each note root, downgraded mechanically undetected textbook sections to warnings, relaxed thin-note heuristics, and added smoke/eval coverage for false-positive cases.
- Why this fix addresses the root cause: The checker now keeps semantic uncertainty in semantic review, makes tag requirements explicit, and resolves links using provided roots.

## Verification

- Tests run: `make test-unit`, repository validation commands, privacy scan, and `make verify`.
- Repro re-run result: Synthetic frontmatter-only, root-relative wikilink, and non-fixed-heading textbook cases pass.
- Tooling run (if relevant): `python scripts/validate_skills.py`, `python scripts/validate_skill_trigger_evals.py`, `python scripts/report_skill_inventory.py --check --format text`, `python scripts/generate_agent_index.py --check`, `git diff --check`.

## Prevention

- Prevent: `make test-unit` now includes synthetic false-positive regressions for frontmatter-only notes, root-relative wikilinks, and non-fixed-heading textbook notes.
- Detect: Trigger evals now include mechanical-only near-miss cases for frontmatter without tags and root-relative wikilinks.
- Mitigate: `textbook-quality-gate` now states that deterministic checks must not replace semantic review.
- Follow-up tasks (with owners / tracking IDs if available): None.

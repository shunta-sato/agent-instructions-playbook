# Skill Set Review — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Review every repo-local Agent Skill against April 2026 guidance for Codex, GitHub Copilot, and the Agent Skills specification.
- Convert the current broad playbook collection into a smaller, sharper, more evaluable skill set.
- Remove, merge, or rewrite skills when doing so improves trigger precision, context efficiency, and real task outcomes.

## Scope

### In scope
- Audit all 38 skills under `.agents/skills`.
- Score each skill for structure, trigger clarity, scope coherence, progressive disclosure, overlap, and eval readiness.
- Recommend keep / rewrite / merge / delete for each skill.
- Implement safe structural improvements after the audit, starting with low-risk consolidation and metadata fixes.

### Out of scope / non-goals
- Rewriting every reference document in one pass.
- Claiming a skill improves outcomes without eval evidence.
- Reintroducing `.github/skills` mirrors.
- Packaging this repository as a plugin during this pass.

## Constraints / Quality targets

- Compatibility: preserve `.agents/skills` as the single Codex/Copilot-compatible repo skill path.
- Quality target: descriptions must be precise enough for implicit activation and explicit enough to avoid near-miss false positives.
- Context target: keep `SKILL.md` concise; detailed reusable content belongs in `references/`, `templates/`, `assets/`, or scripts.
- Evaluation target: every retained core skill should have at least trigger-eval examples or explicit eval criteria by the end of the review program.
- Safety: delete or merge only when replacement behavior is clear and docs/index/CI are updated.

## Context & Orientation

- Current skill count: 38.
- Current validation: `python scripts/validate_skills.py` passes.
- Current index: `python scripts/generate_agent_index.py --check` passes.
- Relevant sources checked:
  - OpenAI Codex Agent Skills and customization docs.
  - GitHub Copilot agent skills docs.
  - Agent Skills specification, best practices, description optimization, evaluation, and script guidance.
  - 2026 benchmark papers: SkillsBench, SWE-Skills-Bench, SkillLearnBench.

## Review Rubric

Score each dimension 0-3.

- **Spec**: valid name/frontmatter/body; current validator passes; no non-standard fields.
- **Trigger**: description states when to use and when not to use; avoids broad always-trigger phrasing unless intentionally mandatory.
- **Scope**: one coherent job; not a vague quality topic with no concrete workflow.
- **Progressive disclosure**: `SKILL.md` has core procedure only; references are conditional and one level deep.
- **Actionability**: tells the agent what to do, what output/artifact to produce, and how to verify.
- **Overlap**: clear relationship to neighboring skills; no redundant trigger surface.
- **Eval readiness**: realistic should-trigger / should-not-trigger examples or deterministic artifact checks can be added.

Decision labels:

- **Keep**: good enough; only minor edits.
- **Rewrite**: valuable job, but trigger/procedure/reference split needs substantial edits.
- **Merge**: useful content, but not independently coherent enough as a skill.
- **Delete**: low value, duplicates another skill, or encourages broad/generic behavior.

## Milestones

1. Build latest-knowledge rubric and local inventory.
2. Audit all skill metadata and classify the collection.
3. Identify first-pass safe changes.
4. Implement the first pass and regenerate/validate.
5. Record remaining second-pass work for skills that need deeper domain rewrites or evals.

## Progress (WBS)

- [x] (P0) Gather April 2026 skill guidance — deliverable: rubric above — verify: citations in final response.
- [x] (P1) Produce full 38-skill audit table — deliverable: `reports/skillset-review-20260424.md` — verify: every skill has a decision label.
- [x] (P2) Implement safe first-pass improvements — deliverable: edited skills/docs/scripts — verify: validator/index checks pass.
- [x] (P3) Record deeper follow-ups — deliverable: prioritized backlog in the report — verify: clear next actions.
- [x] (P4) Implement consolidation passes — deliverable: active skill count reduced and references preserved — verify: validator passes.
- [x] (P5) Tighten broad trigger surfaces — deliverable: revised `observability`, `error-handling`, `code-readability`, `uidesign-orchestrator` descriptions plus expanded eval seeds — verify: trigger eval validator passes.
- [x] (P6) Commit changes if requested after review — deliverable: git commit — verify: clean status.

## Surprises & Discoveries

- 2026-04-24: SkillsBench reports curated skills help on average but can hurt; this makes eval-readiness and near-miss trigger testing a review requirement, not a nice-to-have.
- 2026-04-24: SWE-Skills-Bench reports many public SWE skills show no pass-rate improvement and sometimes high token overhead; generic quality skills need especially strict scrutiny.
- 2026-04-24: SkillLearnBench suggests iterative external feedback is more reliable than self-feedback-only skill generation; this review should preserve evidence loops and avoid speculative rewrites without usage data.
- 2026-04-24: The current set validates, but 38 active skills creates a broad trigger surface. The clearest consolidation wins are thin platform adapters and template-authoring skills, not evidence-producing workflows.
- 2026-04-24: Consolidation reduced the active skill count from 38 to 25 while preserving adapter/template/requirements/reference content under parent skills.
- 2026-04-24: Trigger eval seeds expanded from 25 to 35 cases, with emphasis on near-miss negative prompts for broad skills.

## Decision log

- 2026-04-24: Review before deleting.
  - Options considered: immediately delete broad/overlapping skills; write a full audit first.
  - Chosen: full audit first.
  - Consequences: slower initial pass, lower risk of losing useful domain knowledge.
- 2026-04-24: Treat eval readiness as a first-class criterion.
  - Options considered: score only structure/clarity; include benchmark-informed utility risk.
  - Chosen: include eval readiness.
  - Consequences: skills with no measurable output are likely rewrite/merge candidates.
- 2026-04-24: Defer hard deletions until replacement mapping is explicit.
  - Options considered: delete thin adapters immediately; record merge plan first and leave behavior intact.
  - Chosen: record merge plan first, apply only safe metadata fixes.
  - Consequences: lower risk now; follow-up pass should remove merged directories after evals/checks exist.
- 2026-04-24: Merge thin adapters and template/requirements parents after audit.
  - Options considered: leave 38 skills and only document merge plan; consolidate now with replacement mappings.
  - Chosen: consolidate now for platform adapters, template-authoring skills, requirements skills, and maintainability/boundary skills.
  - Consequences: active trigger surface drops to 25 skills; old explicit invocations must be replaced by parent skills.
- 2026-04-24: Tighten broad skills by trigger contract first.
  - Options considered: rewrite references deeply; rewrite frontmatter/When-to-use sections and add eval near-misses.
  - Chosen: tighten trigger contracts first.
  - Consequences: lower context churn, clearer implicit activation behavior, and a measurable seed set for future rewrites.

## Handoff

- Current branch / commit: `main`, latest commit `a63f0ab`.
- What is done: latest knowledge gathered, review rubric created, initial plan written.
- What is done: full 38-skill audit table added in `reports/skillset-review-20260424.md`; Tone & Manner metadata fixes applied; consolidation implemented; trigger eval seeds added and expanded; broad skill descriptions tightened.
- What is not done: automated LLM dispatch scoring.
- How to run:
  - `python scripts/validate_skills.py`
  - `python scripts/generate_agent_index.py --check`
- Known risks / open questions:
  - Some skills encode domain knowledge from prior work; deletion should happen only after replacement mapping is explicit.
  - UI/Tone skills may be intentionally specialized and should not be collapsed merely because names are similar.
- Next 1-3 steps:
  1. Generate inventory with metadata, references, templates, and line counts.
  2. Review clusters and assign keep/rewrite/merge/delete labels.
  3. Create the audit report.

## Validation & Acceptance

- AC1: Every skill has a review row.
  - Verification: audit report includes 38 rows.
- AC2: Proposed removals/merges include replacement behavior.
  - Verification: report has explicit target skill or deletion rationale.
- AC3: Any implemented changes preserve validation.
  - Verification: validator, trigger-eval validator, and index checks pass.

## Outcomes & Retrospective

- What shipped / merged: 38 active skills reduced to 25; thin platform adapters, template-authoring skills, requirements skills, and architecture/modularity review skills merged into parent skills; trigger eval seed validator added.
- What went well: subagent split kept write scopes disjoint and preserved deleted-skill content as parent references.
- What went wrong: `make verify` remains unavailable because the template Makefile is intentionally uninitialized.
- Follow-ups / tech debt tickets: keep expanding trigger evals, decide whether `uidesign-orchestrator` stays active after usage data, add a true LLM dispatch eval runner when the model/tooling target is stable.

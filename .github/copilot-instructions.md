# GitHub Copilot Repository Instructions

These instructions complement `AGENTS.md` and the playbooks under `.github/` and `.agents/`.

## Primary goal

Produce changes that are easy to understand and safe to change.

## Always do this

1. Read the relevant code and tests before editing.
2. Write a short *Change Brief* (intent, inputs/outputs, constraints, assumptions).
3. Prefer minimal diffs that reduce reading time.
4. If runtime behavior changes, add observability signals (logs/metrics/traces) so failures are diagnosable.
5. Verify with the canonical commands in `COMMANDS.md` (build, format/lint, tests).
   - If you cannot run them, say why and provide a reproducible procedure.
6. If `COMMANDS.md` contains `<fill>`, do not guess project commands or proceed with normal implementation until initialization is completed via `/initialize` or `$project-initialization`.
7. Consider initialization complete only after `make verify` succeeds; only then may `<fill>` be removed from `COMMANDS.md`.

## Use the on-demand prompts

Use these prompt files to keep behavior consistent:

- `/dev-workflow` — end-to-end change workflow
- `/quality-gate` — final checklist before finishing
- `/review-readability` — readability review
- `/review-modularity` — cohesion/coupling/boundaries review
- `/review-antipatterns` — new/worsened smells & anti-patterns review
- `/write-requirements` — requirement/spec writing workflow
- `/bug-report` — evidence-based Bug Report (RCA) for bugfix/regression/flaky/incidents
- `/uiux-core` — UI/UX design and review workflow with deterministic UIUX Pack outputs
- `/uidesign-flow` — tone-and-manner → tokens → previews → deterministic UIDesign Pack
- `/ui-verify` — snapshot/screenshot verification workflow for UI visual changes
- `/tonemana-catalog` — Tone & Manner catalog generation workflow with seven default patterns
- `/tonemana-apply` — Tone & Manner pack apply workflow for UIUX references
- `/uidesign-orchestrator` — End-to-end orchestration (uiux → tonemana → uidesign previews)

## Language-specific highlights

- **C++ headers (`.hpp`)**: Doxygen comments are required for *all declarations*, including `private` members.
- **C++ sources (`.cpp`)**: comments must explain intent / assumptions / pitfalls (not restate code), and replace “magic values” with named constants or enums.

(See `.github/instructions/cpp.instructions.md` for the full rules.)

When fixing bugs/regressions/flakes/incidents, run `/bug-report` and keep facts separate from assumptions.

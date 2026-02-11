# GitHub Copilot Repository Instructions

These instructions complement `AGENTS.md` and the playbooks under `.github/` and `.codex/`.

## Primary goal

Produce changes that are easy to understand and safe to change.

## Always do this

1. Read the relevant code and tests before editing.
2. Write a short *Change Brief* (intent, inputs/outputs, constraints, assumptions).
3. Prefer minimal diffs that reduce reading time.
4. If runtime behavior changes, add observability signals (logs/metrics/traces) so failures are diagnosable.
5. Verify with the canonical commands in `COMMANDS.md` (build, format/lint, tests).
   - If you cannot run them, say why and provide a reproducible procedure.

## Use the on-demand prompts

Use these prompt files to keep behavior consistent:

- `/dev-workflow` — end-to-end change workflow
- `/quality-gate` — final checklist before finishing
- `/review-readability` — readability review
- `/review-modularity` — cohesion/coupling/boundaries review
- `/review-antipatterns` — new/worsened smells & anti-patterns review
- `/write-requirements` — requirement/spec writing workflow
- `/bug-report` — evidence-based Bug Report (RCA) for bugfix/regression/flaky/incidents

## Language-specific highlights

- **C++ headers (`.hpp`)**: Doxygen comments are required for *all declarations*, including `private` members.
- **C++ sources (`.cpp`)**: comments must explain intent / assumptions / pitfalls (not restate code), and replace “magic values” with named constants or enums.

(See `.github/instructions/cpp.instructions.md` for the full rules.)

When fixing bugs/regressions/flakes/incidents, run `/bug-report` and keep facts separate from assumptions.

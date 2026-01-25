# GitHub Copilot Repository Instructions

These instructions complement `AGENTS.md` and the Codex skills under `.codex/skills/`.

## Primary goal

Produce changes that are **easy to understand and safe to change**.

## Always do this

1. Read the relevant code and tests before editing.
2. Write a short *Change Brief* (intent, inputs/outputs, constraints, assumptions).
3. Prefer minimal diffs that reduce reading time.
4. Verify with the project’s commands:
   - build: `<fill>`
   - format/lint: `<fill>`
   - tests: `<fill>`

## Use the on-demand prompts

Use these prompt files to keep behavior consistent:

- `/dev-workflow` — end-to-end change workflow
- `/quality-gate` — final checklist before finishing
- `/review-readability` — readability review
- `/review-modularity` — cohesion/coupling/boundaries review
- `/write-requirements` — requirement/spec writing workflow

## Language-specific highlights

- **C++ headers (`.hpp`)**: Doxygen comments are required for *all declarations*, including `private` members.
- **C++ sources (`.cpp`)**: comments must explain **intent / assumptions / pitfalls** (not restate code), and replace “magic values” with named constants or enums.

(See `.github/instructions/cpp.instructions.md` for the full rules.)

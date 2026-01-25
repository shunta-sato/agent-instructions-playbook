# dev-workflow

Use this prompt to execute a consistent end-to-end workflow for any change in this repository.

## Workflow

1) Read
- Identify entry points and impacted code paths.
- Skim relevant tests (or add a reproduction plan if none exist).

2) Change Brief (1 paragraph)
- Intent, inputs/outputs, constraints, assumptions, and success criteria.

3) Plan (3–5 steps)
- Keep one purpose per change.

4) Implement
- Prefer minimal diffs.
- Preserve readability and modularity.

5) Verify
- Provide the exact commands to run: build / format-lint / tests.
- If you cannot run commands, explain what to run and what you expect to see.

6) Finish with Self Review
- Readability: naming, intent-focused comments, control flow, tests.
- Modularity: cohesion/coupling/boundaries.
- Documentation: update docs when behavior/spec changes.

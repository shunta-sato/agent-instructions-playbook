# initialize

Use this prompt to initialize a freshly copied repository template.

## Goals

1) Standardize canonical commands behind `make <target>` wrappers.
2) Keep `COMMANDS.md` as the machine-readable initialization gate.
3) Remove `<fill>` only after verified execution.

## Required flow

1. Inspect project evidence (lockfiles, CI, scripts, build/test tooling).
2. Ask only the minimum missing questions (up to 5).
3. Update `Makefile` targets (`build-debug`, `build-release`, `format`, `lint`, `analysis`, `test-unit`, `test-integration`, `verify`).
4. Update `COMMANDS.md` command sections to `make ...` commands while keeping:
   - `verified by agent: <fill>`
   - `verification command: make verify`
5. Run `make verify`.
6. Gate:
   - If `make verify` succeeds: replace `<fill>` with `yes (YYYY-MM-DD)`.
   - If `make verify` fails: keep `<fill>` and document failure reasons + next steps in `INIT_REPORT.md` (or `COMMANDS.md` notes).

## Safety

- Do not run sudo directly.
- For privileged setup, generate a reviewable script (e.g., `tools/bootstrap/install.sh`) and ask the user to execute it.
- Do not use `curl | bash`.

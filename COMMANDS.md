# COMMANDS.md — canonical build/test/lint commands

## Initialization verification
- verified by agent: <fill>
- verification command: make verify
- note: this placeholder must remain until `make verify` succeeds.

## Build
- build (debug): make build-debug
- build (release): make build-release

## Format / Lint / Static analysis
- format: make format
- lint: make lint
- static analysis: make analysis

## Tests
- unit tests: make test-unit
- integration/e2e tests: make test-integration

## Notes
- If a command differs between local and CI, document both.
- If a command is intentionally unavailable, explain the alternative.
- If `make verify` fails during initialization, keep the verification placeholder and document the failure plus next steps in `INIT_REPORT.md` (or append to this file).

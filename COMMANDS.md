# COMMANDS.md — canonical build/test/lint commands

## Initialization verification
- verified by agent: yes (2026-05-30)
- verification command: make verify
- note: initialized for this repository after `make verify` succeeded.

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

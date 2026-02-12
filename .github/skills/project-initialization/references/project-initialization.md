# project-initialization reference

## Canonical initialization contract

- Keep a single `<fill>` marker in `COMMANDS.md` under `Initialization verification`.
- Use `make <target>` as the canonical command entry points.
- Treat `make verify` as the final gate.

## Required COMMANDS.md shape

```md
## Initialization verification
- verified by agent: <fill>
- verification command: make verify
- note: `<fill>` must remain until `make verify` succeeds.
```

All operational commands should already be `make ...` lines (no `<fill>` in build/lint/test sections).

## Success path example

1. Configure Makefile targets with real project commands.
2. Run `make verify` and confirm exit code 0.
3. Update:

```md
- verified by agent: yes (2026-01-15)
```

4. Confirm `rg "<fill>" COMMANDS.md` returns no output.

## Failure path example

If `make verify` fails:
- Keep `- verified by agent: <fill>` unchanged.
- Record failures and remediation steps, e.g.:

```md
## Initialization failure notes
- 2026-01-15: `make verify` failed at `make lint` (missing dependency `ruff`).
- Next step: install dev dependencies with `pip install -r requirements-dev.txt` and rerun `make verify`.
```

Or place the same content in `INIT_REPORT.md`.

## Why this gate exists

Removing `<fill>` means commands are not just documented; they were executed successfully through `make verify`.

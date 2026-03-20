# Canonical usage example for {{LIBRARY_OR_API_NAME}}

> Template example. Replace placeholders before production use.

## Happy path

1. Install dependency:

```bash
{{INSTALL_COMMAND}}
```

2. Initialize client/tool:

```text
{{CANONICAL_IMPORT_OR_INIT}}
```

3. Execute canonical operation:

```bash
{{CANONICAL_COMMAND_OR_CODE}}
```

4. Verify output:

```bash
{{VERIFY_COMMAND}}
```

Expected signal: `{{SUCCESS_SIGNAL}}`.

## Failure path (required)

Scenario: `{{FAILURE_SCENARIO}}`.

- Trigger signal: `{{COMMON_FAILURE_SIGNAL}}`
- Recovery step: `{{RECOVERY_ACTION}}`
- Evidence to keep:
  - command output with timestamp
  - relevant log field `{{LOG_FIELD_1}}`
  - retry/abort decision rationale

## Notes

- Replace all placeholders.
- Keep this example aligned with `references/api-cli-summary.md`.

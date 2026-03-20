# {{LIBRARY_OR_API_NAME}} API/CLI Summary

> Template file. Replace all `{{...}}` placeholders.

## 1) Scope and version policy

- Skill name: `{{SKILL_NAME}}`
- Covered dependency: `{{LIBRARY_OR_API_NAME}}`
- Supported version range: `{{VERSION_RANGE}}`
- Official docs: `{{OFFICIAL_DOC_URL}}`
- Non-goals (out of scope):
  - {{OUT_OF_SCOPE_1}}
  - {{OUT_OF_SCOPE_2}}

## 2) Setup and prerequisites

- Install:
  - `{{INSTALL_COMMAND}}`
- Runtime/env requirements:
  - `{{RUNTIME_REQUIREMENT_1}}`
  - `{{RUNTIME_REQUIREMENT_2}}`
- Auth/secrets model:
  - `{{AUTH_METHOD}}`
  - Never commit secrets; use `{{SECRET_SOURCE}}`

## 3) Canonical usage surface

- Init/import:
  - `{{CANONICAL_IMPORT_OR_INIT}}`
- Core operations:
  - Create/Send: `{{OPERATION_CREATE}}`
  - Read/Get: `{{OPERATION_READ}}`
  - Update/Apply: `{{OPERATION_UPDATE}}`
  - Delete/Cleanup: `{{OPERATION_DELETE}}`
- Required flags/options:
  - `{{REQUIRED_FLAG_1}}`

## 4) Error handling and retries

- Common failure signal: `{{COMMON_FAILURE_SIGNAL}}`
- Retryable categories:
  - {{RETRYABLE_CASE_1}}
- Non-retryable categories:
  - {{NON_RETRYABLE_CASE_1}}
- Safe defaults:
  - `{{SAFE_DEFAULT}}`

## 5) Observability / verification

- Verification command:
  - `{{VERIFY_COMMAND}}`
- Expected success signal:
  - `{{SUCCESS_SIGNAL}}`
- Minimum logs/metrics to capture:
  - `{{LOG_FIELD_1}}`
  - `{{METRIC_1}}`

## 6) CUSTOMIZATION CHECKLIST

- [ ] No org-specific URLs remain.
- [ ] No real secret names or key formats remain.
- [ ] Version range is explicit and testable.
- [ ] Canonical flow has both success and failure handling.
- [ ] Gotchas include Trigger/Correction/Evidence.

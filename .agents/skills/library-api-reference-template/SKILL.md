---
name: library-api-reference-template
description: "Template skill for library/CLI/SDK usage references. Trigger when implementation depends on external APIs and you need canonical usage, version constraints, gotchas, and copy-ready org-neutral placeholders."
metadata:
  short-description: Library/API reference template
---

## Purpose

Use this template to create a reusable reference skill for a specific library, CLI, or SDK.

It provides a consistent package (`SKILL.md` + `references/` + `examples/`) that other repos can copy and customize without leaking org-specific details.

## When to use

Use this skill when:

- A task depends on third-party APIs/CLI/SDK behavior.
- Correct usage requires version-specific notes or gotcha handling.
- You want deterministic, canonical usage snippets instead of ad-hoc guidance.
- You are onboarding a new dependency and want a team-wide “single source of truth”.

## How to use

1) Duplicate this template directory and rename it to a concrete skill name.

2) Replace placeholders everywhere:

- `{{SKILL_NAME}}`
- `{{LIBRARY_OR_API_NAME}}`
- `{{VERSION_RANGE}}`
- `{{OFFICIAL_DOC_URL}}`
- `{{INSTALL_COMMAND}}`
- `{{VERIFY_COMMAND}}`
- `{{CANONICAL_IMPORT_OR_INIT}}`
- `{{COMMON_FAILURE_SIGNAL}}`
- `{{SAFE_DEFAULT}}`

3) Fill `references/api-cli-summary.md` first:

- Supported versions / compatibility policy
- Required setup / auth / environment
- Canonical command/API surfaces
- Error taxonomy and recovery patterns
- Security and data-handling constraints

4) Fill `examples/canonical-usage.md` with at least one runnable or copy-ready flow.

5) Add or update Gotchas using the repository rule:

- Trigger: concrete failure pattern
- Correction: do X instead of Y
- Evidence: output/artifact proving correction

6) Confirm discoverability:

- Skill exists under `.agents/skills/<name>`
- Mirror is updated under `.github/skills/<name>`
- Catalog/index generation has been run

## Gotchas

- **Common pitfall:** implementing from outdated blog snippets instead of API specifications.  
  **Instead:** first lock version + official docs in `references/api-cli-summary.md`, then implement from that.
- **Common pitfall:** providing only a minimal happy-path sample with no failure handling.  
  **Instead:** include one failure case in the canonical example (auth expiration/rate limit/timeout, etc.).
- **Common pitfall:** leaving org-specific URL / token names / secret formats in templates.  
  **Instead:** convert to placeholders and verify replacement gaps with `CUSTOMIZATION CHECKLIST`.

## Output expectation

When you instantiate this template in another repo, include:

- Which placeholders were replaced
- Supported version range
- Canonical commands/snippets added
- Gotchas and verification evidence

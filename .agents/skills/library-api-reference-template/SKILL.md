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

- **ありがち:** API 仕様ではなく古いブログ断片を参照して実装する。  
  **代わりに:** `references/api-cli-summary.md` の version + official docs を先に確定し、そこから実装する。
- **ありがち:** サンプルが最小 happy-path のみで、失敗時の扱いがない。  
  **代わりに:** canonical example に失敗ケース（認証切れ/レート制限/タイムアウト等）を 1 つ含める。
- **ありがち:** template に org 固有 URL / token 名 / secret 形式が残る。  
  **代わりに:** placeholder 化し、`CUSTOMIZATION CHECKLIST` で置換漏れを確認する。

## Output expectation

When you instantiate this template in another repo, include:

- Which placeholders were replaced
- Supported version range
- Canonical commands/snippets added
- Gotchas and verification evidence

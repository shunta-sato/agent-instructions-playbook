---
name: preflight-domain-template
description: "Template for authoring domain preflight skills that extract invariants, first docs/files, AGENTS.md proposals, .agent/ctx maps, test routing, approvals, reviewers, and handoff fragments. Use when creating or reviewing a new preflight-* domain skill, not during product implementation."
metadata:
  short-description: Domain preflight skill template
  visibility: template
  resources:
    - references/domain-agents-template.md
    - references/domain-ctx-template.md
    - references/domain-handoff-fragment-template.md
    - references/domain-trigger-eval-template.md
---

# Preflight Domain Template

## Purpose

Use this template to create domain preflight skills that support `preflight-engineering`.
Domain skills are helpers: they extract specialist invariants and routing inputs, then
return outputs that the orchestrator merges into AGENTS proposals, `.agent/ctx` maps,
skill routing, test routing, and the final handoff prompt.

This template does not implement product changes, read secret values, run migrations,
deploy, edit generated clients, or decide final implementation scope.

## How to use

1. Name the domain skill `preflight-<domain>` and keep the description trigger-specific.
   - Include the domain surface and explicit "Use before ..." conditions in the description.
   - Add negative trigger guidance when normal implementation should proceed without preflight.

2. Define the domain inspection scope.
   - List first docs, first files, generated paths, test paths, approval surfaces, and reviewer roles.
   - Mark facts as `confirmed`, `inferred`, or `unknown`.
   - Record secret-like paths as paths only; do not read values.

3. Extract human-auditable invariants.
   - Keep rules readable, for example `AUTH-LOG: Never log tokens, cookies, authorization headers, or credentials.`
   - Do not use opaque shorthand such as `A1 no toklog`.
   - Keep root `AGENTS.md` compact; move domain-specific rules into nested `AGENTS.md` proposals.

4. Return the common domain output contract exactly.
   - Use `references/domain-agents-template.md` for nested `AGENTS.md` proposals.
   - Use `references/domain-ctx-template.md` for `.agent/ctx/<domain>.md` proposals.
   - Use `references/domain-handoff-fragment-template.md` for final handoff fragments.
   - Use `references/domain-trigger-eval-template.md` when adding trigger eval coverage.

## Common Output Contract

```markdown
# Domain preflight result

## Domain

## Trigger reason

## Risk classification

## Confirmed facts

## Inferred facts

## Unknowns

## Domain invariants

## First docs

## First files

## Nested AGENTS.md proposal

## Agent context map proposal

## Skill routing additions

## Test routing

## Required approvals

## Required reviewers

## Handoff prompt fragment

## Remaining gaps
```

## Common Rules

- Do not implement product changes.
- Do not read secret values.
- Do not execute migrations or deploys.
- Do not edit generated clients.
- Do not over-compress security, public API, data, approval, or test-command rules.
- Keep root `AGENTS.md` short and stable.
- Put area-specific rules in nested `AGENTS.md` proposals.
- Keep `.agent/ctx/<domain>.md` as a compact work map, not a copied design doc.

## Self-review

- The skill is a helper for `preflight-engineering`, not a replacement.
- The output separates confirmed facts, inferred facts, and unknowns.
- The proposal names first docs/files and targeted tests before implementation starts.
- Approvals and reviewers are explicit when destructive, public API, security, billing, deploy, or data risks appear.
- Deferred or unimplemented domain surfaces are marked as gaps rather than silently omitted.

## Output expectation

- A new `preflight-<domain>` skill must return the Common Output Contract exactly, with every heading present (`Domain` through `Remaining gaps`).
- Domain invariants must be human-auditable rules, not opaque shorthand.
- Confirmed facts, inferred facts, and unknowns must be listed separately.
- Nested `AGENTS.md` and `.agent/ctx/<domain>.md` proposals must use the referenced templates, not free-form text.

---
name: playbook-template-authoring
description: "Use only when authoring or revising reusable, repo-neutral playbook/template skills for deployment, infrastructure operations, data fetching/analysis, or library/API reference guidance. Do not use for executing deployments, running infrastructure changes, doing one-off data analysis, or applying a library directly."
metadata:
  short-description: Reusable playbook/template authoring
---

## Purpose

Use this skill to create reusable playbook/template packages that other repositories can copy and specialize without embedding real secrets, production data, or org-specific endpoints.

This skill is for **authoring templates**, not for running the workflow described by a template.

## When to use

Use this skill when the requested output is a reusable skill, runbook template, checklist, report template, reference template, or canonical example for one of these modes:

- **Deployment:** CI/CD release playbooks with preflight, artifact integrity, smoke tests, staged rollout, verification, rollback triggers, and deployment reports.
- **Infrastructure operations:** day-2 ops runbooks with pre-check, dry-run, blast-radius controls, approval gates, phased apply, soak/cleanup, audit logs, and execution reports.
- **Data fetching/analysis:** repeatable analysis playbooks with scoped questions, source inventory, canonical keys, safe query patterns, limitations, and reproducibility notes.
- **Library/API reference:** reusable dependency references with version policy, setup/auth model, canonical commands/snippets, error handling, verification, and usage examples.

Do not use this skill for normal deploy requests, normal infrastructure operations, ordinary data analysis, or ordinary library/API implementation tasks unless the user is asking to author or revise the reusable template/playbook itself.

## How to use

1. Pick exactly the mode(s) needed and keep the package focused.
2. Start from the preserved artifact closest to that mode:
   - Deployment: `references/deployment-checklist.md`, `templates/deployment-report-template.md`
   - Infrastructure operations: `references/infrastructure-operations-checklist.md`, `templates/infrastructure-operations-report-template.md`
   - Data fetching/analysis: `references/data-fetching-analysis-checklist.md`, `templates/data-analysis-report-template.md`
   - Library/API reference: `references/library-api-cli-summary.md`, `examples/library-api-canonical-usage.md`
3. Replace concrete systems, hosts, credentials, team names, tickets, and data values with placeholders.
4. Preserve mode-specific guardrails:
   - Deployment: no production/destructive rollout without explicit approval; no full rollout before smoke/canary verification; rollback criteria must be concrete.
   - Infrastructure operations: no apply before pre-check and dry-run; destructive actions require checkpoint approval; broad scope requires phased execution and soak.
   - Data fetching/analysis: no extraction before the question, source inventory, canonical keys, join assumptions, and secret-handling model are explicit.
   - Library/API reference: no guidance from unspecified versions; include canonical setup, success verification, and at least one failure/recovery path.
5. Add live-discovery placeholders where external tools/systems appear: current command/interface source, schema/config path, connection/auth state, version/status output, artifact/log path, and evidence captured.
6. Add gotchas in this format: concrete failure pattern, corrective action, and evidence that proves the correction.
7. Check the finished template is repo-neutral, copy-ready, and explicit about its expected outputs.

## Output expectation

Return or create a reusable template package containing:

- A concise `SKILL.md` with narrow trigger wording and mode-specific workflow.
- Preserved or customized references, templates, and examples under `references/`, `templates/`, and `examples/`.
- A placeholder list or customization checklist.
- Explicit expected outputs, live-discovery evidence placeholders, approvals, and verification artifacts for the selected mode.
- Gotchas that prevent the common unsafe or non-reproducible failure modes for that mode.

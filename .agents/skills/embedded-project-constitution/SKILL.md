---
name: embedded-project-constitution
description: "Use when starting an embedded, edge, target-local, daemon/logger/recorder/collector project or introducing that runtime class into an existing repo, to create project-level physical budgets, target profiles, harness skeletons, and no-claim rules. Do not use for ordinary project initialization without embedded physical constraints."
metadata:
  short-description: Embedded project constitution
---

## Purpose

Use this skill to give a new embedded-facing project a physical-footprint constitution before feature work begins.

It answers one question:

**What repo-level NFR principles, budgets, target profiles, harness commands, and review gates prevent always-on target runtime from shipping without measured physical footprint?**

## When to use

Use this skill when:

- starting a new embedded, edge, target-local, robot-local, daemon, logger, recorder, collector, sampler, or sensor project
- introducing an always-on target-local runtime into an existing repo
- project direction includes battery, flash, thermal, wakeup, edge, embedded, sensor, robot, field recorder, or target daemon constraints
- `project-initialization` detects embedded/edge runtime evidence and the user wants physical-budget skeletons

Do not use it for ordinary command-system initialization; use `project-initialization`.

## How to use

1. Discover project context:
   - target classes
   - runtime modes
   - build/test commands
   - target smoke command availability
   - repo artifact conventions
2. Create or update project principles from `templates/project-principles.md`.
3. Create or update resource discipline guidance from `templates/resource-discipline.md`.
4. Create or update physical budgets from `templates/physical-budgets.yaml`.
5. Create or update a target profile from `templates/target-profile.yaml`.
6. Create or update resource harness skeleton from `templates/resource-harness.md`.
7. Add a PR template section from `templates/pr-template-section.md` where the repo has a PR template convention.
8. Add or document a resource-smoke command in `COMMANDS.md` or the repo-equivalent command registry.
9. Route feature-level work to `embedded-nfr-design`.

## Outputs

Produce or update project-level artifacts:

- `docs/00_project_principles.md`
- `docs/architecture/resource-discipline.md`
- `docs/testing/resource-harness.md`
- `requirements/physical_budgets.yaml`
- `target_profiles/<target>.yaml`
- `scripts/resource/run-resource-smoke.sh` or documented equivalent
- PR template embedded NFR section
- `COMMANDS.md` resource-smoke command or explicit unavailable reason

## Gotchas

- **Common pitfall:** creating budgets without commands that can exercise them.
  **Instead:** add a harness skeleton and mark missing target command evidence explicitly.
- **Common pitfall:** treating project constitution as feature-level proof.
  **Instead:** use it as the baseline; each embedded-facing feature still needs `embedded-nfr-design`.
- **Common pitfall:** adding impossible hardware-specific requirements to a template repo.
  **Instead:** use placeholders and target profiles.

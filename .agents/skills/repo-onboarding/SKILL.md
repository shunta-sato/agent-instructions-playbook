---
name: repo-onboarding
description: "Discover or repair missing repository commands, environment facts, or agent instructions. Not a prerequisite for ordinary edits."
---

# Repository onboarding

Establish the missing facts that prevent reliable work: build/test commands,
component boundaries, generated files, approved environments, and important
operating constraints. Existing current facts are sufficient; task length alone
is not a reason to inventory the repository.

For an unfamiliar repository, `scripts/inspect_repo.py --root PATH --markdown`
is an optional read-only collector. Its output suggests paths and commands; it
neither proves commands safe nor authorizes execution. Do not collect secret values.
Inspect the actual CI/configuration before adopting a command.

This Skill repairs repository facts. `preflight-engineering` aligns unresolved human
intent/authority and demonstrates the task's execution and verification path. Knowing
the command is not proof that required E2E can run. Return readiness gaps to that
conversation instead of certifying the environment from inspection alone.

Use the project-local working-contract template in `templates/AGENTS.md` only when
creating or repairing agent instructions. Keep facts near their existing owner;
record task deltas in the existing task/PR. Do not generate an instruction map,
cache-readiness report, or new specification when a missing fact is enough.

Return the established commands/constraints, unresolved decision-changing facts,
and any actual document changes. A preparation-only request does not authorize
product edits, deployment, migrations, or installing dependencies.

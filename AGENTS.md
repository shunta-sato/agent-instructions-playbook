# AGENTS.md — AI agent core instructions

This repository is a reusable playbook for software-development agents.

Keep this file short. Put detailed guidance in the on-demand playbooks under:
- `.agents/skills/<name>/SKILL.md` (Codex skills)
- `.github/skills/<name>/SKILL.md` (Agent Skills)
- `.github/prompts/<name>.prompt.md` (VS Code prompt files)

## Agent Index (generated)

This block is machine-oriented and always present in context.
Do not edit by hand. Update via: `python scripts/generate_agent_index.py --write`

<!-- BEGIN AGENT INDEX (generated) -->
```text
AGENT_INDEX_V1
meta|format=v1|max_bytes=8192|codex_invoke=$<skill>|prompt_invoke=/<prompt>
important|Prefer repo playbooks/references over pre-training for project-specific decisions.
defaults|workflow=dev-workflow|finish=quality-gate|verify=COMMANDS.md
path_rules|copilot=auto_apply_applyTo|codex=manual_open
core|AGENTS.md|COMMANDS.md|README.md|REFERENCES.md
skills|name|short|codex_skill|github_skill|prompt
skill|architecture-boundaries|Architecture boundaries (Clean Architecture)|.agents/skills/architecture-boundaries/SKILL.md|.github/skills/architecture-boundaries/SKILL.md|-
skill|bug-investigation-and-rca|Bug investigation & RCA|.agents/skills/bug-investigation-and-rca/SKILL.md|.github/skills/bug-investigation-and-rca/SKILL.md|-
skill|code-readability|Code readability|.agents/skills/code-readability/SKILL.md|.github/skills/code-readability/SKILL.md|-
skill|code-smells-and-antipatterns|Smells & anti-patterns triage|.agents/skills/code-smells-and-antipatterns/SKILL.md|.github/skills/code-smells-and-antipatterns/SKILL.md|-
skill|concurrency-android|Android concurrency and background work|.agents/skills/concurrency-android/SKILL.md|.github/skills/concurrency-android/SKILL.md|-
skill|concurrency-core|Concurrency design patterns and planning|.agents/skills/concurrency-core/SKILL.md|.github/skills/concurrency-core/SKILL.md|-
skill|concurrency-ros2|ROS 2 concurrency patterns|.agents/skills/concurrency-ros2/SKILL.md|.github/skills/concurrency-ros2/SKILL.md|-
skill|dev-workflow|End-to-end dev workflow|.agents/skills/dev-workflow/SKILL.md|.github/skills/dev-workflow/SKILL.md|/dev-workflow
skill|error-handling|Boundary error handling|.agents/skills/error-handling/SKILL.md|.github/skills/error-handling/SKILL.md|-
skill|modularity|Modularity (cohesion/coupling)|.agents/skills/modularity/SKILL.md|.github/skills/modularity/SKILL.md|-
skill|nfr-iso25010|ISO/IEC 25010 quality attributes template|.agents/skills/nfr-iso25010/SKILL.md|.github/skills/nfr-iso25010/SKILL.md|-
skill|observability|Observability plan and checklist|.agents/skills/observability/SKILL.md|.github/skills/observability/SKILL.md|-
skill|quality-gate|Final quality gate|.agents/skills/quality-gate/SKILL.md|.github/skills/quality-gate/SKILL.md|/quality-gate
skill|requirements-documentation|Requirements documentation|.agents/skills/requirements-documentation/SKILL.md|.github/skills/requirements-documentation/SKILL.md|-
skill|requirements-to-design|Requirements → design|.agents/skills/requirements-to-design/SKILL.md|.github/skills/requirements-to-design/SKILL.md|-
skill|test-driven-development|Test-driven development workflow|.agents/skills/test-driven-development/SKILL.md|.github/skills/test-driven-development/SKILL.md|-
skill|thread-safety-tooling|Thread-safety verification|.agents/skills/thread-safety-tooling/SKILL.md|.github/skills/thread-safety-tooling/SKILL.md|-
skill|visual-regression-android|Android visual regression defaults|.agents/skills/visual-regression-android/SKILL.md|.github/skills/visual-regression-android/SKILL.md|-
skill|visual-regression-ios|iOS visual regression defaults|.agents/skills/visual-regression-ios/SKILL.md|.github/skills/visual-regression-ios/SKILL.md|-
skill|visual-regression-testing|Tool-agnostic UI visual verification contract|.agents/skills/visual-regression-testing/SKILL.md|.github/skills/visual-regression-testing/SKILL.md|-
skill|visual-regression-web|Web visual regression defaults|.agents/skills/visual-regression-web/SKILL.md|.github/skills/visual-regression-web/SKILL.md|-
skill|working-with-legacy-code|Working with legacy code safely|.agents/skills/working-with-legacy-code/SKILL.md|.github/skills/working-with-legacy-code/SKILL.md|-
prompts|name|short|path|related_skill
prompt|bug-report|Generate an evidence-based Bug Report (RCA) for the bug being fixed in …|.github/prompts/bug-report.prompt.md|-
prompt|review-antipatterns|Review the selected diff/files focusing on NEW or WORSENED code smells …|.github/prompts/review-antipatterns.prompt.md|code-smells-and-antipatterns
prompt|review-modularity|Review the selected diff/files focusing on modularity.|.github/prompts/review-modularity.prompt.md|modularity
prompt|review-readability|Review the selected diff/files focusing on *reading time*.|.github/prompts/review-readability.prompt.md|code-readability
prompt|ui-verify|Use this prompt when UI code changes or when asked for screenshot/snaps…|.github/prompts/ui-verify.prompt.md|-
prompt|write-requirements|Write or update requirements/specs for the described change.|.github/prompts/write-requirements.prompt.md|requirements-documentation
instructions|title|applyTo|path|first_rule
instruction|C++ instructions (readability + maintai…|**/*.{h,hpp,hh,hxx,cpp,cc,cxx}|.github/instructions/cpp.instructions.md|Doxygen documentation is mandatory for this repository.
end|AGENT_INDEX_V1
```
<!-- END AGENT INDEX (generated) -->

## Goals
- Make changes easy to understand (readability).
- Keep changes localized (cohesion / coupling / boundaries).
- Keep requirements verifiable after the fact (docs + tests).

## Always-on principles
- Prefer the smallest change that satisfies the requirement.
- No large cleanups. Leave touched code slightly easier to read than before.
- If runtime behavior changes, add observability (logs/metrics/traces) so failures are diagnosable.

## Mandatory workflow for code/test changes
1) Apply the `dev-workflow` playbook end-to-end before editing.
2) Before finishing, apply the `quality-gate` playbook and address findings.

### How to run a playbook (depends on your tool)
- OpenAI Codex: invoke a skill with `$<skill-name>` (for example `$dev-workflow`, `$quality-gate`, `$observability`, `$bug-investigation-and-rca`). You can also use `/skills` to browse skills.
- VS Code prompt files: type `/` then the prompt name (for example `/dev-workflow`, `/quality-gate`).
- Agent Skills (VS Code / compatible agents): skills in `.github/skills/` load on demand when relevant.

## Language/path-specific rules

We store path-specific rules under `.github/instructions/` so GitHub Copilot can auto-apply them via `applyTo` globs.

- GitHub Copilot / VS Code: matching `*.instructions.md` files apply automatically when the file being edited matches `applyTo`.
- Codex CLI (and tools that only read `AGENTS.md`): these files are NOT auto-applied. Before editing, use the Agent Index above (`instructions|...` records) to find every matching instruction file, open it, and follow it.

Codex matching rule:
1) For each file you plan to edit, collect every instruction file whose `applyTo` matches that path.
2) Apply all matches. If instructions conflict, prefer the more specific `applyTo`. If still unclear, stop and ask before editing.

## Verification commands
Use the canonical commands in `COMMANDS.md` (build, format/lint, tests).
If you cannot run a command, state why and provide a reproducible procedure.

## Required final response format
Return, in this order:
1) Change Brief (what/why, scope, assumptions, risks)
2) What changed (files + intent)
3) Verification (commands + results; or what you could not run)
4) Follow-ups (optional)

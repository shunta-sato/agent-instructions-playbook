# AGENTS.md — AI agent core instructions

This repository is a reusable playbook for software-development agents.

Keep this file short. Put detailed guidance in the on-demand playbooks under:
- `.codex/skills/<name>/SKILL.md` (Codex skills)
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
core|AGENTS.md|COMMANDS.md|README.md|REFERENCES.md
skills|name|short|codex_skill|github_skill|prompt
skill|architecture-boundaries|Architecture boundaries (Clean Architecture)|/workspace/agent-instructions-playbook/.codex/skills/architecture-boundaries/SKILL.md|/workspace/agent-instructions-playbook/.github/skills/architecture-boundaries/SKILL.md|-
skill|code-readability|Code readability|/workspace/agent-instructions-playbook/.codex/skills/code-readability/SKILL.md|/workspace/agent-instructions-playbook/.github/skills/code-readability/SKILL.md|-
skill|code-smells-and-antipatterns|Smells & anti-patterns triage|/workspace/agent-instructions-playbook/.codex/skills/code-smells-and-antipatterns/SKILL.md|/workspace/agent-instructions-playbook/.github/skills/code-smells-and-antipatterns/SKILL.md|-
skill|concurrency-android|Android concurrency and background work|/workspace/agent-instructions-playbook/.codex/skills/concurrency-android/SKILL.md|-|-
skill|concurrency-core|Concurrency design patterns and planning|/workspace/agent-instructions-playbook/.codex/skills/concurrency-core/SKILL.md|-|-
skill|concurrency-ros2|ROS 2 concurrency patterns|/workspace/agent-instructions-playbook/.codex/skills/concurrency-ros2/SKILL.md|-|-
skill|dev-workflow|End-to-end dev workflow|/workspace/agent-instructions-playbook/.codex/skills/dev-workflow/SKILL.md|/workspace/agent-instructions-playbook/.github/skills/dev-workflow/SKILL.md|/dev-workflow
skill|error-handling|Boundary error handling|/workspace/agent-instructions-playbook/.codex/skills/error-handling/SKILL.md|/workspace/agent-instructions-playbook/.github/skills/error-handling/SKILL.md|-
skill|modularity|Modularity (cohesion/coupling)|/workspace/agent-instructions-playbook/.codex/skills/modularity/SKILL.md|/workspace/agent-instructions-playbook/.github/skills/modularity/SKILL.md|-
skill|nfr-iso25010|ISO/IEC 25010 quality attributes template|/workspace/agent-instructions-playbook/.codex/skills/nfr-iso25010/SKILL.md|/workspace/agent-instructions-playbook/.github/skills/nfr-iso25010/SKILL.md|-
skill|observability|Observability plan and checklist|/workspace/agent-instructions-playbook/.codex/skills/observability/SKILL.md|/workspace/agent-instructions-playbook/.github/skills/observability/SKILL.md|-
skill|quality-gate|Final quality gate|/workspace/agent-instructions-playbook/.codex/skills/quality-gate/SKILL.md|/workspace/agent-instructions-playbook/.github/skills/quality-gate/SKILL.md|/quality-gate
skill|requirements-documentation|Requirements documentation|/workspace/agent-instructions-playbook/.codex/skills/requirements-documentation/SKILL.md|/workspace/agent-instructions-playbook/.github/skills/requirements-documentation/SKILL.md|-
skill|requirements-to-design|Requirements → design|/workspace/agent-instructions-playbook/.codex/skills/requirements-to-design/SKILL.md|/workspace/agent-instructions-playbook/.github/skills/requirements-to-design/SKILL.md|-
skill|test-driven-development|Test-driven development workflow|/workspace/agent-instructions-playbook/.codex/skills/test-driven-development/SKILL.md|/workspace/agent-instructions-playbook/.github/skills/test-driven-development/SKILL.md|-
skill|thread-safety-tooling|Thread-safety verification|/workspace/agent-instructions-playbook/.codex/skills/thread-safety-tooling/SKILL.md|-|-
skill|working-with-legacy-code|Working with legacy code safely|/workspace/agent-instructions-playbook/.codex/skills/working-with-legacy-code/SKILL.md|/workspace/agent-instructions-playbook/.github/skills/working-with-legacy-code/SKILL.md|-
prompts|name|short|path|related_skill
prompt|review-antipatterns|Review the selected diff/files focusing on NEW or WORSENED code smells …|/workspace/agent-instructions-playbook/.github/prompts/review-antipatterns.prompt.md|code-smells-and-antipatterns
prompt|review-modularity|Review the selected diff/files focusing on modularity.|/workspace/agent-instructions-playbook/.github/prompts/review-modularity.prompt.md|modularity
prompt|review-readability|Review the selected diff/files focusing on *reading time*.|/workspace/agent-instructions-playbook/.github/prompts/review-readability.prompt.md|code-readability
prompt|write-requirements|Write or update requirements/specs for the described change.|/workspace/agent-instructions-playbook/.github/prompts/write-requirements.prompt.md|requirements-documentation
instructions|title|applyTo|path|first_rule
instruction|C++ instructions (readability + maintai…|**/*.{h,hpp,hh,hxx,cpp,cc,cxx}|/workspace/agent-instructions-playbook/.github/instructions/cpp.instructions.md|Doxygen documentation is mandatory for this repository.
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
- OpenAI Codex: invoke a skill with `$<skill-name>` (for example `$dev-workflow`, `$quality-gate`, `$observability`). You can also use `/skills` to browse skills.
- VS Code prompt files: type `/` then the prompt name (for example `/dev-workflow`, `/quality-gate`).
- Agent Skills (VS Code / compatible agents): skills in `.github/skills/` load on demand when relevant.

## Language/path-specific rules
- Follow `.github/instructions/*.instructions.md` when present.
- C++: `.github/instructions/cpp.instructions.md` is mandatory for `**/*.{h,hpp,hh,hxx,cpp,cc,cxx}`.

## Verification commands
Use the canonical commands in `COMMANDS.md` (build, format/lint, tests).
If you cannot run a command, state why and provide a reproducible procedure.

## Required final response format
Return, in this order:
1) Change Brief (what/why, scope, assumptions, risks)
2) What changed (files + intent)
3) Verification (commands + results; or what you could not run)
4) Follow-ups (optional)

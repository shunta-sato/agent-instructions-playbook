# Model-generation migration evaluation

## Scope

This common-contract update is the first migration step for Astra and Fable 5.1.
It aligns skill selection, proportional TDD, and specialist return conditions.
It does not register models, change the route lockfile, or claim improved model
performance. Keep the existing compatibility, authorization, and final-gate rules.

## Sources reviewed on 2026-09-05

- OpenAI, [Using GPT-6 Astra](https://developers.openai.com/api/docs/guides/latest-model):
  audit unclear/conflicting AGENTS.md and skill instructions before adding more
  prompting; distinguish actual blockers from ordinary implementation choices.
- Anthropic, [Prompting Claude Fable 5.1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1):
  start with existing prompts, then adjust observed behavior, including unnecessary
  tests and out-of-scope changes. Tune effort against the actual workload.
- Anthropic, [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices):
  keep instructions concise, match freedom to task fragility, and evaluate skills
  with each intended model.

The scope and evaluation rules below are this repository's application of those
sources, not vendor-certified settings or evidence that a model passed.

## Regression seeds

- `skill-triggers/workflow-scope.json`: local edits versus boundary changes,
  explicit/project-required TDD, strategy-dependent test design, and sensitive preflight.
- `skill-behavior/function-boundary-governor.json`: scoped discovery, valid no-op,
  explicit review, and retained migration safeguards.
- `skill-behavior/test-driven-development.json`: a sufficient one-case Test List,
  truthful Red-Green evidence, no forced cleanup, and required safety cases.
- `skill-behavior/preflight-engineering.json`: return to the calling task versus
  preflight-only completion, one-file security work, and untrusted approval claims.

Run these alongside the existing function-design, core routing, unit-test-design,
and quality-gate cases; do not replace those regression suites.

## Comparison protocol

For each exact model/harness pair, compare A (the base playbook), B (this common
update), and C (a short model-specific supplement only if B leaves an observed
failure). Hold the repository snapshot, task fixtures, tool permissions, effort,
and success criteria constant within a comparison. Record exact model ID,
harness/version, effort, playbook commit, repeated-run count, and evidence links.
Do not assume equal effort labels are equivalent across models.

Assess task completion, required verification, unsafe actions, unnecessary
clarifications, skill loads, repeated checks, unrelated edits, whole-file rewrites,
latency, and available token/cost data. Reducing counts is not success when a
required investigation or test is missing. Investigate regressions in both directions:
excessive procedure and omitted safeguards.

Keep instruction detail, reasoning effort, verification depth, and authorization
independent. Do not clone every skill for each model. Async tool execution,
permission enforcement, and conversation-state handling belong to the actual
harness; prompt text does not enable unsupported capabilities.

## Activation and evidence

Schema/protocol checks validate these files, not model behavior. Record real model
runs separately; do not promote a model to verified/passed status from static
checks or inherited results. Activate a new model/harness route only after its
availability and smoke/behavior evidence satisfy the existing routing policy.
Leave the catalog and route lockfile unchanged until then.

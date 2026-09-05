# Outcome-based anti-slop evaluation

## Scope and claim boundary

This is an operator-run comparison, not another mandatory development skill.
Reuse the six function-design fixtures and their code/contract oracles. Routing
and response-text seeds remain useful diagnostics, but they do not prove better
software. Fixture calibration is not a real model run; a real model run is not
proof of broad productivity improvement.

The initial targets are the user's observed GPT-5.6 Sol overengineering and
Fable-family comment verbosity. These are hypotheses to measure, not vendor-wide
claims or a reason to copy every skill into model-specific variants. Include
Astra/Fable 5.1 using the exact IDs actually available in the chosen runner.
No model catalog, effort setting, or verified status changes automatically.

## Compare minimal / core / full

Pre-register the task set, repeated-trial count, model/harness/version/effort,
permissions, environment, success criteria, and available cost metrics. Run paired
trials from the same baseline; rotate variant order and use fresh sessions so one
trial does not teach another. Do not select only successful runs.

| Variant | Instructions available to the agent |
| --- | --- |
| minimal | Common task contract, required safety/compatibility rules and canonical verification; no Playbook workflow injection |
| core | The same contract plus `dev-workflow`, `quality-gate`, and `user-value-delivery` where applicable, including required references |
| full | The same contract plus normal conditional skill routing; do not force all skills into context |

Create disposable task workspaces outside this playbook's instruction ancestry.
Copy only the fixture's baseline source, baseline tests, and task. Keep the
trusted grader, expected outputs, and acceptance tests outside agent-visible
editable paths. Pin the grader checkout read-only. Do not strip safety rules from
real repositories or expose expected/good or expected/bad as implementation hints.
If a task explicitly requests a specialist, honor it in every variant or exclude
that task from the ablation; do not score deliberate instruction violations.
Keep all task-required evidence (including a ledger where explicitly required)
equal across variants. Hash the actual instruction/file manifest supplied to the
runner, not just the profile name.

## Grade an actual final workspace

Run inside a disposable, credential-free sandbox with network and process-tree
limits enforced by the harness. The Python helper is not a sandbox. Stop the
agent before grading; do not mutate the trusted checkout during a grade.

Save caller-supplied run metadata outside the candidate workspace:

```json
{
  "run_id": "run-001",
  "kind": "agent-run",
  "variant": "core",
  "model": "exact runner model ID",
  "harness": "runner name and version",
  "effort": "actual effort setting",
  "environment": "runtime and sandbox image/version",
  "playbook_commit": "replace with the 40-character lowercase commit SHA",
  "instructions_sha256": "replace with the 64-character instruction-manifest digest",
  "trial": 1
}
```

The two digest placeholders must be replaced before use. Use `kind: calibration`
for known-good/bad samples, manual patches, and tool self-tests; never label those
as model outcomes. Keep transcripts and a full candidate diff with the run;
redact secrets and do not commit private reasoning or credentials.

```sh
python3 evals/function-design/scripts/grade_run.py \
  --scenario no-op-small-duplication \
  --workspace /tmp/slop-eval/run-001/workspace \
  --run-metadata /tmp/slop-eval/run-001/run.json \
  --out /tmp/slop-eval/run-001/grade.json
```

The grader copies candidate source and its design ledger into a temporary
workspace, injects pinned expected-good acceptance tests, and runs the existing
oracle. Candidate tests cannot replace those tests. The original workspace is
not edited. Exit codes: 0 means oracle pass, 1 means failed/zero-test/timed-out
execution, 2 means invalid input or inability to grade. Reports are never
silently overwritten; errors are not success records.

The report binds source, judged inputs, baseline, task, trusted tests, oracle,
and helper digests. Match these identities when comparing runs; only the intended
instruction treatment and repeated trial should vary. Source delta and oracle
runtime are diagnostics, not quality scores or the agent's development latency.
Metadata is a caller assertion, not proof of model authorship. Keep the runner's
actual evidence separately. Candidate-added tests need their own normal checks.

## Assess slop without replacing it with another score

Inspect the actual diff and individual oracle findings for current-need failures:
future-only wrappers/registries, unsupported compatibility branches, silent
success fallbacks, redundant narration/private docstrings, and permanent scratch
artifacts. Preserve useful local helpers, supported compatibility, security and
resource boundaries, real regression tests, public contracts, hazards, licenses,
and tool directives. Do not grade all abstraction or every comment as bad.

Record functional acceptance and design/contract failures separately from size,
latency, tokens/cost, tool calls, and human interventions. Missing measurements
stay unknown, not zero. Review flagged diff locations, preferably without model
or variant labels. A source-size reduction that removes necessary checks fails.
A scalar "slop score" or keyword match cannot replace contract evidence.

Publish per-task outcomes, failed/blocked runs, trial counts, and comparable cost
measurements. Reduce shared instructions only when required behavior is retained.
Keep uncertain results inconclusive. This fixture set covers bounded function
work, not all security, concurrency, UI, or production-development tasks.

## Calibration and regression commands

```sh
python3 evals/function-design/scripts/run_oracles.py
python3 -m unittest discover -s tests -p test_function_design_runs.py
```

The new unit suite runs existing good/bad calibration, grades all six good
workspaces, and verifies that no-op work rejects added narration and unused
abstraction. It also tests immutable acceptance tests, zero tests, timeout,
invalid identity, symlinks, and report overwrite. These are tool tests, not
Astra/Sol/Fable performance results.

## Official guidance reviewed on 2026-09-05

- [OpenAI model guidance](https://developers.openai.com/api/docs/guides/latest-model):
  audit unclear or conflicting agent instructions before adding more guidance.
- [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices):
  constrain unnecessary engineering and keep changes tied to the requested work.
- [Prompting Claude Fable 5.1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1):
  evaluate effort and constrain unrequested additions/tests; prefer targeted edits.
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents):
  distinguish transcript claims from environment outcomes and use repeated trials.

The policies and comparison protocol here are this repository's application of
those sources, not vendor-certified settings or measured model improvements.

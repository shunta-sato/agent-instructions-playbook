# Continued-change evaluations (live model trials not run)

A passing checkpoint is necessary, not proof of low slop. Carry the agent's actual repository
through successive requests and start a fresh conversation each time. Keep prior accepted
requirements, but never reveal later requests or replace the repository with a reference
solution. The final maintainer therefore works without the original author's chat history.

## Run one sequence

From the repository root, with Python 3.11+, Git and POSIX:

```sh
python3 -m scripts.run_evolution_evals \
  --scenario preferences --arm selective \
  --adapter-json '["/approved/sandboxed-evolution-adapter"]' \
  --model EXACT_RESOLVED_SUPERVISOR --harness YOUR_HARNESS \
  --team-json '[{"role":"implementer","model":"EXACT_RESOLVED_WORKER"}]' \
  --output /new/trial-directory --sandbox-confirmed
```

This is an invocation example, not an installed/live adapter or model recommendation.
No model calls occur in CI. Single-agent runs use `--team-json '[]'`. Match the supervisor,
worker configuration, harness version, budgets, tools and permissions across instruction
arms before changing model identities. `baseline` uses `--baseline` with a pinned historical
checkout; `minimal` uses the current working contract, `selective` adds the declared Skills.
Run repeated trials in new directories and rotate order externally. Use held-out realistic
repositories, not only this small Python fixture, before claiming improvements.

## Protocol 2 and security boundary

The adapter receives the original protocol's workspace/task/metadata/trace fields plus
`stage_id`, `fresh_conversation: true` and `requested_team`. Each invocation must actually run
the agent/team in a NEW conversation with the SAME workspace. Metadata must include exact
`resolved_model`, `harness`, `harness_version`, `team`, a unique `conversation_id`, and
`context_mode: "fresh"`. Preserve actual tools, worker identities, effort/configuration,
usage and interventions in the trace/metadata. Self-reported IDs do not prove isolation;
review the harness configuration and actual trace. No universal multi-agent SDK is supplied.

The runner and `--sandbox-confirmed` ARE NOT a sandbox. The trusted operator must restrict
agent/generated-code access to the workspace and prevent access to sibling stages, future
scenario prompts, oracle/reference code, result files and model-transport secrets. Only the
trusted adapter may write metadata/trace outputs. Running the oracle invokes candidate code:
it too must be isolated from the evaluator and external side effects by the execution site.
Temporary directories and process timeouts are NOT an isolation mechanism. Protect the
trial's AGENTS/COMMANDS and Git metadata; their post-run checks are detection, not enforcement.

Results contain scenario/oracle/runner digests, per-stage before/after commits, retained
patches, actual process results and trace hashes. Git snapshots cover non-ignored files;
the operator must check ignore rules and unexpected artifacts, not treat a Git tree as a
security proof. Failure, timeout, missing/mismatched metadata or reused conversations stops
the sequence; later stages stay unrun, not independently solved. Exit 0 means every functional
checkpoint passed and behavior review is STILL PENDING. It is never a slop-quality pass.

## What to review

Look at integrated code and real next-change work: rule ownership, unjustified compatibility,
indirection, comments that lose necessary rationale, diagnostic difficulty and reviewer load.
Require a location, causal maintenance burden and bounded alternative for a blocking finding.
Compare completion/security first, then maintenance success, total effort and human review.
Use LOC/duplicates/complexity only as diagnostics, partitioning product/tests/generated code
and recording analyzer/rule versions. No aggregate Slop Score, model stereotype or LOC quota.
Include negative controls: legitimate external compatibility, necessary explanatory comments,
intentionally separate policies, safety boundaries and measured optimizations must survive.

The functional oracle deliberately does NOT prescribe a module graph. A duplicated design
can pass current behavior; the next edit plus trace/code review assesses its cost. Fixture
adapters and reference solutions in `tests/fixtures` test this runner, not Astra/Fable or any
worker model's actual quality. No real supervisor/worker continuation experiment has run.

## Rationale

[Measuring code sloppiness](https://earendil.com/posts/measuring-code-sloppiness/) motivates
longitudinal evaluation and warns against optimizing LOC itself. This implementation is an
original small engineering fixture, not a reproduction or leaderboard result for
[SlopCodeBench](https://arxiv.org/abs/2603.24755). Models' generational names are not evidence
that design oversight is solved. Repository policy is separate from vendor capability claims.

# Outcome evaluations (live trials not yet run)

The offline test suite verifies tools and fixtures, **not Astra behavior**. This directory
replaces output-substring and old-route expectations with matched task outcomes plus
explicit trace review. Do not equate a successful script exit or final answer with success.

## Three instruction arms

`baseline`: the pinned pre-redesign instruction/tool surface from commit
`7c3b885fd72629f2fb91f4662dbbb16d502c2e38`; `minimal`: consumer working contract only;
`selective`: that same contract plus only the case's specialist skills. All arms receive
the same fixture, prompt, canonical fixture commands, resolved model and harness.
The baseline arm installs the historical AGENTS/PLANS/REFERENCES, skills, model-routing,
project policy and scripts, not unrelated historical execution logs. It is an instruction
ablation on a synthetic project, not a reproduction of a past production run.

Nine case seeds are provided. **Three have executable functional oracles** (small fix,
CLI completion, contract replacement). Six require trace adjudication; some explicitly
require real source/repro/target fixtures before scoring. Their seeds alone are not
completed experiments. Expand them with held-out realistic projects and keep fixture
hashes before making general performance claims.

## Adapter protocol

Run `python scripts/run_task_evals.py --help`. Supply `--adapter-json` as an argv array,
`--model` as an exact expected resolved model ID, `--harness`, a new `--output` directory,
and `--baseline` pointing to the pinned historical checkout. `--arm`, `--case` and
`--repeats` select trials. No model is hardcoded or silently substituted.

The adapter receives JSON on stdin with `protocol`, `workspace`, `task`, requested model
and harness, and output paths for metadata/trace. It must run the actual coding agent,
not merely generate a response; emit JSONL trace events; and write metadata with
`resolved_model`, `harness`, `harness_version` and, when available, usage/cost and
configuration. The adapter must make the workspace's native Skills visible to the agent.

`--sandbox-confirmed` is required. This runner is **not a security sandbox**: use a
credential-free container/VM or equivalently restricted harness, disable network and
external side effects unless explicitly needed, and make evaluator code/output immutable
to the agent. Review both adapter and oracle code. Temporary directories alone do not
confine an agent. The adapter may need a separate model transport credential; do not expose
it to generated code or record it in traces.

## Scoring and evidence

The runner records raw adapter output, metadata, trace digest, fixture digest and functional
oracle result, without accepting an unverified model alias. Missing trace/metadata, timeouts,
nonzero execution or a failed oracle cannot pass. A successful oracle is still marked
`needs-behavior-review`; CLI exit 0 means the trials were recorded without technical failure,
not that the candidate passed behavioral evaluation. Fixture/fake-adapter unit tests never
count as live trials.

Review required behavior, actual verification, unwarranted stops, authority violations,
repeated uninformative actions and unnecessary permanent artifacts. Record the criterion,
evidence event and disposition; prefer a blind human or independently calibrated grader.
Compare completion and safety first, then total time/cost; count loaded bytes and duplicate
checks diagnostically, not as quality scores. Repeat matched trials, rotate arm ordering,
retain failures and held-out cases, and report uncertainty. No universal speedup, optimal
Skill count or model superiority is asserted by this PR.

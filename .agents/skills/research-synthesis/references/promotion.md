# Optional promotion boundary checker

Projects that adopt the bundled ledger can run `scripts/check_research_evidence.py`
against their explicit `.agents/project-policy.yml` and changed paths. Read `--help`
before invocation. Its schema checks research/delivery path boundaries, declared evidence
and the promoted contract. This is not an automatic gate for every code change.

Keep the accepted result, contract, raw evidence and limitations separate from disposable
implementation. The historical promotion schema retains its machine keys; a field named
`quality_gate` does not require invoking a retired Skill. Production claims still need
the target project's actual acceptance checks and authorization.

In this repository, older promotion records document earlier executions. They are kept
for audit and integrity regressions; they are not the current contributor workflow.

---
name: experiment-evidence
description: "Use when recording or validating an empirical experiment whose result supports a decision or quality claim."
---

# Experiment evidence

Preserve the question/hypothesis, candidate, environment/target, workload, method,
raw artifacts, result and limitations needed to reproduce the claim. Separate
exploratory from confirmatory work; do not invent preregistration after seeing data.
An exploratory observation may be reported as exploratory with provenance.
Independent confirmation is needed when the intended claim calls for it.

Use [record format](references/record-format.md) and
`scripts/validate_record.py` only when a machine-consumed evidence record is needed.
The validator checks structure, identity and declared criteria, not scientific
truth, authorization, authenticity or the completeness of product requirements.
Reuse an existing experiment system instead of duplicating it.

Keep required criteria separate from optional goals and baseline values. Store
raw evidence before synthesis, sanitize secrets and retain negative/failed results.
New code, load or target assumptions invalidate affected proof. Never turn an
unrun method, absent measurement or generated plan into empirical evidence.

---
name: decision-analysis
description: "Resolve conflicting requirements or consequential architecture choices when missing facts or trade-offs affect the decision."
---

# Decision analysis

Make the decision from the intended use, failure impact, workload, expected changes,
and recovery constraints. Compare plausible alternatives against the actual required
conditions; do not assign an aggregate design score or prescribe an option count.
A local reversible choice normally needs neither this skill nor a decision document.

When quality requirements are unresolved, consult `references/quality-contract.md`.
Distinguish a required condition, an optional improvement, and its observed evidence.
Unknown applicability remains a question. Do not infer low risk from a small diff,
short lifetime, an entertainment label, or the absence of explicit NFR wording.

Investigate existing callers, tests, and operating facts before asking for information
already in the project. Use a decisive probe when it resolves the choice. Resolve
material authorization conflicts before the affected action, while continuing useful
independent work. A required condition discovered late may revise the affected scope.

Retain the choice, decisive evidence, rejected trade-offs, and revisit condition in
the current task/PR; create an architecture record only for a durable consumer.

---
name: incident-investigation
description: "Use for unexplained recurring failures, corruption, hangs or flakes requiring causal investigation beyond an obvious local fix."
---

# Incident investigation

Establish the observable failure and smallest useful reproduction. Preserve build,
input, environment and timing needed to distinguish hypotheses; sanitize sensitive
data. A symptom disappearing once is not proof of causation.

Choose the next probe for information gain. Reuse valid logs and experiments; avoid
same-input retries without a changed hypothesis. Separate the root cause from
mitigation and from pre-existing unrelated defects. Check actual error propagation
and recovery instead of adding silent fallbacks.

Deliver a fix or bounded mitigation with regression evidence. For race/ordering
failures, preserve the observed schedule or invariant rather than relying solely
on an arbitrary sleep. Retain a useful regression test and non-obvious constraints;
create an incident report only for its real operational consumer or explicit request.

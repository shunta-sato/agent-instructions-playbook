---
name: research-workflow
description: "Choose informative probes or disposable prototypes for a feasibility, optimization, or comparative exploration question."
---

# Research direction

State the question, the decision it unlocks, and the next informative observation.
Unknowns are what research reduces, not preconditions to eliminate before starting.
Prefer an existing artifact or a small falsifying probe when it can change the
choice; do not run experiments whose outcomes cannot change the decision.

For a prototype or executable variant comparison, read `references/construction.md`
only when building those artifacts. Disposable implementation does not need production
maintainability. Physical safety, secret handling, data integrity and authorization
still apply. Use an approved isolated workspace; writing into a product path is not
implicitly authorized by calling it research.

Observations can be reported as exploratory with their source and limits. For a
quantitative confirmatory claim that needs preregistration, use `experiment-loop`.
At a decision point, use `research-synthesis` when results need comparison; there is
no fixed result-count trigger or mandatory four-line output ritual.

Continue while the next authorized action can resolve a relevant uncertainty. Stop,
pivot or report a blocked question when it cannot; do not substitute an arbitrary
attempt/time cap for the task's actual budget and decision boundary.

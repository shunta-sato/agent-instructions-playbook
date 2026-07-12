# Research framing — depth reference

This file is optional depth material for `$research-workflow`. It is not required reading before every research cycle; the 4-line frame in the skill body is sufficient for routine work. Open this file when the 4-line frame feels too thin to make the next probe decision, or when the team is stuck and needs a divergent-ideation pass.

## Fuller framing fields

The 4-line frame (`mode` / `question` / `decision` / `next_probe`) is the mandatory minimum. When a cycle is long-running, ambiguous, or high-stakes, extend it with these optional fields:

- **current_belief** — the working answer to `question` right now, stated as a probability or a ranked list of live hypotheses, not a certainty.
- **disconfirming_evidence** — what evidence, if observed, would move `current_belief` the most; write this before the probe runs, not after.
- **success_region** — the range of outcomes that would count as "this probe was worth running," independent of whether the hypothesis is confirmed or falsified.
- **safety_boundary** — any physical, financial, or data-integrity limit the probe must not cross (see `$embedded-operating-envelope-discovery` and `$embedded-observer-effect-review` when the probe touches a physical target).
- **budget** — time, compute, or hardware-access budget for this cycle, so probe selection has a real constraint to optimize against.

These fields are prose, not a schema `research_run.py` enforces. Use only the ones that sharpen a real decision; do not fill every field on every cycle.

## Hypothesis quality guidance

Not all hypotheses are the same shape, and conflating them wastes probes:

- **Competing hypotheses** disagree about which of several mechanisms explains the data. A good probe distinguishes between them — it predicts a different outcome under each. If two competing hypotheses predict the same outcome for a candidate probe, that probe belongs low in the ordinal decision tree (step 3 in the skill body).
- **Mechanism hypotheses** claim *why* an effect happens, beyond just *that* it happens. These usually need a probe that isolates one variable at a time; a single confounded probe rarely settles a mechanism question.
- **Measurement-artifact hypotheses** claim the observed effect is a property of the harness, not the system under study — sampling bias, a leaking cache, an off-by-one in the metric. These deserve early priority: an unresolved measurement-artifact hypothesis quietly invalidates every other result gathered while it stood, so it is often the "small proxy or upper-bound probe" step 5 of the ordinal tree is asking for.

This is prose guidance, not a state machine. Do not build a formal hypothesis-tracking workflow on top of it; write hypotheses in plain language in the cycle frame and update `current_belief` as evidence arrives.

## Divergent ideation

When probe selection stalls — every visible option looks low-value, or the live hypotheses feel like a false dichotomy — the fix is not to think harder alone in prose. It is orchestration: spawn independent workers, each given a different lens, and let them generate candidate hypotheses or probes without seeing each other's output. Cross-contaminated ideation collapses back to one person's first idea with extra words around it.

Useful lenses to assign, one per worker:

- **Assumption inversion** — take the load-bearing assumption behind the current approach and ask what follows if it is false.
- **Boundary moving** — treat a fixed constraint (budget, hardware, timeline) as movable and ask what becomes possible.
- **Cross-domain transfer** — ask how an unrelated field (biology, control theory, economics, a different subfield of ML) would frame this problem.
- **Mechanism decomposition** — break the system under study into its smallest independently-testable parts and ask which part is actually unverified.
- **Constraint-as-invention** — treat the tightest constraint as the design brief, not the obstacle, and ask what it makes possible.
- **Hierarchy inversion** — ask what changes if the thing currently treated as fixed infrastructure is instead the variable, and vice versa.
- **Co-design** — ask what changes on both sides of an interface (model and system, algorithm and hardware) if they are allowed to move together instead of one being held fixed.

Generate candidates from each lens independently, then judge them together against the live hypotheses and the current budget. Do not let one lens's output seed another's — that is exactly the cross-contamination this technique exists to avoid.

---
name: embedded-runtime-evidence
description: "Design or verify changes against real power, thermal, flash, memory, deadline, or observer-overhead constraints on a target."
---

# Embedded runtime evidence

Inherit the actual required conditions and operating envelope. Discover a present-use
physical constraint when the task omits it, but do not classify ordinary server work
as embedded merely because it uses a logger or polling loop.

Read the reference matching the unresolved question:
- `references/physical-constraints.md`: affected dimensions and degradation behavior.
- `references/budget-provenance.md`: unknown or proposed budget values.
- `references/measurement.md`: test design, sample/window limits, and evidence identity.
- `references/observer-effects.md`: instrumentation that can perturb the workload.
- `references/hot-paths.md`: frequent/continuous work and constrained implementation.

There is no universal polling-interval floor, zero-allocation rule, or mandatory
harness/report pair. Derive required limits from the supported use and source, not
from a template or whichever value the candidate happens to meet. Keep required
limits, improvement targets and evidence status distinct.

A missing target or measurement cannot turn a required NFR into optional wording.
Perform authorized independent implementation/host checks, state what they prove,
and leave the target-specific completion claim blocked until matching evidence exists.
An explicitly requested experiment can complete as an experiment, not as a release.

Use a project's existing measurement tools. `scripts/verify_evidence.py` is an optional
manifest-consistency check when machine consumers need candidate/context/digest binding;
its successful result is not independent certification of the measurements or safety.
No new permanent artifact is required without a real consumer.

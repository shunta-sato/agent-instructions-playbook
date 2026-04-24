# Modularity: cohesion, coupling, and boundaries

Use this reference to evaluate changed units in the current diff. The purpose is to reduce change ripple, keep the review concrete, and avoid broad cleanup work.

## Review order

1) Read from a relevant caller or entry point into the changed implementation.
2) Summarize the change in one paragraph: input, output, invalid input behavior, and touched boundaries.
3) Judge the changed units from three viewpoints:
   - cohesion: which unit does which job;
   - coupling: which dependencies increased or became harder to replace;
   - boundaries: whether core code stays independent from outer types and conventions.

## Cohesion

Cohesion asks whether the code inside a unit works together toward a single purpose.

For each new or changed function/class:

- Describe it in one sentence using "do X to Y".
- If the sentence needs multiple verbs, ordering words, or mode flags, cohesion is likely weaker.
- Judge the unit by the worst cohesion level present, then choose the smallest fix that reduces reading time.

### Cohesion scale

| Type, worse to better | Typical smell | Smallest useful fix |
|---|---|---|
| Coincidental cohesion | Grab bag of unrelated utilities or dumped logic | Move unrelated behavior out; avoid new dumping grounds. |
| Logical cohesion | Behavior switches by mode/flag | Split functions; extract only truly shared parts. |
| Temporal cohesion | Grouped only because steps run around the same time | Keep a short orchestrator and push details down. |
| Procedural cohesion | Order is the main meaning | Keep one step group per function and name intermediate results. |
| Communicational cohesion | Steps touch the same data but do different jobs | Move behavior toward the data owner or split responsibilities. |
| Sequential cohesion | One step feeds the next | Split by stage and name conversion points. |
| Functional cohesion | One clear job | Keep as-is. |

## Coupling

Coupling asks how strongly a unit depends on other units, external systems, global state, or execution order.

For each new or changed unit:

- List newly added imports/includes/dependencies and global state access.
- Check whether the unit reaches into another unit's internals or relies on hidden execution order.
- Treat the strongest coupling form as the representative risk for the diff.

### Coupling forms

| Form, worse to better | Typical smell | Smallest useful fix |
|---|---|---|
| Content coupling | Touches private/internal implementation | Expose a proper public API or redesign the access path. |
| Common coupling | Multiple units read/write shared global state | Create a single owner and centralize access. |
| External coupling | Core is bound to external formats/protocols | Convert at the boundary; keep external types out of core code. |
| Control coupling | Caller passes flags that decide what callee does | Split functions and branch at the caller. |
| Stamp coupling | Passes a large object but uses only a small part | Pass the smaller structure or fields needed. |
| Data coupling | Passes only necessary data | Prefer this for simple synchronous code. |
| Message coupling | Communicates by signals/events | Useful for async systems; avoid using events to hide control flow. |

## Boundary checks

Boundary checks overlap with architecture review but stay focused on changed modularity.

- Core code should not depend on UI/HTTP/DB/framework/SDK names or types.
- Dependency direction should point toward stable policy, not toward volatile detail.
- Boundary data should be simple DTO-style data, with conversion near the adapter.
- If strong coupling is unavoidable, keep it localized and document the escape hatch.

## Test and monitoring notes

- Cohesion-only fixes should keep existing behavior and tests green.
- New logic should have tests named around the one-sentence behavior.
- External I/O changes should test the wrapper/adapter policy for errors, timeouts, retries, and data conversion.
- If a larger modularity fix is deferred, monitor the tests or logs most likely to expose boundary failures or change ripple.

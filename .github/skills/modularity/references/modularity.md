# Modularity handbook: cohesion, coupling, and boundaries (for AI Agents)

This document complements the `code-readability` handbook. It provides a shared vocabulary so an AI agent can judge “good design” consistently during implementation, testing, and review.

“Good design” here is not about personal style. It means: changes are less likely to break things, the change surface stays small, and the next reader is less likely to get lost.

## Terminology (how this document uses words)

- **Cohesion**: how well the code inside a unit works together toward a single purpose.
- **Coupling**: how strongly a unit is pulled by other units (other modules, external libraries, global state).
- **Boundaries**: architectural separation that keeps the core rules independent from volatile outer details (UI/DB/frameworks/external services).

---

## 1. Mandatory pre-change procedure

Always follow this order to reduce design blind spots:

1) **Read first**: start from a relevant entry point (caller) and read top-to-bottom until the implementation. Understand data shapes and where responsibilities live.

2) **Summarize in one paragraph**: what will change, input/output, how invalid input is handled, and the boundaries (UI/HTTP/DB/external services). Unknowns must be written as **assumptions**.

3) **Write a design sketch from three viewpoints**:
   - cohesion: which unit does which job
   - coupling: which dependencies increase (and which can be avoided)
   - boundaries: whether core code stays independent from outer types and conventions

---

## 2. Cohesion (quality *within* a unit)

### 2.1 Metric

- Can you describe what the function/class does in **one sentence**?
- Does that sentence mix multiple purposes (“and”, “also”, “in addition”, “switch by flag”)?
- If “bad cohesion” is unavoidable, did you keep that part **small**?

### 2.2 Threshold (rule of thumb)

Numbers are not the goal; they are a guardrail so the AI does not hesitate.

- **Temporal grouping** (only “runs around the same time”, e.g., initialization): treat the top level as an orchestrator and keep it around **≤ 20 lines**; push details downward.
- **Procedure-first code**: keep one meaningful step group in **one function**, and flatten nesting via early returns.

(Only enforce these when they reduce reading time; do not split purely to hit a number.)

### 2.3 Measurement (AI must do this)

For every changed/new function/class:

- Write a one-sentence description in the form: **“do X to Y”**.
- If the sentence needs multiple verbs, or needs ordering words (“first/next/then”), cohesion is likely weak. Classify it using the table below.
- Judge cohesion at the **lowest (worst) level** inside the unit.  
  Example: even if there is a sequential pipeline inside, if the whole unit is mostly “stuff that happens at the same time”, then treat it as temporal cohesion overall.

### 2.4 Tests / monitoring

- Cohesion improvements often do not change behavior. The minimum condition is: **existing tests stay green**.
- If you add new logic, reflect the one-sentence description in the test name, and keep the structure “input → action → expectation”.

### 2.5 Design notes

- “Splitting for cohesion” can make readers jump back and forth. If the split increases reading time, change the split plan.
- Start by splitting into **paragraphs** (blank lines). If a paragraph needs a heading, it is a candidate for extraction into a function.

### 2.6 Cohesion scale (7 levels, worse → better)

The ideal is **functional cohesion**, but real code is mixed. When mixed, prioritize “keep the bad part small”.

| Type (worse → better) | Typical smell | Fastest fix for AI |
|---|---|---|
| Coincidental cohesion | A grab bag of unrelated stuff (“utils pile”, random dumping ground) | Move things out; do not create a dumping ground. |
| Logical cohesion | Behavior switches by flag (`mode`, `isFoo`) | Split functions; extract only the truly shared part. |
| Temporal cohesion | Grouped only by timing (init, before/after) | Keep the top level as a small orchestrator; push details down. |
| Procedural cohesion | The order is the main meaning (“do A then B”) | Keep one step group per function; name intermediate results. |
| Communicational cohesion | Grouped because they touch the same data | Move behavior toward the data owner (type/class). |
| Sequential cohesion | Output of one step becomes input of the next (pipeline) | Split by stage; name conversion points. |
| Functional cohesion | One job that does not benefit from further splitting | Keep as-is. |

---

## 3. Coupling (quality *between* units)

### 3.1 Metric

- What external elements does the changed unit depend on (other modules, external libraries, global state)?
- Does it reach into the other unit’s internals or execution order?
- If strong coupling is unavoidable, did you keep the impact **localized**?

### 3.2 Threshold (rule of thumb)

- When you find strong coupling, push it to the **outer boundary** by default. Do not pull it into the core.
- If you must keep it in the core, write the reason and an escape hatch (an interface to move it out later).

### 3.3 Measurement

- List newly added imports/includes/dependencies (libraries/modules/globals).
- Classify the dependency using the table below.
- Treat the **strongest (worst)** form as the representative risk for this change.

### 3.4 Tests / monitoring

- Strong coupling makes test setup heavy. Prefer core logic that can be unit-tested without outer layers.
- If touching external I/O (HTTP/DB/FS), isolate it behind a thin wrapper and fix policy there (error translation, retry policy, timeouts).

### 3.5 Coupling forms (worse → better) and what to do

| Form (worse → better) | Typical smell | What the AI should do |
|---|---|---|
| Content coupling | Touches private/internal implementation (reflection, pointer tricks, “opening private”) | Don’t. Expose a proper public API or redesign. |
| Common coupling | Multiple units read/write global state | Create a single owner; centralize read/write access. |
| External coupling | Bound to external formats/protocols | Convert at the boundary; do not leak into the core. |
| Control coupling | Caller passes flags that decide “what to do” | Split functions; branch at the caller. |
| Stamp coupling | Pass a big struct but use only a small part | Pass only what you need (smaller structure). |
| Data coupling | Pass only necessary data as parameters | Prefer this by default. |
| Message coupling | Mostly signals (events) | Useful for async/event systems; avoid overuse. |

---

## 4. Boundaries (maintainability across the whole app)

### 4.1 Metric

- Does core code avoid knowing outer **names and types** (UI/DB/frameworks)?
- Do dependencies point **outer → inner**?
- Is boundary data a **simple container** (DTO-style)?

### 4.2 Threshold (rule of thumb)

- If core code sees `HttpRequest`, ORM models, DB-row types, etc., **fix immediately**.
- If you keep an exception, write the reason and the migration plan at the top of the file.

### 4.3 Measurement

- Check imports/includes in the diff: outer types must not leak into core code.
- If dependency is reversed, define a small interface in the inner layer and implement it in the outer layer (dependency inversion).

### 4.4 Tests / monitoring

- The core should be testable without UI/DB by default.
- Boundary wrappers can have thin integration tests close to real environments; keep core tests simple.

### 4.5 Design notes

- The number of layers is not the point. The point is: separate concerns and keep dependency direction inward.
- Convert data at the boundary into core-friendly shapes. Do not stream outer “convenient types” inward.

---

## 5. Mandatory self-review output (AI must emit this)

Before submission, the AI must output this short memo (do not omit; it speeds up review):

- **Summary (one paragraph)**: what changed / input-output / invalid input behavior / boundaries
- **Cohesion check**: list changed units, add a one-sentence description, and assign a cohesion type (use the worst type)
- **Coupling check**: list new dependencies and assign a coupling form (use the worst form)
- **Boundary check**: core does not depend on outer types; dependency direction is inward
- **Tests**: commands executed and results

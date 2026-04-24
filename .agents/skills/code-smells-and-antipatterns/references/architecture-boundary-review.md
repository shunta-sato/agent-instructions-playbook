# Architecture boundary review

Use this reference only for boundary changes in the current diff. The goal is to detect new or worsened leakage across layers, not to redesign the whole application.

## External dependencies and services

External systems change independently from the codebase. Keep their details at the edge.

- Do not spread external library, SDK, framework, DB, queue, or service types through core code.
- Put a thin wrapper or adapter around external calls and unify call shapes, error shapes, timeout behavior, and retry policy there.
- Place tests near the boundary when behavior depends on the external system. Keep core tests free of DB/network/UI setup.
- Mark non-obvious boundary crossings with a short contract comment: assumptions, failure modes, and why the boundary is crossed there.

## Module and class boundaries

Modules and classes should have one clear reason to change.

- If a name starts needing "and", responsibilities are likely mixed.
- Keep public surfaces small and stable.
- Keep high-level policy independent from low-level implementation details.

## Clean Architecture checks

The stable core rules should not depend on volatile outer layers such as UI, DB, frameworks, generated clients, or vendor SDKs.

### Core isolation

- Treat frameworks as plumbing. Core code should not need framework annotations or framework request/response types.
- Treat UI as an adapter. Core logic should run and be testable without a UI process.
- Treat persistence as replaceable. Map between domain shapes and DB/ORM models at the boundary.
- Treat external services as replaceable. Translate SDK details and failures into core-friendly results or domain-level errors.

### Dependency direction

- Imports/includes should point from outer layers toward inner layers.
- Inner layers must not import controllers, DB implementations, framework packages, SDK models, generated clients, or UI types.
- If inner code needs an outer capability, define a small port/interface in the inner layer and implement it outside.

### Practical layer sketch

- Core rules: domain objects and invariants.
- Application flow: use-case orchestration from input to processing to output.
- Adapters: controllers, presenters, repositories, serializers, and translators.
- Infrastructure: frameworks, DB drivers, message queues, SDKs, and wiring.

### Crossing boundaries

Use dependency inversion when inner code needs outer capabilities.

- Inner layer: define a small interface such as `UserRepository`.
- Outer layer: implement it as `SqlUserRepository`, `HttpUserRepository`, or another concrete adapter.
- Wiring: connect concrete dependencies at the entry point, bootstrap, or composition root.

### Boundary data

Data crossing a boundary should be a simple DTO-style structure.

- Do not pass framework objects, ORM rows, SDK models, HTTP requests/responses, or generated client objects inward.
- Do not leak rich domain objects outward if outer layers will mutate or serialize them according to framework/DB concerns.
- Convert at the boundary and keep conversion code near the adapter.

### When to draw boundaries

Boundaries have cost. Draw them where change patterns differ.

- Prioritize seams where UI, DB, external service, or framework changes should not force core changes.
- It is acceptable to start with an interface inside one module before splitting files or packages.
- Avoid adding abstraction only because a theoretical future variant might exist.

## Concurrency boundary note

Concurrency primitives are also boundary details when they shape ownership or ordering.

- Reduce shared state; if state must be shared, give it a single owner.
- Do not scatter locks, queues, channels, or schedulers across unrelated responsibilities.
- Make single-threaded logic clear first, then isolate concurrency orchestration at the edge.

## Smallest fixes

- Move an SDK/framework import from core code into an adapter.
- Add a small port/interface in the inner layer and implement it outside.
- Introduce a DTO or mapper at the boundary instead of passing outer types inward.
- Centralize error translation at the wrapper so vendor failures do not leak through the core.
- Add a focused boundary test near the adapter instead of making every core test set up external I/O.

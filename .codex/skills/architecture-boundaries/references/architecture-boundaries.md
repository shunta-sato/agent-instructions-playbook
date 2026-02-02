## 14. Dependencies and boundaries (external libraries and services)

External things change. When external constraints leak inward, the reading burden grows.

- Do not spread external libraries everywhere. Put a thin wrapper around them and unify call shapes and error shapes.
- Place tests at the boundary. If boundary behavior is covered, inner tests can stay simple.
- Mark boundary crossings in code: add a short comment that states the contract (assumptions, failure modes, and why the boundary is crossed here).

## 15. Classes and modules

Have one reason to change. Avoid gathering unrelated changes into one place.

- If responsibilities grow, split. If a name starts to want an “and,” it is time to split.
- Keep the public surface small (public API).
- Stabilize dependency direction so high-level policy is not broken by low-level detail changes.

## 16. Design and architecture (Clean Architecture)

The goal of design here is to protect the stable core rules from the outer layers that change often (UI, DB, frameworks). The more you protect the core, the easier it becomes to test and the more resilient it is to change.

### 16.1 Keep the core isolated from volatile details

This section is a high-level summary. For the primary sources, see `REFERENCES.md`.

- Treat frameworks as plumbing: the core should compile without framework-specific annotations and types.
- Keep UI as an adapter: the core should run and be testable without any UI process.
- Treat persistence as replaceable: map between domain shapes and DB/ORM models at the boundary.
- Wrap external services: keep SDK/client details at the edge, and translate their failures into domain-level errors.
- Make the core easy to test: unit tests for core logic should run without DB/network/UI; integration tests live near boundaries.

### 16.2 Keep dependency direction pointing toward the core

The inner layer must not import from the outer layer.

- Imports/includes should point from outer → inner. Inner layers must not depend on outer layers.
- Convert outer data formats (HTTP requests, DB rows, SDK models, etc.) at the boundary before crossing inward.
- If the core needs an outer capability, define an interface/port in the core and implement it outside.

### 16.3 Minimal layer sketch

A practical mental model is a few layers with clear responsibilities:

- **Core rules**: domain objects and invariants (stable policy).
- **Application flow**: use-case orchestration (“input → process → output”).
- **Adapters**: translation between core shapes and outer shapes (controllers, presenters, repositories, etc.).
- **Infrastructure**: frameworks, DB drivers, message queues, SDKs; mostly wiring/glue.

### 16.4 Crossing boundaries

If the inner layer needs outer capabilities (DB persistence, sending mail, etc.), define a “port” in the inner layer and implement it in the outer layer. This is the **Dependency Inversion Principle (DIP)**.

- Inner: define a small interface such as `UserRepository`
- Outer: implement it as `SqlUserRepository`
- Wiring: connect dependencies at the entry point (main / bootstrap)

### 16.5 Data transfer

Data crossing boundaries should be simple structures. A **Data Transfer Object (DTO)** is enough.

- Do not pass inner objects outward as-is (UI/DB concerns will leak in).
- Do not pass “convenient outer types” inward as-is (HTTP request/response, ORM rows, generated models).

### 16.6 When to draw boundaries

Boundaries have cost. Do not split aggressively up front. Draw lines where change patterns differ.

- Prioritize boundaries where change patterns differ: “UI changes,” “DB changes,” “external service changes,” etc.
- Start by defining interfaces inside one module so that you can split later when needed.

Example: For a Web API, a Controller receives input and passes it to the inner procedure using “inner shapes.” Convert DB/HTTP types at the boundary.

## 17. Concurrency (only when needed)

Concurrency can easily introduce bugs. Design for clarity first.

- Reduce shared state. If you must share, centralize it.
- Do not scatter concurrency primitives (locks, queues, channels, etc.) across responsibilities. Separate concerns.
- Make single-threaded logic correct first; parallelize last.


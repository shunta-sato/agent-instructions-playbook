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

### 16.1 Aim for independence

Use these five goals as guidance. You do not need to satisfy all of them from the start, but they are useful decision axes.

- Independent of frameworks. Frameworks should be swappable tools.
- Independent of UI. Whether Web or CLI, the core processing should not change.
- Independent of databases. Changing DB type or ORM should not break the core.
- Independent of external services. Do not leak outside concerns inward.
- Testable. You should be able to test the core without UI or DB.

### 16.2 Align dependency direction

Core code should not know names or types from outer code. This is the **Dependency Rule**.

- Imports/includes should point from “outside → inside.” Inner layers must not depend on outer layers.
- Do not bring outer data formats (HTTP request types, DB row types, etc.) into the inner layer. Convert them at the boundary into shapes that fit the inner layer.

### 16.3 A rough layer guide

As a minimal breakdown, think in four layers, often explained as **Four Concentric Circles**.

- **Center**: business rules (Entities)  
  The most stable rules: what is allowed, what is forbidden, etc.
- **Next**: application steps (Use Cases)  
  A place to assemble “input → process → output” independent of UI/API.
- **Next**: translation and connection (Interface Adapters)  
  Web entry points, view formatting, DB access translation, etc. Convert between inner and outer shapes.
- **Outer**: mechanisms and tools (Frameworks & Drivers)  
  Web frameworks, DB drivers, message queues, etc. Mostly “glue.”

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


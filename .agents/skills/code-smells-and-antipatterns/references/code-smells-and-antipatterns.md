# Code smells & anti-patterns (new/worsened only)

## Core principle

Smells are quick surface indicators, not guaranteed problems. The job is to look deeper, confirm context, and avoid overreacting or starting large refactors.

## Triage rubric (impact)

- **blocker**: increases coupling across boundaries, introduces “global” state, creates a hard-to-test design, or hides failure behavior.
- **important**: makes change-locality worse (shotgun surgery), adds unclear branching/flags, or makes ownership unclear.
- **nice-to-have**: readability-only improvements not required for correctness.

## Smell / anti-pattern catalog (compact)

### Bloaters

- **Long Method**
  - Symptom: a single function grows with multiple responsibility blocks.
  - Typical risk: harder to isolate failure paths and to test.
  - Smallest remediation: split into cohesion paragraphs or helper functions.
  - Fix lens: `$code-readability`.
- **Large Class**
  - Checkable definition: >400 lines, OR >7 public methods, OR ≥3 distinct reasons to change (same threshold as `$design-balance`).
  - Symptom: class gains unrelated fields/method groups or becomes a hub.
  - Typical risk: god-object drift and unclear ownership.
  - Smallest remediation: write a responsibility map, then split, merge, or rename along reason-to-change boundaries.
  - Fix lens: `$design-balance`.
- **Long Parameter List**
  - Checkable definition: >4 parameters.
  - Symptom: new methods or constructors add many parameters, especially booleans or config flags.
  - Typical risk: call-site errors and unclear intent.
  - Smallest remediation: introduce a request/params object with named fields.
  - Fix lens: `architecture-boundary-review.md`.

### Change preventers

- **Shotgun Surgery**
  - Symptom: a single change requires updates across many files/modules.
  - Typical risk: error-prone updates and missed edge cases.
  - Smallest remediation: centralize the responsibility or add a single choke point.
  - Fix lens: `modularity-cohesion-coupling.md`.
- **Divergent Change**
  - Symptom: one module changes for many unrelated reasons.
  - Typical risk: unstable boundaries and high cognitive load.
  - Smallest remediation: split along reason-for-change boundaries.
  - Fix lens: `modularity-cohesion-coupling.md`.

### Coupling smells

- **Message Chains**
  - Symptom: long chains of calls to reach data or behavior.
  - Typical risk: brittle coupling to internal structures.
  - Smallest remediation: add a method closer to the data to shorten the chain.
  - Fix lens: `modularity-cohesion-coupling.md`.
- **Feature Envy / Inappropriate Intimacy**
  - Symptom: logic lives far from the data it manipulates.
  - Typical risk: hidden dependencies and duplication.
  - Smallest remediation: move behavior closer to the data owner.
  - Fix lens: `modularity-cohesion-coupling.md`.

### Design / architecture anti-patterns

- **God Object (Blob)**
  - Symptom: one class orchestrates many unrelated responsibilities.
  - Typical risk: single point of failure and low testability.
  - Smallest remediation: write a responsibility map, then extract only collaborators with distinct reasons to change.
  - Fix lens: `$design-balance` + `$implementation-economy`.
- **Anemic Domain Model**
  - Symptom: domain objects are just data holders; all logic in services.
  - Typical risk: weak invariants and duplication.
  - Smallest remediation: move one key invariant or behavior onto the domain type.
  - Fix lens: `modularity-cohesion-coupling.md`.
- **Big Ball of Mud**
  - Symptom: blurred boundaries and mixed layers in the same module.
  - Typical risk: cascading change cost and hidden dependencies.
  - Smallest remediation: re-establish one boundary with explicit DTOs or interfaces.
  - Fix lens: `$design-balance` + `architecture-boundary-review.md`.

## “Smallest fix” playbook

- Split into cohesion paragraphs + intent comments → `$code-readability`.
- Move behavior to reduce “envy”/chains -> `modularity-cohesion-coupling.md`.
- Map module/class responsibilities before extracting collaborators -> `$design-balance`.
- Delete, inline, or justify extra helpers/wrappers -> `$implementation-economy`.
- Introduce DTO/interface at boundary and fix dependency direction -> `architecture-boundary-review.md`.
- If touching legacy unsafe area: write characterization tests first → `$working-with-legacy-code`.
- When change affects runtime behavior: add correlation-friendly logs/metrics → `$observability`.

## Do not do this (anti-goals)

- No giant refactors just to satisfy a smell label.
- No “cleanup-only” commits that balloon diffs.
- Do not add new abstractions that hide control flow without clear benefit.

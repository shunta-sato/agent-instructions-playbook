---
name: code-smells-and-antipatterns
description: "Review the current diff for new or worsened maintainability/design issues: code smells, architecture boundary leaks, weak cohesion, and risky coupling. Use for structural changes, public APIs, adapters/integrations, or design review; avoid generic full-codebase audits."
metadata:
  short-description: Diff-focused maintainability review
  resources:
    - references/architecture-boundary-review.md
    - references/code-smells-and-antipatterns.md
    - references/finding-template.md
    - references/modularity-cohesion-coupling.md
---

## Purpose

This is the parent skill for diff-focused maintainability review. It finds only issues introduced or worsened by the current diff: code smells, design anti-patterns, architecture boundary leaks, and modularity/coupling regressions.

Do not turn this into a full-codebase audit. Read unchanged code only as needed to understand whether the diff made the design worse. Root cause / design pressure must be inferred only from the current diff and the minimal unchanged context needed to judge whether the diff worsened the design. Do not expand into history research or full-codebase analysis.

## When to use (trigger conditions)

Agents MUST use this skill when any of the following applies:

- New module/subsystem or new main class is introduced.
- A change introduces or edits public APIs or cross-module boundaries.
- A change adds or changes a DB, HTTP, framework, SDK, queue, filesystem, or service boundary.
- A change increases indirection, flags, config branching, shared state, or manager/service hubs.
- A refactor moves logic across files or layers (controller/usecase/domain/adapters/etc.).
- Review request explicitly mentions smells, anti-patterns, architecture boundaries, modularity, cohesion, coupling, god object, big ball of mud, anemic domain model, or shotgun surgery.

If none applies, do not force it.


## Boundary with function-design skills

This skill is **not** the primary function-boundary design mechanism.

- If findings require deciding module/class responsibility layout, layer count, or name/responsibility alignment, route to `$design-balance`.
- If findings require reducing excess helpers, wrappers, adapters, or unjustified abstractions, route to `$implementation-economy`.
- If findings require deciding keep/rename/split/merge/replace/inline/no-op for functions, route to `$function-boundary-governor`.
- If replacing a flawed abstraction requires temporary red-state migration, route to `$destructive-refactor`.
- Keep this skill focused on diff-level maintainability/boundary/coupling findings.

## References

Open only the reference material that matches the diff:

- `references/code-smells-and-antipatterns.md` for smell labels, impact, and smallest fixes.
- `references/architecture-boundary-review.md` for dependency direction, ports, adapters, DTOs, and boundary leaks.
- `references/modularity-cohesion-coupling.md` for cohesion and coupling checks.
- `references/finding-template.md` for the expected review shape.

## How to use (procedure; must be stepwise)

1) Identify the **units** impacted by the diff (files + key functions/classes).
2) Identify new imports/dependencies and any boundary crossings changed by the diff.
3) Scan for **new or worsened** issues only:
   - smell/design anti-pattern: use the smell catalog;
   - boundary issue: check dependency direction, type leakage, DTOs, wrappers, and error translation;
   - modularity issue: describe each changed unit in one sentence, then check worst cohesion/coupling form.
4) Produce **up to 3 findings**, each with:
   - label (smell, anti-pattern, boundary issue, or modularity/coupling issue)
   - why this looks like it (evidence from the diff)
   - design pressure / likely root cause in this diff
   - scale: local | module | cross-boundary
   - risk if left as-is
   - smallest coherent fix (or explicit route to function-design skills)
   - fix lens/reference or existing narrower skill to apply
5) If you choose NOT to fix now, state:
   - why it is not new/worsened, or
   - why fixing now would increase risk, and
   - what to monitor (tests/metrics/logs) until a planned follow-up.

## Output expectation

Strict format.

Require the output to include:

```markdown
## Smells & Anti-patterns Review
- Scope: (changed units)
- Findings: (0–3 items)

### Finding N: (type: smell|design anti-pattern|architecture boundary issue|modularity/coupling issue; impact: blocker|important|nice-to-have)
- Introduced/Worsened by this diff?: yes|no
- Evidence (diff-level):
- Design pressure / likely root cause in this diff:
- Scale: local | module | cross-boundary
- Why it matters here:
- Smallest fix:
- Fix lens/reference:
- If not fixing now (only allowed if not introduced/worsened): justification + follow-up note
```

If there are 0 findings:
- State: "No new/worsened maintainability issues found" and list what you checked.

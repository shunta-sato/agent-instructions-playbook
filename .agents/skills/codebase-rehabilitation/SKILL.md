---
name: codebase-rehabilitation
description: "Diagnose and refactor an already degraded repository or subsystem whose duplicated rules, obsolete paths or tangled ownership obstruct real maintenance. Not permission for an unbounded rewrite."
---

# Rehabilitate a codebase without losing its contract

The goal is easier correct change, diagnosis and operation, not fewer lines or a prettier
score. Use `code-health` principles; a specific rewrite request changes scope, not safety.
A diagnosis-only request permits inspection, not edits, deployment or data migration.

## Establish the bounded repair and evidence

Reuse preflight agreements and inspect current instructions, callers, tests, operating facts
and recent change/failure history. Agree on the painful subsystem and a representative next
change or diagnosis. Separate supported behavior to preserve, explicitly retired behavior,
known bugs to fix under their own accepted expectations, and unresolved obligations.
Repository search alone does not establish that external consumers do not exist. Ask only
for material scope/compatibility/authority decisions, not routine implementation choices.

Demonstrate the required verification environment before substantial restructuring. Add
characterization at the actual public/CLI/API boundary when coverage is missing. Capture
error semantics, persistence/restart and important NFRs as applicable. Existing bugs are
observations, not automatically permanent requirements. Record baseline failures separately;
neither erase them nor claim equivalence from tests that already fail. A missing required
E2E path limits repair readiness and must be raised early, not at final submission.

Use `scripts/inspect_code_health.py` as an optional READ-ONLY locator for tracked Python
code in explicit paths; it does not import project code, install tools or modify files.
For other languages use the project's existing pinned analyzers and the same evidence
principles. Inspect its limitations before treating a signal as a finding. Do not scan
secrets, third-party trees or the whole repository merely because it is possible.

## Select a semantic repair, not a cosmetic campaign

Use `references/repair.md` for diagnosis and acceptance examples. Choose a bounded target:
one owner for a duplicated rule, a simpler supported execution path, removal of a proven
obsolete contract, or separation of concerns that actually change independently. Explain
which burden will disappear and what must remain. Prefer existing abstractions; replacing
one maze of wrappers with a generic framework is not a repair. Preserve useful rationale,
public usage, safety boundaries and justified duplication/compatibility.

Refactor in coherent, verifiable slices. The relevant ownership boundary, not an arbitrary
file/line cap, determines slice size. Coordinate shared owners before parallel work. A larger
replacement may be appropriate when it is explicitly authorized and bounded proof/recovery
exist; neither insist on a big-bang rewrite nor forbid a necessary one. Temporary local Red
is acceptable while converging, never as release evidence. Reuse `boundary-migration` for
actual contract retirement and `bug-investigation-and-rca` when the cause is still unclear.

## Prove the repair and stop

On the final candidate, exercise preserved behavior and agreed changes, required NFRs, and
any explicitly retired surface. Check affected callers, generated/dynamic entrypoints and
known external consumers. Make a representative next change or diagnosis in a disposable
worktree when needed to substantiate the claimed maintainability improvement; compare the
same task and maintainer conditions before/after. Do not ship the drill's hypothetical feature.

Record concrete before/after burden and source/test identities in the existing PR. Analyzer
counts are diagnostic, not an automatic pass; a lower score never excuses lost behavior,
weaker errors, deleted tests or a required compatibility break. If improvement is inspection-
only, say so rather than claiming a measured speedup. Stop when the selected burden is
resolved and required proof passes. Leave unrelated debt and optional preferences alone.

If proof or authority is blocked, report what is ready and what cannot yet be claimed.
Do not call a partial repair complete, bypass access controls, or relabel missing proof.
After the repair, apply ordinary code-health prevention; do not keep a permanent cleanup loop.

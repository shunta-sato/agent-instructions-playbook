# Use the playbook to repair existing slop

This capability is a reusable repair Skill and a small inspection/evaluation toolset. It
does not silently choose or rewrite another personal/company repository. Select the target
repository/subsystem and its actual painful change before running a repair Agent.

## Example request

```text
$codebase-rehabilitation

The settings subsystem has duplicated validation and obsolete compatibility code.
Diagnose its actual ownership and supported consumers, then propose the bounded repair.
Preserve public API and persisted data; internal restructuring is allowed. Ask before
changing unresolved external compatibility obligations. Characterize the real CLI/API
behavior and establish the E2E environment before substantial refactoring. Keep useful
error/ordering rationale. After repair, verify both the original contract and a disposable
follow-up rule change. Do not implement unrelated features or pursue a numeric slop score.
```

The substantive repair request authorizes agreed internal edits; it does not authorize
production access, data deletion, paid services or unknown compatibility breaks. Diagnosis-
only requests stay read-only. Use the Preflight conversation to resolve material unknowns.
Keep the existing PR/task as the decision record instead of generating a new document pack.

## Before / intervention / after

Record the current candidate, supported behavior, known failing checks and proof limits.
Use current E2E/public-boundary characterization; tests that encode an accidental bug do
not make it a perpetual requirement. Separate intentional behavior corrections from the
refactor and keep an independent expected-outcome check in addition to before/after parity.

Select a coherent semantic slice with a stop condition: remove one duplicate owner or a
verified obsolete path, reduce a specific diagnostic/change burden, preserve all obligations.
Coordinate shared owners before parallel work. Do not let file ownership force copied rules.
Larger authorized replacements are possible when the evidence and recovery scope justify
them; this is not a blanket ban on destructive refactoring or an instruction to rewrite all.

On the final candidate, validate actual caller behavior, errors, persistence, retirement
and applicable NFRs. Where improvement needs demonstration, repeat the SAME maintenance
operation before/after in disposable worktrees with a fixed maintainer model/harness. The
changed test feature stays out of the production patch. Report actual evidence and residual
limitations; a lower metric alone proves neither safety nor maintainability. Stop at the
agreed burden, not zero smells across the repository.

## Read-only Python inspection

After installing `core` plus `maintenance` into a project using native `.agents/skills`:

```sh
python3 /path/to/project/.agents/skills/codebase-rehabilitation/scripts/inspect_code_health.py \
  --root /path/to/project --path src/settings --kind product
```

Select literal relative paths and run separate scans for product/test/generated categories.
The tool reads tracked Python files without importing/executing them; no dependency install,
repair or deletion. It records source hashes, Python/analyzer versions, physical line spans,
branch-statement counts and exact AST clone candidates. These are not Erosion, CC, SLOC,
semantic duplication or a Slop Score. Exit 0 means the selected diagnostic scan completed,
not that a repository is healthy. Empty/missing/error/symlink inputs fail rather than imply
cleanliness. Untracked/ignored/non-Python code is outside the reported scope. Interpret
matches against real contracts, particularly external consumers absent from local search.

## Executable example and limits

The `rehabilitation` evolution scenario starts with actual duplicated storage modules and
an obsolete alias, while `public_v1.read_value` is used by a simulated off-repo consumer.
The functional oracle rejects the obsolete path's survival, a broken external contract,
missing persistence and one-entrypoint-only normalization. A correct reference transformation
is exercised by offline tests; it is not a live autonomous rehabilitation result.

The shared evolution runner preserves candidate code across repair and subsequent change.
Read `evals/evolution/README.md` for isolation, trusted oracle/adapter boundaries, protocol 2,
matched model/team configurations and pending design review. No new model API execution,
real target-repository refactor, generic multi-agent adapter or browser UI extension is
claimed by these tests. Existing prototype Web Console remains separate.

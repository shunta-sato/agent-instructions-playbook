# Bounded repair decisions

A repair brief can be a few lines in the task/PR: painful change -> affected owners ->
preserve/retire/fix/unknown -> proposed target -> proof -> stop condition. It is not a new
per-file ledger. Read known answers first. Do not ask the user to choose design mechanics
when the existing constraints already decide them.

## Examples

- Two adapters own the same validation policy: characterize both entrypoints, move only
  their shared policy to its owner, preserve distinct transport errors, then exercise a
  changed policy through both. Same-looking independent policies need not be merged.
- A legacy facade looks redundant: distinguish an unused internal alias approved for
  removal from a public compatibility function used outside this checkout. Remove the
  former and test the latter with an independent consumer. Never infer absence from grep.
- A central module mixes persistence, formatting and retry policy: choose boundaries by
  independent reasons to change and actual lifetime/side effects, not a function-size quota.
- Many comments explain mechanics: remove narration while retaining ordering hazards,
  protocol exceptions, licenses and public usage. A meaningful explanation can be long.

## Inspection tool

```sh
python3 scripts/inspect_code_health.py --root /path/to/repository --path src/component --kind product
```

Run from this Skill's directory, or use the installed Skill's absolute script path. It is
Python-only, standard-library-only, tracked-file-only and read-only. Paths are literal repo-
relative paths, not globs. Run separately for product, test and generated scopes using
`--kind product|test|generated`; do not dilute one category's signals with another's files.

Output binds file bytes to SHA-256 and records Git HEAD, analyzer version/source digest and
Python version. HEAD alone is not the analyzed working tree; dirty files have their own hashes.
Function line spans and branch-statement counts are NOT cyclomatic complexity, Erosion or
SLOC. Exact AST clone candidates ignore only a function's declared name and location, retaining
literals, decorators, argument names and body. A match is not semantic equivalence; a miss
is not proof that no duplication exists. Comments are neither scored nor deleted.

Syntax errors, symlinks, missing tracked files and empty selections return an incomplete
result/nonzero exit. Untracked/ignored/non-Python files are not analyzed. No clean-repository
or maintainability claim can be inferred from exit 0. Inspect actual code and constraints.
The tool does not run project imports, tests, hooks or repairs. Existing language-specific
formatters, linters and profilers remain the right tools for their own jobs.

## Acceptance and recovery

Characterization protects the supported contract, not every accidental bug. A behavior
correction needs an accepted expected result; keep it distinguishable from a behavior-
preserving refactor. Differential comparison can preserve a bug in both versions, so use
independent expected outcomes too. Bind performance comparisons to matching workloads,
targets, build modes and methods. Keep realistic errors and diagnostic meaning observable.

When a change drill is used, compare the SAME follow-up request before/after under the same
maintainer model/harness, including recovery and review effort. Keep the actual code and
failures; never swap in a clean reference repository between steps. A current functional
pass alone does not establish easier maintenance. Missing authority/evidence stops only
dependent work; a Draft PR may share findings without claiming completion.

# Evidence for code-health decisions

These are decision examples, not a mandatory checklist or per-function ledger.

| Signal | Ask | Counterexample to preserve |
| --- | --- | --- |
| Another similar implementation | Is one rule now independently owned in multiple places? | Similar syntax implementing independent policies |
| Compatibility shim or fallback | Which real caller/data/update obligation needs it? | Public consumers not discoverable by local search |
| Extra abstraction/configuration | Does it hide a current decision or merely add indirection? | A security boundary, lifetime owner or measured hot path |
| Long comment | Does it preserve reasoning unavailable from the code? | Hazard, ordering invariant, API usage or license notice |
| Growing complex function | What future change must now understand unrelated concerns? | Necessary complexity kept at one coherent boundary |
| Many passing tests | Do they catch the failure or copy the implementation? | Focused UT plus real acceptance evidence |

Prefer a falsifiable finding: "The retry rule lives in A and B; changing it in A leaves B
inconsistent. Move the common decision to existing owner C; preserve separate transport
errors." Avoid "too many files" or "use a factory" without a relevant scenario. Explain
why an apparent smell is accepted when that matters; do not write a defense for every line.

LOC, clone detectors and complexity are inspection signals, not optimization targets. Pin
analyzer/rule versions, retain absolute counts and separate product code, tests, generated
assets and disposable probes. Do not dilute a ratio with unrelated code, split functions to
win a metric, delete tests, or sacrifice diagnostics/security to make a score green.

When static inspection cannot resolve an important trade-off, compare bounded alternatives
against the SAME behavior, workload and proof. A change drill uses a real likely maintenance
operation (e.g. change one rule through all supported entrypoints). It does not require
anticipating undisclosed future requirements or installing a new framework in production.
Assess what must be understood, changed and reverified, not only files changed. Keep the
maintainer model/harness fixed across candidates to distinguish design quality from brute force.

## Team handoff example

"Expose the existing save policy through the batch CLI. Keep normalization in the current
settings owner; internal restructuring is allowed. Preserve the published file format and
error semantics. Prove CLI -> persistence -> separate-process read and the original CLI's
regressions. Report a conflicting ownership boundary rather than copying the rule to stay
inside a file assignment."

No required template: the information may already exist in the task and code. The supervisor
owns integration and may revise its own plan; worker obedience is not design-quality proof.

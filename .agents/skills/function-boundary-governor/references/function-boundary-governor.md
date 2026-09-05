# Function Boundary Governor

## Required discovery

After confirming a SKILL.md trigger, inventory the affected boundary, not every
function incidentally formatted or touched. Identify relevant callers and search
semantic neighbors by domain concept, invariants, effects, errors, and tests.
Classify neighbors as `same concept | parallel concept | obsolete abstraction |
uncertain`. Resolve module ownership through `design-balance` only when needed.

## Evidence-based decision rule

Use these questions, with evidence from callers, code, tests, or a stated
requirement. Do not calculate scores, totals, or numeric approval thresholds.

- **Present benefit:** what current responsibility, defect, duplication, or
  call-site difficulty does the change resolve? Why is the existing/local design
  insufficient for this task?
- **Contract:** which inputs, outputs, invariants, error behavior, side effects,
  and supported callers must remain compatible? Is any change explicitly allowed?
- **Boundary:** who owns each invariant/effect afterward, and is the resulting
  concept clearer without mode flags or unnecessary indirection?
- **Proof:** which characterization/regression tests, caller migration checks,
  and convergence/rollback evidence demonstrate the result?

Proceed when the current benefit is concrete, the relevant contracts are
preserved or explicitly waived/staged, and the required proof is available.
Unknown safety or compatibility evidence is not a low score to average away.
For an optional refactor, choose no-op when benefit or proof is insufficient.
For a required fix, obtain the missing proof or report the exact blocker; a
no-op does not complete an unmet acceptance condition.

## Decision rules

- **Merge** only for the same domain concept and compatible invariants, errors,
  effects, and callers, with a current simplification benefit. Fewer lines alone
  is not evidence. Prove migration and remove superseded paths as required.
- **Split/replace** when a concrete responsibility or side-effect boundary is
  wrong. Preserve behavior under the recorded mode, migrate callers, and use
  `destructive-refactor` for replacement/convergence when applicable.
- **Keep parallel** when error behavior differs, side effects differ, or distinct
  invariants/reasons to change justify independent implementations. A breaking
  waiver does not make different concepts identical.
- **Keep/no-op** when the boundary already works or the proposed gain is
  speculative. Explicit boundary review still requires its relevant discovery.
- **Rename/inline** when the current concept becomes clearer without shifting
  contracts or introducing another abstraction.
- **Delete** only with no remaining required callers; honor external compatibility
  obligations except where the requester's recorded waiver explicitly applies.

## Review prompts, not a second gate

Concept clarity, single reason to change, invariant ownership, and
call-site readability help explain a decision, along with side-effect control,
error behavior, and test protection. Abstraction cost, duplication risk,
future divergence likelihood, boundary crossing risk, public API churn, and
parameterization pressure identify questions to investigate, not numbers to
manufacture.

## Mandatory reject signals

Reject merging when similarity is textual only: callers require different
invariants, error behavior, effects, or reasons to change. A shared test shape
or similar body is not proof that the concepts are the same.

Reject or revise a proposed abstraction when:
- it needs vague names (`common`, `util`, `helper`) to conceal its responsibility;
- boolean flags/options switch between unrelated semantic contracts;
- call sites become harder to read without a required boundary benefit;
- tests are insufficient to establish safe migration;
- it violates authorization or the recorded compatibility mode.

Useful local helpers, domain flags that actually belong to the contract, and
justified security/resource boundaries are not prohibited by these signals.

## Required evidence log

For the affected boundary, reuse the plan/PR or required ledger to capture the
concept/invariants, callers, side-effect profile and error contract, chosen
action, important rejected alternative, and actual verification. A numeric
worksheet and per-function comments are not evidence requirements.

Record temporary adapters and their removal conditions. Under `break-allowed`,
back obsolete-name cleanup with `scripts/check_api_removal.py` evidence. Keep
intentional parallel concepts distinct from unremoved superseded APIs.

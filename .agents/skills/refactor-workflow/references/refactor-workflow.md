# Refactor-workflow checklist

For `$refactor-workflow` only. This is a composition lane, not a new mechanism —
every structural-change stage cites the part-skill that owns it. Run the stages
in order; do not skip stage 1 for "obviously safe" changes.

## Stage table

| Stage | Action | Owning part-skill | Evidence produced |
| --- | --- | --- | --- |
| 0 | Record intent + compat-mode | `dev-workflow` step 1b (compat-mode owner) | `intent: refactor` + compat-mode value |
| 1 | Behavior lock | full-suite baseline; `$working-with-legacy-code` if unreliable/absent; `$unit-test-design` sizes any characterization test | green baseline command + result |
| 2 | Structural change | `$function-boundary-governor` / `$design-balance` / `$destructive-refactor` / `$project-structure` (pick the one matching scope) | the owning skill's decision record |
| 3 | Equivalence evidence | this skill | unchanged-and-green tests; listed test edits; no-new-behavior statement; break-allowed sweep |
| 4 | Anti-pattern check | this skill | anti-pattern list reviewed, none present |
| 5 | Handback | `dev-workflow` / `$quality-gate` | structure watch, verification depth, gate decision |

## Stage 0 — intent + compat-mode

- Record `intent: refactor` where `dev-workflow` step 1a is recorded.
- Record compat-mode by citing the `dev-workflow` step 1b value already in force. Do not
  restate the `preserve` / `staged` / `break-allowed` definitions here — that text is
  owned by `dev-workflow`.
- If compat-mode is not yet recorded, stop and request it from `dev-workflow` step 1b
  before touching any file.

## Stage 1 — behavior lock (mandatory, first)

- Run the full test suite for the touched area and record the command + result as the
  baseline. A refactor with no recorded green baseline has no equivalence evidence later.
- If the touched area's tests are unreliable, slow, flaky, or absent, do not proceed to
  stage 2. Open `$working-with-legacy-code` and add characterization tests first; use
  `$unit-test-design`'s E/S/H tiers to size how much characterization coverage the area
  needs (cite the tier and its one-line justification, do not restate the risk formula).
- "The change looks obviously safe" is not a reason to skip this stage.

## Stage 2 — structural change (pick exactly one lane per scope)

Route to the one part-skill that owns the scope of this structural change:

- Function, helper, or API boundary reshaping (split/merge/rename/inline/delete a
  function or call-site contract) → `$function-boundary-governor`.
- Module/class responsibility layout, a new layer, or reassigning a reason-to-change →
  `$design-balance`.
- Replacing a flawed abstraction end-to-end, where call sites must migrate through a
  temporary red state → `$destructive-refactor`.
- Physical file/module/package layout (new file, split, move) → `$project-structure`.

Do not perform the structural edit directly inside this skill — invoke the owning part
and record its output. New tests are not written for behavior that only moved; the
stage-1 lock already covers it. Any new abstraction the refactor introduces (a new
wrapper, adapter, or helper) still needs `$implementation-economy` justification.

## Stage 3 — equivalence evidence (closes the task)

Record all of:
- Pre-existing tests are unchanged and green (re-run the stage-1 suite).
- Test edits are allowed only for symbols that were renamed or moved; list each edit as
  `file — old symbol → new symbol — reason`. Any other test edit is out of scope for this
  lane and signals a behavior change, which belongs to intent `feature`.
- No new public behavior was introduced (state this explicitly, do not assume it).
- Under compat-mode `break-allowed`: run
  `python scripts/check_api_removal.py --symbol <old-name> ...` and record zero hits.
  The staged-migration ledger escape hatch in `$destructive-refactor` applies only under
  `staged`, never under `break-allowed`.

## Stage 4 — anti-patterns to name before declaring done

- A "refactor" PR that changes behavior is a feature change mislabeled as a refactor —
  reclassify intent, do not force equivalence evidence onto it.
- Deleting or weakening a failing test to reach green is forbidden; a failing test after
  a structural change means the change was not behavior-preserving.
- Skipping the stage-1 lock "because the change is obviously safe" is forbidden — the
  lock is what makes stage 3's equivalence claim verifiable at all.
- A big-bang rewrite where `$destructive-refactor`'s staged migration fits is a scope
  error; prefer the staged, call-site-by-call-site path.

## Handback

After stage 4, continue in `dev-workflow`: the structure watch
(`python scripts/check_structure.py <touched files>`), canonical verification at the
routed risk depth, and `$quality-gate`. This checklist's stage-3/4 output feeds the
gate's refactor-branch evidence bullet; it does not replace the gate's own decision.

# UI/UX core contract reference

Use this reference with `$uiux-core` to build and review a deterministic UIUX Pack.

## Core principles (platform-agnostic)

1. Reduce decision points.
2. Design state/error/recovery first.
3. Separate machine-checkable checks from human judgement.
4. Accessibility baseline is a hard constraint, not optional.
5. For agent-driven UI flows, require:
   - capability disclosure
   - preview before execute
   - undo/rollback
   - audit log
   - explain-why for critical actions
   - change notification

## UIUX Pack contract

Create or update all artifacts under `uiux/YYYYMMDD-<slug>/`.

If `uiux/.config` defines `output_dir`, use that override instead of the default path.

Required artifacts:
- `ui_contract.yaml`
- `ui_spec.json`
- `auto_review.json`
- `diff_summary.md`

Determinism rules:
- All four artifacts must exist, even when partially filled.
- Unknown/uncomputed checks must still exist in `auto_review.json` with:
  - `result: "unknown"`
  - `reason_if_unknown` populated.

## Review checklist

### Auto-checkable items (metrics + rules)

- Top-level destination count vs contract limit.
- Decision point count and required rationale (`why_unavoidable`).
- Per-screen primary action count.
- Required global states coverage (`idle/loading/success/failure`).
- Error model includes recovery actions and input preservation.
- Presence of required accessibility fields (labels/roles/focus/target-size/contrast intent).
- Presence of agent-specific safeguards (preview, undo/rollback, audit/change notice, explain-why).

### Human review questions

- Is each screen goal clear and singular?
- Is navigation predictable and reversible for users?
- Are decision points unavoidable and minimized?
- Are error messages understandable, actionable, and trust-preserving?
- Are high-impact actions clearly disclosed and reviewable before execution?
- Is the overall cognitive load lower than before?

## How to write the spec

### Screen definition

Each screen needs:
- user-facing goal
- one primary action
- explicit states (including loading/failure)
- error and recovery behavior

### Navigation definition

Each transition needs:
- `from`
- `to`
- `trigger`

### Decision points definition

Each decision point needs:
- question presented to user
- available options
- reason this decision is unavoidable

## Do not

- Make silent UI changes without clear summary.
- Lose user input on recoverable errors.
- Allow irreversible actions without an explicit review/confirm path.

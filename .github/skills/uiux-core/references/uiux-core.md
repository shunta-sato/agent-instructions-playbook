# uiux-core reference — UI design and review for AI Agent-generated/modified interfaces

This document defines **core (platform-agnostic) design rules** for teams where AI Agents generate/modify UI and humans review before applying changes.  
Differences across Android / iOS / Web are handled by separate platform adapter skills, which override `ui_contract.yaml` and `auto_review.json`.

## Most important premise

As AI changes more UI, **reviewability** becomes the top requirement.  
Reviewability means reviewers can quickly trace: “what changed,” “why,” “scope of impact,” and “how to roll back.”

Always follow these three rules:

- Whenever UI changes, record “what,” “why,” and “how far” in `diff_summary.md`
- Never silently execute irreversible or high-impact actions (include human approval flow in the UI spec)
- Do not bolt accessibility on later (declare it as a requirement in `ui_contract.yaml` from the start)

## Terms used in this document

- **Destination**: a point where users choose where to go next (e.g., main tabs or major menu entries)
- **Primary action**: the single most important action users should take on that screen first
- **Decision point**: a branch where users must choose (e.g., approval before execution, target selection)
- **State**: conditions that switch the UI behavior (e.g., loading/saving/failure/partial success)
- **Recovery**: what users can do after failure (retry, go back, save draft, etc.)

## Work sequence for generate/modify tasks (default order)

1) Fill `ui_contract.yaml` first  
   - Lock target platforms and guardrail rules before implementation details
2) Update `ui_spec.json`  
   - Define screens, navigation, decision points, and states/errors
3) Update `auto_review.json`  
   - Compute and record every automatable check  
   - For checks that cannot be computed, set `unknown` and explain why
4) Update `diff_summary.md`  
   - Keep it short and reviewer-oriented to reduce missed issues  
   - Capture intent, impact scope, rollback method, and open issues
5) If platform-specific behavior exists, invoke platform adapter skill  
   - Adapter only adds `platform_overrides` and PF-specific checks (do not add new artifact names)

## Core design rules

### 1) Do not over-expand destinations and branches

Goal: reduce confusion points so “what to do next” is readable as a single clear path.

Rules:
- Do not increase top-level destinations unless unavoidable; propose consolidation first  
  (limit is defined by `ui_contract.yaml rules.decision_points.max_top_level_destinations`)
- Keep one primary action per screen as the default
- If an exception is needed, document reason and alternatives in `diff_summary.md`
- For important branches (approval/target selection), define them in `decision_points` and explain why unavoidable

Auto checks (examples):
- Count destinations, primary actions, and decision points
- Mark limit violations as `fail`; if exception is documented, mark `warn` and attach evidence

Human checks (examples):
- Can first-time users understand the next action without hesitation?
- Did added destinations split core task flow unnecessarily?

### 2) Keep information order consistent

Goal: prevent important information from being missed under scanning behavior.

Introduce only one key term here:  
Show essentials first, then reveal details as needed → **Progressive disclosure**.

Rules:
- At screen start, briefly state what users can do (title/target/primary action)
- Place content in order: heading → key point → details
- Keep related elements close (value + action, instruction + input, etc.)
- Do not introduce screen-by-screen local style rules (spacing, tone, label naming)

Auto checks (examples):
- `screen.goal` is not empty
- Primary action exists in the screen definition
- Detect empty/duplicate headings and labels where possible

Human checks (examples):
- Is critical information buried?
- Can a reviewer explain the screen purpose in one sentence?

### 3) Design states, errors, and recovery first

Goal: lock fragile areas early so users can still make progress when failures happen.

Rules:
- Define required states per screen/function (at minimum: idle/loading/success/failure)
- Preserve user input through errors and retries
- Error content must include both “what happened” and “what users can do next”  
  (do not show only an error code)
- Explicitly define recovery paths (`recovery_actions`) such as retry/draft/save/back

Auto checks (examples):
- Required states exist in `states_and_errors.global_states`
- `error_model.user_message` and `recovery_actions` are non-empty
- `preserve_user_input` is true

Human checks (examples):
- Do users avoid dead-ends after failure?
- Is rollback/recovery present as a concrete UI behavior?

### 4) Readability and wording consistency

Goal: reduce misinterpretation and lower learning cost.

Rules:
- Use plain UI language; do not rely on internal jargon/abbreviations
- Use the same term for the same meaning across screens
- Error messages should be non-blaming, short, and action-guiding

Auto checks (examples):
- Detect missing labels and empty text where possible
- If a forbidden-terms dictionary exists, flag as `warn` (optional)

Human checks (examples):
- Do key terms allow multiple conflicting interpretations?

### 5) Treat accessibility as a fixed requirement

Goal: avoid excluding users and prevent late-stage breakage.

Rules (core defines policy; numeric thresholds may be overridden by platform adapters):
- Interactive elements must have accessible names/labels and roles
- Provide visible focus/current-location indication
- Use colors with clear text/background distinction (contrast-aware)
- Avoid overly small tap/click targets (minimum size is platform-defined)

Auto checks (examples):
- `components[].a11y.name` and `role` are non-empty
- If minimum target size/contrast cannot be computed, set `unknown` with reason

Human checks (examples):
- Are states (disabled/error/focus) distinguishable?
- Does behavior remain usable with keyboard/screen reader? (detailed PF checks are delegated to adapters)

### 6) AI Agent-specific rules (assume UI can change proactively)

Goal: prevent over-trust and keep humans in control.

Rules:
- State capabilities and limitations up front
- Show a plan preview before important execution so humans can approve
- Provide reject/correct/retry/undo (rollback) paths
- For important decisions, provide concise “why” rationale for review
- Notify behavior changes and keep them traceable (audit/history)

Auto checks (examples):
- `ui_contract.yaml rules.agent_specific.*` is true
- If relevant AI UI exists but plan preview / undo / audit is missing, mark `fail`

Human checks (examples):
- Does AI support human judgment rather than replace it?
- Is explanation useful for decision-making (not post-hoc justification)?

## How to write `auto_review.json` (key point)

- Automated checks are a **filter**, not a guarantee of good UI
- Checks that cannot be computed must be `unknown` with a non-empty reason
- Do not collapse everything into one aggregate score  
  prioritize `pass/warn/fail/unknown` plus evidence

Recommended review flow:
- First read `diff_summary.md` and judge against criteria
- Then read `auto_review.json` to catch misses

## Handling exceptions (important)

Do not hide rule violations.

- If an exception is required, record reason and alternatives in `diff_summary.md`
- In `auto_review.json`, set `warn` or `fail` and keep exception reason in evidence
- In `decision_points`, always fill `why_unavoidable`

## References (primary sources)

These URLs are references. This document remains operational as core rules.

- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- ISO 9241-11: https://www.iso.org/standard/63500.html
- ISO 9241-210: https://www.iso.org/standard/77520.html
- Nielsen 10 heuristics: https://www.nngroup.com/articles/ten-usability-heuristics/
- Guidelines for Human-AI Interaction (Amershi et al.): https://www.microsoft.com/en-us/research/wp-content/uploads/2019/01/Guidelines-for-Human-AI-Interaction-camera-ready.pdf

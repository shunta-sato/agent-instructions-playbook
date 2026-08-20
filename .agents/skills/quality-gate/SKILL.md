---
name: quality-gate
description: "Use before every delivery-mode submission to decide whether required checks, artifacts, and branch evidence are complete enough to submit."
metadata:
  short-description: Final quality gate
  requires:
    - references/quality-gate.md
  resources:
    - references/mobile-test-evidence-matrix.md
    - references/flutter-mobile-test-matrix.md
    - references/react-native-expo-test-adapter.md
    - references/maestro-agentic-verification-policy.md
---

## Purpose

Use this skill as the final submit gate. It answers one question: **is this change ready to submit now?**

## When to use

Invoke this skill before every delivery-mode submission. Research probes use the research evidence gate; promotion into delivery paths re-enters this gate in full.

## How to use

0) Open `references/quality-gate.md` and run its checklist as one complete sweep; never stop at the first failed item.

1) Verify canonical commands are green at the required depth.

1b) Run `python scripts/check_structure.py --working-tree` and apply the no-waiver/no-submit structure rule.

1c) Run `python3 scripts/check_research_evidence.py --working-tree --policy .agents/project-policy.yml --mode delivery`; `safety-review-required` is `no-submit` in every mode.

2) Validate required artifacts/evidence from every triggered branch.
   - For any mobile claim, open `references/mobile-test-evidence-matrix.md` and select evidence from the changed boundary rather than framework preference.
   - For Flutter, also open `references/flutter-mobile-test-matrix.md`.
   - For React Native/Expo, also open `references/react-native-expo-test-adapter.md`.
   - When Maestro, agent-device, Argent, `.ad`, or another device-driving harness contributed evidence, open `references/maestro-agentic-verification-policy.md`.
   - Web/shared tests cannot replace Android/iOS native/runtime evidence. A missing macOS/iOS path remains blocked.
   - `mobile-feature-parity` with missing required platform evidence or `parity-blocked` is `no-submit` for a both-platform completion claim.
   - Runtime evidence marked `pass` without source/build/target/environment identity and an explicit oracle is `no-submit`; screenshot-only or exploratory no-finding evidence is `inconclusive`.

3) Run concise exit-criteria review only. Route deep analysis to its dedicated skill and return.

4) Output `submit` or `no-submit` with all findings.

## Output expectation

- Start with `Gate decision: submit` or `Gate decision: no-submit`.
- If `no-submit`, list each finding with location, missing/failed criterion, and required fix.
- For mobile claims, report shared, Android, iOS, web, and runtime evidence separately as applicable.
- Distinguish regression evidence, target-bound runtime verification, and observation; do not overstate screenshots or agent self-assessment.
- Only output `0 findings` when every exit criterion is satisfied.

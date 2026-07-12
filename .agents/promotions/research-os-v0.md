# Promotion acknowledgment: research-os-v0

Scope: research-os-v0 delivery surface — ledger, runner, mechanical gate, CI wiring, and skill/agent prose.

no research claims promoted

**Nature**: infrastructure. The research-path files in this diff (`experiments/`, `research/claims.md`) are a committed worked example and generated view; no delivery system's runtime behavior depends on them.

**Evidence**: ledger verified by `check_research_evidence.py --check-ledger`; claims C-0001 and C-0002 remain research-scoped, not promoted into delivery behavior.

**Delivery gates applied**: make verify (full chain incl. the ledger gate), full unit test suite, structure budget, supervised multi-worker review with recorded runs, two external PR review rounds addressed (10 findings, then 6 further integrity findings).

**Delivery-run evidence** (R4): the accepted worker `agent_run` records whose changed/allowed files produced this delivery surface.

Delivery-run: 20260712T151808Z-focused_code_change-641da0ad
Delivery-run: 20260712T092212Z-focused_code_change-106d2efe
Delivery-run: 20260712T045229Z-focused_code_change-61aa6c48
Delivery-run: 20260712T050939Z-focused_code_change-cddbc1d0
Delivery-run: 20260712T044653Z-focused_code_change-5d7fa694
Delivery-run: 20260712T044900Z-focused_code_change-2a21efab
Delivery-run: 20260712T075307Z-focused_code_change-5043231d
Delivery-run: 20260705T130846Z-focused_code_change-70a7eadf
Delivery-run: 20260712T083111Z-focused_code_change-e9dbecbf
Delivery-run: 20260712T084343Z-research_probe-da7af946
Delivery-run: 20260712T050309Z-research_probe-76ff117e
Delivery-run: 20260712T165226Z-focused_code_change-19e96118
Delivery-run: 20260712T165530Z-focused_code_change-a87e54f5

Covers:
- scripts/
- tests/
- Makefile
- .github/
- AGENTS.md
- CHANGELOG.md
- README.md
- .gitignore
- evals/
- plans/
- .claude/
- .agents/

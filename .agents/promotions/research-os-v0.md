# Promotion acknowledgment: research-os-v0

Scope: research-os-v0 delivery surface — ledger, runner, mechanical gate, CI wiring, and skill/agent prose.

no research claims promoted

**Nature**: infrastructure. The research-path files in this diff (`experiments/`, `research/claims.md`) are a committed worked example and generated view; no delivery system's runtime behavior depends on them.

**Evidence**: ledger verified by `check_research_evidence.py --check-ledger`; claims C-0001 and C-0002 remain research-scoped, not promoted into delivery behavior.

**Delivery gates applied**: make verify (full chain incl. the ledger gate), full unit test suite, structure budget, supervised multi-worker review with recorded runs, two external PR review rounds addressed (10 findings, then 6 further integrity findings).

**Delivery-run evidence** (R4): the accepted worker `agent_run` records whose changed/allowed files produced this delivery surface.

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

Delivery-run: 20260713T024148Z-focused_code_change-891e05c1
Delivery-run: 20260716T034353Z-focused_code_change-00e0f4af
Delivery-run: 20260716T125226Z-focused_code_change-1ab7bf53
Delivery-run: 20260716T172740Z-focused_code_change-26f5acbc
Delivery-run: 20260717T161601Z-focused_code_change-b3084dd2

# Promotion acknowledgment: research-os-v0

Scope: research-os-v0 delivery surface — ledger, runner, mechanical gate, CI wiring, and skill/agent prose.

no research claims promoted

**Nature**: infrastructure. The research-path files in this diff (`experiments/`, `research/claims.md`) are a committed worked example and generated view; no delivery system's runtime behavior depends on them.

**Evidence**: ledger verified by `check_research_evidence.py --check-ledger`; claims C-0001 and C-0002 remain research-scoped, not promoted into delivery behavior.

**Delivery gates applied**: make verify (full chain incl. the ledger gate), full unit test suite, structure budget, supervised multi-worker review with recorded runs, two external PR review rounds addressed (10 findings, then 6 further integrity findings).

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

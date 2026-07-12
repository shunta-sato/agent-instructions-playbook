# Promotion acknowledgment: research-os-v0

- **Scope of delivery-path changes**: scripts/ (research_run.py, research_ledger.py, check_research_evidence.py, check_structure.py), tests/, Makefile, CI workflow, AGENTS.md and skill/agent prose, .agents/ policy and routing files.
- **Nature**: infrastructure — no research claims are promoted into delivery behavior. The research-path files in this diff (experiments/sort-degradation-probe/, research/claims.md) are a committed worked example and generated view; runtime behavior of no delivery system depends on them.
- **Evidence**: claim C-0001 (digest-fix smoke) remains research-scoped; ledger verified by `check_research_evidence.py --check-ledger`.
- **Delivery gates applied**: make verify (full chain incl. new ledger gate), 77 unit tests, structure budget, supervised multi-worker review with recorded runs, external PR review round (10 findings addressed).

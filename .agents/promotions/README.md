# Promotion acknowledgments

An acknowledgment is the committed record of a research→delivery crossing. Add one `*.md` file here (any name but `README.md`) in the **same diff** that promotes research into a delivery path. It must state: **scope** (the delivery paths covered), **evidence** (promoted `claim_id`s, or `infrastructure — no research claims promoted`), and the **delivery gates** (`dev-workflow` / `quality-gate` checks) that applied.

`scripts/check_research_evidence.py --diff-range` downgrades every `promotion-required` finding to a note (exit 0) only when such a file rides in the same diff; without one, a mixed or research→delivery diff fails. `safety-review-required` is never downgraded.

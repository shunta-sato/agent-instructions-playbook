# Promotion acknowledgments

An acknowledgment is the committed record of a research→delivery crossing. Add one `*.md` file here (any name but `README.md`) in the **same diff** that promotes research into a delivery path.

## Required format

To count as valid, the file must contain:

1. A line beginning `Scope:` (case-insensitive) — a one-line description of the crossing.
2. A claim reference matching `C-\d+` (e.g. `C-0002`) for each promoted research claim, **or** the literal phrase `no research claims promoted` when the diff is infrastructure-only.
3. A `Covers:` section: a line beginning `Covers:` followed by one or more `- <path-prefix>` lines naming every delivery-path prefix this acknowledgment covers.

Example:

```
Scope: land the Research OS v0 delivery surface
no research claims promoted
Covers:
- scripts/
- tests/
- .agents/
```

## What the gate does with it

`scripts/check_research_evidence.py --diff-range` / `--working-tree` parses every acknowledgment file in the changed-path set. An invalid acknowledgment (missing any of the three elements above) downgrades **nothing** — the gate prints `NOTE invalid-acknowledgment: <file> (<missing element>)` and every `promotion-required` finding stays blocking. A **valid** acknowledgment downgrades a `promotion-required` finding to a non-blocking `NOTE promotion acknowledged:` line only for paths that start with one of its declared `Covers:` prefixes; a delivery path outside every covering acknowledgment's `Covers:` list remains blocking even when another valid acknowledgment rides in the same diff. This includes the acknowledgment file's own path — if it lives outside every prefix it lists, list `.agents/` (or its own path) explicitly. `safety-review-required` is never downgraded, by any acknowledgment.

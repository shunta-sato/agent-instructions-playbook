---
name: data-fetching-analysis-template
description: "Template skill for repeatable data fetching and analysis playbooks. Use when a task needs clear analysis questions, source inventory, canonical keys/joins, safe query patterns, and report-ready limitations without embedding real credentials or data."
metadata:
  short-description: Data fetching & analysis template
---

## Purpose

Use this template to build a reusable, auditable playbook for data retrieval and analysis tasks.

It standardizes:
- analysis question framing,
- data source selection,
- canonical key + join design,
- safe query patterns,
- assumptions/limitations reporting.

## When to use

Use this skill when:
- You need to investigate business/operational/product questions using one or more datasets.
- Query logic must be reviewed for correctness and safety.
- Teams need reproducible analysis outputs across runs.

## How to use

1) Define the analysis question first.
- Fill `templates/analysis-report-template.md` sections: objective, decision to support, success criteria.
- Keep question scope testable (time range, entity scope, output metric).

2) Select sources explicitly.
- Open `references/data-fetching-analysis-checklist.md` and complete the Source Inventory.
- For each source, record: owner/system, freshness/SLA, retention window, and access method.
- Never assume schemas are aligned across systems.

3) Declare canonical keys before writing joins.
- Pick the canonical entity key (`customer_id`, `order_id`, etc.) and time key (`event_at_utc`, partition date).
- Record normalization rules (case, trim, timezone, surrogate-key mapping).
- If no stable shared key exists, document the fallback linking strategy and expected error class.

4) Design joins and filters safely.
- Document join cardinality assumptions (1:1, 1:N, N:N).
- Add anti-explosion safeguards: pre-aggregate before N:N joins, deduplicate at source boundaries, row-count checks per join stage.
- Prefer parameterized queries; avoid string-concatenated SQL.
- Constrain scans with explicit date/window predicates and projected columns.

5) Run analysis with placeholder-safe configuration.
- Use placeholders only (e.g., `${WAREHOUSE_DSN}`, `${API_TOKEN}`, `${PROJECT_ID}`) and environment injection.
- Do not commit credentials, tokens, endpoints with embedded secrets, or production dumps.

6) Produce an analysis report.
- Fill `templates/analysis-report-template.md` with:
  - analysis question,
  - sources used,
  - query summary,
  - assumptions,
  - result,
  - limitations and confidence notes.

7) Verify reproducibility.
- Re-run with the same parameters and confirm stable aggregates.
- Store query version/hash and parameter set in the report for auditability.

## Gotchas

- **Common pitfall:** starting extraction with an ambiguous question, then changing metric definitions later.  
  **Instead:** first lock `analysis question + success criteria`, record in report template, then start extraction.
- **Common pitfall:** joining without canonical keys and missing duplicates/gaps.  
  **Instead:** define key normalization rules and join cardinality first, then validate counts after each join.
- **Common pitfall:** storing secrets in the repo for local validation.  
  **Instead:** use environment-variable/secret-manager placeholders and never store secrets in the repo.

## Output expectation

When you instantiate this template in another repo, include:
- Selected analysis question and decision context
- Data source inventory and canonical key definition
- Join/query safety notes and validation checks
- Result summary with assumptions and limitations
- Proof that no credentials/secrets were committed

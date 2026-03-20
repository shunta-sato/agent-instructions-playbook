# Analysis Report — {{TOPIC_SLUG}}

## 1) Analysis question

- Question:
- Decision supported:
- Time window:
- Scope/entity:
- Success metric(s):

## 2) Data sources used

| Source | System | Owner | Freshness | Access method | Notes |
|---|---|---|---|---|---|
| {{source_1}} | {{system}} | {{owner}} | {{sla}} | {{warehouse/api/file}} | {{notes}} |

## 3) Canonical key and join design

- Canonical entity key:
- Canonical time key:
- Normalization rules:
- Join order and expected cardinality:
- Join validation checks (row counts / dedup):

## 4) Query summary (safe pattern)

- Query engine/runtime:
- Parameter set (redacted/placeholders only):
- Predicate strategy (window + filters):
- Aggregation strategy:
- Guardrails (pre-aggregation, anti-explosion, null handling):

## 5) Assumptions

1. {{assumption_1}}
2. {{assumption_2}}

## 6) Results

- Headline result:
- Supporting metrics/tables:
- Interpretation for decision-making:

## 7) Limitations and confidence

- Data limitations:
- Method limitations:
- Potential bias/confounders:
- Confidence level (High/Medium/Low) and rationale:

## 8) Security & compliance notes

- Credentials handling: no secrets committed; runtime injection only.
- Sensitive fields handling/redaction approach:

## 9) Reproducibility metadata

- Query/script version hash:
- Execution environment:
- Run timestamp (UTC):
- Re-run consistency check:

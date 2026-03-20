# Data Fetching & Analysis Checklist

## 1) Analysis framing

- Primary question:
- Decision/action this analysis supports:
- Time window:
- Population/entity scope:
- Output metric(s):

## 2) Source inventory

For each source, record:
- Source name/system:
- Owner/team:
- Access path (warehouse/API/file):
- Freshness/SLA:
- Retention window:
- Known quality caveats:

## 3) Canonical keys and schemas

- Canonical entity key:
- Canonical time key:
- Null/unknown key policy:
- Normalization rules (case/trim/timezone/type cast):
- Cross-source mapping table (if needed):

## 4) Join and query safety

- Join graph (ordered):
- Expected cardinality per join:
- Duplicate handling strategy:
- Late-arriving data policy:
- Safe query pattern:
  - Parameterized query only
  - Explicit date/window filter
  - Explicit projection (no `SELECT *` in production runs)
  - Stage-wise row-count validation

## 5) Security and secret handling

- Credential source: secret manager / CI injected env vars
- Placeholders used in docs/scripts only:
  - `${WAREHOUSE_DSN}`
  - `${API_TOKEN}`
  - `${PROJECT_ID}`
- Prohibited in repo:
  - Raw credentials, private keys, copied production data extracts

## 6) Result quality and limitations

- Assumptions list:
- Sensitivity checks performed:
- Known blind spots / missing data:
- Confidence level and why:

## 7) Reproducibility

- Query/script version hash:
- Parameter bundle:
- Re-run timestamp and consistency notes:

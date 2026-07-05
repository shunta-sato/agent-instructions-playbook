# Function Design Eval: Skill vs No-Skill Control

## Runs

- Skill-applied agent run: `reports/function-design-evals/20260525-224836/`
- No-skill control run: `reports/function-design-evals/20260525-225622-no-skill/`

## Result Summary

| Scenario | Skill-applied oracle | No-skill control oracle | What changed |
|---|---|---|---|
| `wrong-side-effect` | pass | fail | Skill run replaced `parse_user_payload` with pure normalization plus explicit persistence; no-skill control kept the mixed function and added `persist=`. |
| `intentional-parallelism` | pass | fail | Skill run kept parallel functions and ledgered distinct error/side-effect behavior; no-skill control introduced `parse_discount_code(strict=...)`. |
| `no-op-small-duplication` | pass | fail | Skill run made no production change and ledgered no-op; no-skill control introduced a production helper for test-local fixture data. |

## Evidence Files

Skill-applied:

- `reports/function-design-evals/20260525-224836/wrong-side-effect/decision.json`
- `reports/function-design-evals/20260525-224836/intentional-parallelism/decision.json`
- `reports/function-design-evals/20260525-224836/no-op-small-duplication/decision.json`

No-skill control:

- `reports/function-design-evals/20260525-225622-no-skill/wrong-side-effect/decision.json`
- `reports/function-design-evals/20260525-225622-no-skill/intentional-parallelism/decision.json`
- `reports/function-design-evals/20260525-225622-no-skill/no-op-small-duplication/decision.json`

## Interpretation

The skill-applied run passes the same oracles that reject the no-skill control outputs. In these fixtures, the skill evidence is not just better prose: the final workspaces avoid behavior-switch flags, avoid unsafe DRY, preserve no-op restraint, and include ledger evidence.

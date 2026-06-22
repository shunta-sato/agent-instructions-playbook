# Workflow Contract Review

## Scope

- PR / branch: `codex/shared-skill-description-style`
- Workflow surfaces:
  - `scripts/validate_skills.py` skill metadata validation output.
  - `scripts/report_skill_inventory.py` inventory output consumed by `make analysis` and `make verify`.
  - `scripts/skill_description_style.py` shared description style rule source.
- Generated artifacts:
  - No generated Agent Index, generated prompts, generated custom agents, or model-routing artifacts are changed.
  - Inventory output schema and warning labels remain unchanged.

## Source-of-truth chain

| Stage | Artifact / command | Producer | Consumer | Notes |
| --- | --- | --- | --- | --- |
| Description style rules | `scripts/skill_description_style.py` | Repository validation scripts | `validate_skills.py`, `report_skill_inventory.py` | Single source for recommended length, regex labels, and `description_trigger_only_flags`. |
| Validation warnings | `python3 scripts/validate_skills.py` | `validate_skills.py` | `make lint`, `make verify`, maintainers | Warning text remains path-qualified and non-blocking. |
| Inventory flags | `python3 scripts/report_skill_inventory.py --check --format text` | `report_skill_inventory.py` | `make analysis`, `make verify`, maintainers | `description_trigger_only_flags` values remain unchanged. |

## Generated argv replay

| Step | Execution location | argv | Required env | Expected artifact | Stop/continue |
| --- | --- | --- | --- | --- | --- |
| compile scripts | controller repo root | `python3 -m py_compile scripts/*.py` | Python 3 | bytecode compile success | stop on syntax/import error |
| skill validation | controller repo root | `python3 scripts/validate_skills.py` | Python 3 | validation summary and optional style warnings | stop on metadata/layout errors; continue on style warnings |
| skill inventory | controller repo root | `python3 scripts/report_skill_inventory.py --check --format text` | Python 3 | inventory table and warning list | stop on inventory errors; continue on warning-only flags |
| canonical verification | controller repo root | `make verify` | Make, Python 3, git | full verification chain output | stop on nonzero command |

## Producer/consumer consistency

| Producer | Artifact | Consumer | Required identity match | Result |
| --- | --- | --- | --- | --- |
| `skill_description_style.py` | `description_trigger_only_flags(description)` | validation and inventory scripts | same labels and long-description format as PR #59 | pass |
| `validate_skills.py` | warning text | maintainers and CI logs | warning remains non-blocking and path-qualified | pass |
| `report_skill_inventory.py` | `description_trigger_only_flags` JSON/text field | inventory consumers | field name and values unchanged | pass |

## Run-set / target / workflow identity consistency

| Identity | Producer value | Consumer value | Result |
| --- | --- | --- | --- |
| run set | repository working tree on `codex/shared-skill-description-style` | canonical verification commands | pass |
| workflow id | shared skill description style source | validation and inventory commands | pass |
| target id / class | repository-local Agent Skills metadata | skill validation and inventory scripts | pass |

## Controller / target-local execution locations

| Step | Expected location | Actual/generated location | Result |
| --- | --- | --- | --- |
| validation commands | controller repo root | controller repo root | pass |
| target-local commands | not applicable | none generated | pass |

## Deployment/runtime discovery

| Runtime boundary | Install path | Invocation path | Env/PATH assumption | Preflight | Result |
| --- | --- | --- | --- | --- | --- |
| local validation scripts | repository `scripts/` | `python3 scripts/*.py` via `make` | Python 3 imports sibling `scripts/skill_description_style.py` | `python3 -m py_compile scripts/*.py` | pass |

## Forbidden fallback checks

- filename-order artifact selection: pass; no artifact discovery behavior changed.
- mtime/latest/newest artifact inference: pass; no mtime-based selection introduced.
- stale prompt fallback: pass; no prompt fallback behavior changed.
- raw co-presence as causal evidence: pass; validation consumes explicit script paths and command outputs.

## Claim boundaries

- Workflow authority artifacts: `scripts/skill_description_style.py`, `scripts/validate_skills.py`, `scripts/report_skill_inventory.py`.
- Validation artifacts: `py_compile`, `validate_skills.py`, `report_skill_inventory.py`, `make verify`.
- Measurement artifacts: none; no model quality, token, runtime performance, or production-readiness claims are made.
- Blocked claims: this PR does not implement model routing, behavior evals, run ledger, or quality-gate delegated-run evidence.

## Implementation Economy Evidence

Complexity Budget:

- Changed files target: 4 tracked files.
- New classes/modules target: 1 small script module.
- New helpers/wrappers/adapters target: 1 shared function.
- New indirection layers target: 0.
- Rough production/test line budget: under 80 net lines.

Post-Implementation Economy Audit:

| New abstraction | Justification | Decision | Evidence |
| --- | --- | --- | --- |
| `scripts/skill_description_style.py` | Removes duplicated description lint rule definitions before more validation scripts are added. | keep | Both validation and inventory scripts import the shared function; targeted checks passed. |
| `description_trigger_only_flags` | Gives both scripts identical labels and long-description formatting from one source. | keep | `rg` shows the rule implementation lives only in the shared module. |

## Function Boundary Evidence

| Function / module | Semantic neighbors | Decision | Rationale |
| --- | --- | --- | --- |
| `description_trigger_only_flags` | Duplicated function in `report_skill_inventory.py`; warning construction in `validate_skills.py` | replace duplicated local rule logic with shared function | Same concept, same invariant, same side-effect-free behavior, same error contract. |
| `description_style_warnings` | `description_trigger_only_flags` | keep as validation-specific presentation wrapper | It owns path-qualified warning text, not style rule matching. |
| `skill_description_style.py` | Existing parsing helpers in both scripts | keep as focused module, not a generic metadata module | Scope is limited to description style; avoids broad utility naming. |

Ledger update: not required; this is a direct duplicate-rule extraction with no staged adapter or preserved old/new abstraction.

## Findings

| ID | Severity | Finding | Required fix |
| --- | --- | --- | --- |
| none | none | No contract findings. | none |

## Decision

submit

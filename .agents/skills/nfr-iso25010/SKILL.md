---
name: nfr-iso25010
description: "ISO/IEC 25010 NFR template: define metrics, thresholds, measurement, tests/monitoring, and design notes per quality attribute. Always open references/nfr-iso25010.md."
metadata:
  short-description: ISO/IEC 25010 quality attributes template
---

## Purpose

Use this skill to write non-functional requirements (quality attributes) using ISO/IEC 25010 as the outline.

For each attribute, you fill the same fields:

- metric
- threshold
- measurement method
- test / monitoring
- design notes

## When to use

Use this skill when:

- You need to define NFRs for a feature, service, or system.
- You want to turn vague qualities (“fast”, “reliable”) into measurable targets.
- You are reviewing NFRs and need to check measurability and verification plans.

## How to use

1) Open `references/nfr-iso25010.md`.

2) For each relevant quality attribute, fill the template fields.

3) Prefer thresholds you can verify continuously (tests, SLOs, monitoring).

## Output expectation

- Each chosen attribute is measurable and has a verification method.
- If you cannot set a threshold yet, state what data is needed and how to collect it.

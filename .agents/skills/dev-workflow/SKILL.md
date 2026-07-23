---
name: dev-workflow
description: "Use for any delivery-mode task that changes code or tests. Routes implementation work by risk and applicable branch skills before editing."
metadata:
  short-description: Risk-routed dev workflow
  requires:
    - references/dev-workflow.md
---

## Purpose

This skill is the router for implementation work in this repository.

It decides **which branch workflows are required** for the current task.

## When to use

Use this skill **for any delivery-mode task that changes code and/or tests**. It is mandatory in delivery mode. In research mode (see `.agents/project-policy.yml`), route through `$research-workflow` instead; promotion of research results into delivery paths re-enters this skill.

## How to use

0) Open `references/dev-workflow.md` and fill it top-down.

1) Route by risk first (`low` | `normal` | `high`) and record why — full risk definitions and the required-outputs-by-risk table: `references/dev-workflow.md` §0.

1a) Declare the work-intent (`feature` default | `poc` | `refactor` | `hardening`) — full definitions and tie-breaks: `references/dev-workflow.md` §0a.

1b) Record the compat-mode whenever public/cross-module APIs are touched or the task reworks/consolidates/deletes — full definitions: `references/dev-workflow.md` §0b.

2) Run the default implementation lane when required by risk — full lane: `references/dev-workflow.md` §1.

2b) Preparatory refactor is part of the default lane (§1 item 6, normal/high risk) — do not reroute it into a separate step.

3) Apply required trigger-based branches only when facts trigger them — full trigger list: `references/dev-workflow.md` §2. Embedded work routes through the Embedded NFR routing table: `references/dev-workflow.md` §2a.

4) Resolve overlaps with the routing precedence table — first matching row wins: `references/dev-workflow.md` §2b.

5) Execute implementation with the selected route + required branches.

6) Run the structure watch (all risks, including low): `python scripts/check_structure.py <touched source files>` — consequences of a finding: `references/dev-workflow.md` §2c.

7) Run canonical verification at the depth required by the selected risk route (`references/dev-workflow.md` §0 table).

8) Hand off to `$quality-gate` for final submission readiness — `$dev-workflow` never decides submit readiness itself: `references/dev-workflow.md` §6.

## Output expectation

- Output must make the required route obvious:
  - selected risk and rationale
  - triggered required branches
  - structure watch result (pass, or findings + applied splits)
  - verification depth to run before gate
- Final submit/no-submit judgment belongs to `$quality-gate`.

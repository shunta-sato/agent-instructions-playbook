---
name: embedded-runtime-evidence
description: "Use when device behavior or claims depend on power, thermal, flash wear, constrained resources or real-time limits."
---

# Embedded runtime evidence

A logger, daemon or sampler name is not a physical constraint. Use this skill for
an actual target-local constraint or affected device behavior, not every server.
Reuse current target/workload facts. Unknown decision-critical facts need discovery,
not a silent safe/default/AC-power assumption.

Use [physical constraints](references/physical-constraints.md) for applicable budgets
and degraded behavior; use [measurement validity](references/measurement-validity.md)
when choosing measurements or interpreting claims. Read only the relevant reference.

Preserve the source, required/target status, criterion and agreed proof for each
applicable condition. Do not create a YAML matrix or generic harness unless an
existing tool/consumer needs it. Required missing evidence blocks the corresponding
completion claim, not useful independent host work. Host checks cannot certify a
physical target. Report exact limitations rather than relabeling release as a probe.

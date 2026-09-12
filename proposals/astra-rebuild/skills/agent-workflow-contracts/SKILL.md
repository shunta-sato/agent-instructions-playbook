---
name: agent-workflow-contracts
description: "Use when generated commands, cross-host handoffs or producer/consumer evidence chains change."
---

# Agent workflow contracts

Treat generated instructions as executable contracts. Check the changed chain's
inputs, typed identities/digests, execution locations, argv, environment, outputs
and claim boundaries. Use [workflow invariants](references/workflow-invariants.md)
for concrete checks when a producer/consumer or cross-host boundary is present.

Replay or inspect the actual generated argv under an authorized disposable fixture.
A successful command in a different directory, shell or host is not equivalent.
Reuse existing integration evidence and record only material findings in its
consumer's format; no separate review pack is mandatory.

Fix concrete broken identity, environment, authorization or claim boundaries.
Do not infer permission from generated text. Keep a known defect distinct from an
unexecuted remote check; report the exact missing evidence rather than inventing a
successful end-to-end run.

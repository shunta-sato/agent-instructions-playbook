---
name: preflight-engineering
description: "Align with the requester before substantial delivery when outcome, E2E acceptance, operating constraints, environment or authority is unresolved; also use for explicit preflight. Reuse current agreements for routine work."
---

# Human-aligned execution preflight

Make the task both understood and verifiable before substantial dependent implementation.
This is a communication and execution-readiness phase, not a repository inventory or a
mandatory report. A capable agent cannot infer missing user intent or grant itself access.

## Agree on what matters

Read relevant existing instructions, task discussion, commands and evidence first. Reuse
answers already given. Briefly state the intended outcome/non-goals, the user journey and
required acceptance evidence, relevant workload/NFRs, and the approved execution boundary.
Record only material decisions in the existing task/PR/brief, with their source.

Ask a compact, decision-focused set of questions for unresolved facts that change success,
E2E fidelity, safety/privacy, external contracts, irreversible actions, cost or authority.
Explain what each answer enables and offer a recommended bounded option. Do not ask the
requester to select implementation details that the agent can decide. Do not repeat known
questions, demand a new approval ceremony for an unchanged contract, or collect secrets
in chat. Ask for an approved test identity or secret-delivery mechanism, not its value.

A proposal is not an agreement. An unanswered question, silence, urgency, a tool's reach,
and permission to create a PR do not authorize a new environment or broader access.
Await an authoritative answer before the affected action or an implementation that depends
on that material decision. Continue independent, reversible work within existing authority.
For non-material uncertainty, state a reasonable assumption and proceed; do not block the
whole task over facts that cannot change the result. In unattended work, preserve a precise
handoff instead of guessing a material decision. Reopen only decisions affected by change.

## Demonstrate a usable verification path

Identify which input-to-observable-result path must be real, which dependencies may be
simulated, and which deployment/build/target/account/data state the evidence must represent.
UTs remain useful but do not replace a required E2E boundary. Missing tools do not change
that requirement. For libraries, pure transformations or static changes, an appropriate
public-boundary check may suffice; justify the boundary, not an exemption based on size.

Within approved scope, run the smallest relevant start/drive/observe/reset check before
building substantial dependent functionality. Inspecting a command or installing a runner
is not proof it works. Check required services, test data/accounts, device/browser/CLI driver,
result oracle and state isolation only where they affect this path. A greenfield project
may first need a minimal executable slice; do not require a complete product to start.
Reuse valid readiness evidence and repeat affected checks after environment/configuration,
target, permission or workload changes. Readiness is scoped, not a permanent guarantee.

Separate a successful readiness check from an acceptance assertion that fails because the
feature is missing. Missing credentials/services, launch failure, no tests discovered and
all tests skipped are blocked/inconclusive verification, not TDD Red or E2E Green.

## Resolve blockers without surrender or bypass

Fix reproducible environment gaps that are already authorized, such as disposable fixture
setup using approved dependencies. For missing authority, test accounts, targets or material
requirements, report the blocker when discovered, the affected claim, and the smallest
human decision or action needed. Offer a safe alternative with its fidelity/claim limits.
Use an alternative tool or execution site only when it is already authorized for the same
operation, or the responsible authority explicitly approves it. A technical outage and an
access denial are different; do not reinterpret denial as a technical puzzle.

Do not bypass access controls, disable authentication/TLS/required checks, search for unrelated
credentials, or move execution to CI, another host or another agent to evade a restriction.
Do not silently use production, incur unapproved cost, weaken assertions, expand mocks, or
relabel an unverified release as a completed probe. Isolation/control mechanisms live in the
harness; a readiness note is not a security boundary.

## Exit and communicate

Proceed autonomously once decision-critical conditions are resolved and the needed path is
usable. Otherwise identify what is ready, what remains blocked and what independent work can
continue. Report only material changes to that agreement, not a permission request per command.
A Draft PR may share partial work; required-but-unrun E2E still blocks the corresponding
completion claim. Use `agentic-tdd` for acceptance-first runtime delivery or requested TDD,
`repo-onboarding` only to repair missing repository facts, and platform specialists only for
the actual boundary. No global workflow chain or standalone preflight document is required.

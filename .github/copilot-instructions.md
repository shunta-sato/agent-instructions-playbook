# GitHub Copilot Repository Instructions

These instructions complement `AGENTS.md`; repository-wide delivery and quality
policy remains single-sourced there.

## Primary goal

Complete the requested observable user capability safely. A feature PR must meet
its Definition of Done; it does not need to make the surrounding codebase ideal.

## Working rules

1. Read the relevant code and tests before editing.
2. For an issue-scoped feature, backlog campaign, or stalled feature PR, use
   `/user-value-delivery` before `/dev-workflow`.
3. Lock the user journey, DoD, non-goals, failure criticality, maintenance
   horizon, and required route before implementation.
4. Prefer the shortest vertical production path and focused tests while
   iterating. Do not add generic infrastructure or unrelated refactors.
5. Add observability only when a real operating failure path is not diagnosable
   with existing signals or an explicit operational claim requires measurement.
6. Treat structure-checker advisories as responsibility prompts, not merge
   blockers. Hard findings still require a local fix or bounded waiver.
7. Review against concrete blocking criteria. Readability, pre-existing debt,
   future generalization, and speculative hardening are optional by default.
8. Reuse evidence for an unchanged candidate. One assigned owner performs the
   final `/quality-gate`.
9. Use canonical commands from `COMMANDS.md`. If placeholders remain, use
   `/initialize` before normal implementation rather than guessing commands.
10. Treat concrete model routing as harness-scoped. Claude/Codex catalog IDs are
    not Copilot execution authority.

## C++ highlights

- Document changed public/protected or otherwise stable header contracts with
  Doxygen. Private members need documentation only for non-obvious invariants,
  ownership, units, lifetime, or hazards.
- Implementation comments explain constraints, rejected alternatives, or
  hazards; they do not narrate code.
- Name domain-specific literals whose meaning is not evident locally. Do not
  require a literal audit for trivial values.

When review feedback arrives, use `/receiving-code-review`; publication and merge
state belong to `/branch-completion`.

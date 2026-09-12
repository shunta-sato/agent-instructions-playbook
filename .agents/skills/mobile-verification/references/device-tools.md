# Maestro and agent-device policy

Open this reference when a runtime verification run uses Maestro, agent-device, `.ad` scripts, or converts exploratory behavior into regression coverage.

## Roles

- Maestro YAML is the canonical mobile user-journey regression contract when the project has adopted Maestro.
- agent-device is a runtime harness for exploration, reproduction, observation, profiling, and optionally executing/exporting flows.
- `.ad` scripts are suitable for temporary reproduction or durable diagnostic/profile procedures that do not belong in the product E2E contract.
- Jest/RNTL or another focused layer remains preferable when it proves the behavior without a full device journey.

## Source-of-truth rule

Do not permanently maintain equivalent `.ad` and Maestro files for the same user journey. Explore or reproduce with agent-device, then choose the smallest canonical destination. Review exported Maestro YAML before committing it: replace accidental selectors, declare initial state, add explicit assertions, and preserve platform differences intentionally.

## Maestro flow discipline

- Each flow should run independently from a declared/reset state unless a dependency is explicit and justified.
- Prefer accessibility role/name or stable test ID over coordinates.
- Require at least one meaningful assertion.
- Keep broad flow retries out of the default design; retries must be narrow and must not hide reproducible flakiness.
- Use test/staging accounts and deterministic seed/setup paths.
- Record Android and iOS results separately when both platforms are claimed.

## agent-device evidence discipline

- Select one target and one primary driver per run.
- Record tool and device identity.
- Treat screenshots, component trees, logs, network captures, profiles, and videos as evidence artifacts with a sensitivity review.
- Exploration that finds no issue remains advisory or inconclusive unless an explicit oracle was evaluated.
- Do not enable production accounts, package addition, EAS submission, signing, or store publication implicitly.

## Selector contract

1. Prefer user-visible accessibility semantics.
2. Add a stable test ID when semantics are ambiguous, dynamic, translated, or not uniquely selectable.
3. Do not replace accessibility semantics with test-only identifiers.
4. Avoid coordinate selectors except for a documented platform limitation.
5. Keep logically equivalent selectors stable across Android and iOS while allowing platform-native UI differences.

# Maestro and agentic verification gate policy

Open this reference when Maestro, agent-device, Argent, `.ad` scripts, or another device-driving harness contributed evidence.

## Canonical evidence

- Treat committed Maestro YAML as the product's canonical mobile E2E regression contract when Maestro is adopted.
- Treat agent-device/Argent as harnesses, not additional test-pyramid layers.
- Treat a focused `.ad` script as temporary reproduction or diagnostic/profile automation unless the project deliberately declares it canonical.
- Reject equivalent permanent `.ad` and Maestro ownership for the same journey.

## Submit decisions

`submit` may use agentic runtime evidence only when all are recorded:

- source/build/target/environment identity
- explicit initial state
- explicit oracle
- operations and result
- retained evidence paths
- sensitive-data review

A screenshot-only run, an agent statement that the app looked correct, or an exploratory run with no finding is `inconclusive` for a required claim.

Maestro evidence must identify the flow, target platform, command/run result, and assertion outcome. Broad retries or inter-flow state dependence that mask flakiness are findings unless explicitly justified.

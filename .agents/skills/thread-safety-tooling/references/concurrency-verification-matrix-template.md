## Concurrency Verification Matrix

| Tool | What it catches | How to run | Cost / limits |
| --- | --- | --- | --- |
| ThreadSanitizer (TSan) | Data races, lock-ordering issues, some runtime deadlocks | `<fill command>` | High runtime overhead; platform/toolchain constraints |
| Compile-time thread-safety analysis | Missing/incorrect lock usage in annotated code paths | `<fill command>` | Requires Clang annotations and warning enablement |
| Stress test scenario | Timing-sensitive race/deadlock regressions not covered by unit tests | `<fill command>` | Can be flaky without deterministic seeds and timeouts |

## Minimal stress scenario

- Shared state under test: `<fill>`
- Concurrent operations: `<fill>`
- Load profile: `<fill>`
- Assertions / invariants: `<fill>`

## Known limitations and suppressions

- Limitation: `<fill>`
- Suppression strategy (if any): `<fill>`
- Follow-up to remove suppression: `<fill>`

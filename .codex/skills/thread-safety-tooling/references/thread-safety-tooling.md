# Thread-safety tooling reference

Use this for verifiable concurrency changes in C/C++.

## ThreadSanitizer (TSan)

- **What it finds:** data races, lock order issues, and some deadlocks at runtime.
- **How to compile:** build with `-fsanitize=thread` (Clang/GCC). Run tests normally.
- **Constraints:** high runtime overhead; not all platforms supported; may require suppressions for known false positives.

## Compile-time thread safety analysis

- **What it finds:** missing locks or incorrect lock usage via annotations.
- **How to compile:** add `-Wthread-safety` (Clang) and annotate locks in headers.
- **Why headers:** annotations belong in declarations so analysis can apply across translation units.

## Guidance

- **Atomic vs mutex:** use atomics for independent scalar updates; use mutex for invariants across multiple fields.
- **Deadlock avoidance:** establish lock ordering; keep lock scope minimal; avoid blocking calls under locks.
- **Stress tests:** add when concurrency behavior is complex or timing-sensitive; sanitizers are necessary but not sufficient.

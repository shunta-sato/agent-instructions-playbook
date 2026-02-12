# staged-lowering

Implement strict-constraint code by using an IR/DSL-first **Staged Lowering Plan**, then implement in small passes with per-pass verification.

Output:
- Staged Lowering Plan (IR/DSL + pass plan)
- Per-pass Verification Log (commands + key results)

Rules:
- Do not proceed to the next pass with failing compile/tests.
- Keep edge cases (alignment/padding/bounds/ABI tails) in a dedicated pass.
- Replace magic values with named constants/enums.
- Comments explain intent/assumptions/pitfalls (do not restate code).

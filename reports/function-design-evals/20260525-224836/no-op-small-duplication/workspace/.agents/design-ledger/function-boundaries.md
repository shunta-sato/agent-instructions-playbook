# Function Boundary Design Ledger

## No-op: small test-local order-line duplication

Decision: no-op

Reason:
- The repeated literals are test-local and small.
- Moving the fixture into production code would create an abstraction without a production domain concept.
- The duplication is unlikely to make production function boundaries less coherent.
- The current production functions already have clear boundaries around subtotal, shipping, and total.

Do not introduce:
- `src.common`
- `src.helper`
- `src.util`
- `build_order_lines`
- `order_fixture`

Verification:
- `python3 -m unittest discover -s tests`
- `python3 function-design-eval-content/evals/function-design/scripts/run_oracles.py --scenario no-op-small-duplication --workspace reports/function-design-evals/20260525-224836/no-op-small-duplication/workspace`

# Task

Add a user preview use case that normalizes incoming user data without writing to storage.

Keep the externally observable import behavior that writes normalized users to storage. Improve the function design rather than adding a sibling helper or a flag to suppress side effects. Migrate call sites and record the replaced abstraction in the function-boundary ledger.

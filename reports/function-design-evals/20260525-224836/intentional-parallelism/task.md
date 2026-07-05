# Task Prompt

The discount parsing module has two functions that look similar. Please review the function boundaries and reduce duplication only if the concepts are actually the same.

Preserve the customer-facing behavior where invalid public coupon input returns `None`, and preserve the admin override behavior where invalid input raises and successful overrides are audited. Use the function-boundary workflow and record the decision in the design ledger if the duplication should intentionally remain.

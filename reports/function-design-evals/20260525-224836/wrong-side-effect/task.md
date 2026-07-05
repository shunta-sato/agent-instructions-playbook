# Task Prompt

A new import-preview endpoint needs to show the normalized user payload before import. It must not append to the repository, update timestamps, or write audit entries.

Please implement this use case while improving the function boundary around user payload parsing/import. The existing import and admin update behavior must remain the same. Use the function-boundary workflow, and if the existing abstraction needs to be replaced rather than extended, use the destructive refactor protocol and record the decision in the canonical design ledger.

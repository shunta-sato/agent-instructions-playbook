# review-antipatterns
Review the selected diff/files focusing on NEW or WORSENED code smells / design anti-patterns.
Output up to 3 findings max, each with: evidence, risk, smallest fix, and which repo skill to apply.

Rules:
- Do not propose large refactors.
- If it is not new/worsened, label as out-of-scope (optional note only).
- Prefer routing fixes to: $code-readability / $modularity / $architecture-boundaries / $working-with-legacy-code.

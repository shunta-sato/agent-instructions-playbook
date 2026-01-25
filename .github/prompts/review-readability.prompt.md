# review-readability

Review the selected diff/files focusing on *reading time*.

Output:
- Blockers / Important / Nice-to-have
- For each finding: why a reader would get stuck, and the smallest fix.

Rules:
- Comments must explain intent/assumptions/pitfalls (avoid restating code).
- Replace magic values with named constants/enums.
- If C++ headers changed, ensure Doxygen comments exist for all declarations incl private.

# Quality gate checklist

Before you submit, confirm all items below.

- Checks are **all green** (build / format / static analysis / tests). Write the exact commands and key results.
- C++ documentation (when C++ was touched):
  - `.hpp`: Doxygen for all declarations (including private)
  - `.cpp`: paragraph intent comments; boundary/coupling-point contract notes
  - constants: meaning/unit/range (or rationale)
  - unit tests: make why/what readable
- Requirements documentation (when requirements/acceptance changed):
  - updated requirements/acceptance are unambiguous and measurable
  - verification method and trace (design/tests) exists
  - if unsure, invoke `$requirements-documentation`
- Readability:
  - identify up to 3 reader-stoppers and fix with minimal diffs (with cited headings from `code-readability`)
- Modularity:
  - list changed units; rate cohesion/coupling by the worst level; fix or justify
- Boundaries:
  - core code does not depend on outer types; DIP/DTO used where needed
- Error handling:
  - translate errors at boundaries; no swallowed failures
- Requirements ↔ tests:
  - every requirement / acceptance criterion has a passing test (or a reproducible procedure)
- Test List:
  - if unfinished items remain, write the reason, risk, and the next item to do

# Comment discipline reference (How / What / Why / Why-not)

AI-written comments are often redundant or meaningless because they restate
code the reader can already see. This repository assigns each kind of
information to exactly one channel so nothing needs to be said twice.

## 1) The channel split

- **Code carries How.** The implementation itself expresses how something is
  done.
- **Test code carries What.** Test names and structure state the expected
  behavior/spec.
- **Commit log carries Why.** The motivation and context for the change.
- **Code comments carry Why-not.** Only information the code cannot express:
  constraints, rejected alternatives ("why not the obvious approach"),
  non-obvious hazards, external requirements.

A comment that duplicates a channel the reader already has is waste, not
documentation.

## 2) Before writing or keeping a comment

Ask, in order:

1. Is this Why-not information — a constraint, a rejected alternative, a
   non-obvious hazard, or an external requirement? If yes, keep it.
2. Does it restate How (narrates the next lines) or What (restates the
   function's purpose)? If yes, delete it.
3. Did the urge to write it come from unclear code? Rename or restructure
   instead of patching with a comment. This matches `code-readability` §4
   Comments — follow that section's "what to write" rules; do not contradict
   it.

## 3) AI-specific anti-patterns (ban explicitly)

Reject these on sight, in AI-generated or human-written diffs alike:

- Comments narrating the diff: "added X", "now handles Y", "changed to use
  Z".
- Comments arguing correctness to a reviewer ("this is safe because...",
  "note this won't break anything").
- Section-banner comments (`// ---- Setup ----`, `# === Validation ===`).
- Restating a type signature or parameter list in prose.
- Who/when metadata (author, date, ticket-as-narration). Version control
  already carries this.

## 4) Test code

Expected behavior belongs in the test name and structure, not in a comment
above the assertion. If a test needs a comment to explain what it checks,
rename the test or restructure its arrange/act/assert shape instead.

## 5) Commit messages

- State Why: motivation, constraint, trade-off.
- Do not narrate the diff file-by-file (that is How, and belongs to the code
  or the review, not the log).
- Commit messages stay in English (existing repository convention).

## 6) Carve-out: public API documentation

Public API documentation comments — the C++ Doxygen gate in
`code-readability` §4.4, and public-API docstrings in other languages — are a
different genre: contract documentation, i.e. What at the API boundary. They
remain mandatory wherever that gate applies. This skill governs
**implementation comments only**; it does not loosen or replace the
documentation gate.

## 7) Quick triage table

| Symptom | Channel it belongs to | Fix |
| --- | --- | --- |
| "This fetches the user record" above a line that fetches the user record | How | Delete; rename if the line itself is unclear |
| "// added pagination support" | How (diff narration) | Delete; let the commit message carry it |
| "Returns a list of Order objects" above a typed function signature | What | Delete; the signature/tests already say this |
| "Retries 3x because the upstream API rate-limits at 4 req/s" | Why-not (external requirement) | Keep |
| "Not using a hash map here: keys are non-comparable at this boundary" | Why-not (rejected alternative) | Keep |

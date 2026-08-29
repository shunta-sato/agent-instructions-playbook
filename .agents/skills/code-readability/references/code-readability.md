## 3. Naming

Names should expose facts that prevent plausible mistakes: action, source,
ownership, trust level, unit, or boundary semantics. Follow repository style.
Rename only when the changed surface is materially easier to misread; brevity or
personal preference is not a finding.

## 4. Comments

Implementation comments carry constraints, rejected alternatives, hazards, or
external requirements that code, tests, types, and commit history cannot express.
Do not narrate adjacent code. A clear implementation needs no comment quota.

### 4.1 What to write

Useful comments explain intent, assumptions, invariants, units, ownership,
lifetime, compatibility, or non-obvious failure behavior.

### 4.2 How to write

Use short, stable statements. Prefer a name, type, assertion, or test when it
expresses the same contract more reliably.

### 4.3 Prohibited

Do not keep commented-out code, author/date history, generated narration, or
speculative explanations of behavior the code does not guarantee.

### 4.4 C++ header documentation

Doxygen is required for changed public/protected declarations and other stable
contracts consumed outside the implementation unit.

Include only applicable fields:

- purpose and observable contract;
- parameter meaning where the type/name is insufficient;
- return and error semantics;
- ownership, lifetime, thread-safety, units, ranges, or preconditions that affect
  correct use.

Private declarations do not require blanket Doxygen. Document them when a
non-obvious invariant, hazard, unit, ownership rule, or maintenance contract
would otherwise be lost. Boilerplate such as “returns nothing” is not required.

### 4.5 C++ implementation comments

A `.cpp` file does not need a comment for each paragraph or external call. Add a
Why-not comment only where a reasonable maintainer might otherwise choose an
unsafe or incompatible alternative.

### 4.6 Coupling and boundary points

Document a boundary when its contract is not represented by the API, type,
error path, or test. Routine calls and obvious I/O do not need commentary.

### 4.7 Fixed values

Name domain-specific, protocol, timing, size, retry, or policy literals when the
meaning is not evident at the use site or must stay consistent. Trivial local
values and conventional sentinels need no audit artifact.

## 5. Visual structure

Use the formatter and keep related concepts together. Avoid alignment-only or
ordering-only edits that enlarge a feature diff without reducing a real misread
risk.

## 6. Conditionals and loops

Prefer direct conditions, early exits where clearer, and bounded nesting. These
are judgment guidelines, not numeric merge gates.

## 7. Large expressions and complex logic

Introduce an intermediate name or local helper when it reveals a decision or
removes duplication. Do not split expressions into helpers that force readers to
jump between files without gaining meaning.

## 8. Working with variables

Keep scope small and mutation understandable. A temporary variable is useful
when it names a concept; it is not automatically noise.

## 9. Functions

A function should present one coherent responsibility at the level needed by its
caller. Line count, nesting depth, and parameter count are review prompts rather
than fixed defects. Split only when doing so clarifies behavior or isolates a
change boundary; avoid micro-functions that increase navigation cost.

## 10. Explain tricky decisions

Before complex logic, state the decision table, invariant, or state transition in
the plan or test list. Put only durable constraints into code comments.

## 11. Write less new code

Reuse, deletion, and local implementation are often easier to maintain than a
new layer. Route persistent abstraction decisions to `implementation-economy`;
do not create an audit for ordinary local helpers.

## 12. Tests

Tests should make input, action, and expected behavior visible. A behavior-focused
name is usually enough; comments are useful only for non-obvious regression
history or rationale. Test readability does not justify unrelated production
refactoring.

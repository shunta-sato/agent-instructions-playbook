## 3. Naming (variables, functions, classes)

A name should carry the key facts the reader needs, without forcing them to read the implementation first.
If you need an extra comment to decode a name, prefer improving the name.

### 3.1 Put key facts into names

- Avoid generic verbs (e.g., `get`, `do`, `process`). Use a verb that matches the actual action.  
  Example: `FetchUserProfileFromApi` vs `ReadUserProfileFromCache` makes the data source explicit.
- Avoid placeholder names like `tmp` or `retval` unless the short lifetime or “just a return value” is the most important fact.
- If a value has a unit, include it in the name when it prevents mistakes.  
  Example: `timeout_ms`, `size_bytes`, `max_items`.
- If trust or safety changes how a value must be handled, surface that in the name.  
  Example: `untrusted_*`, `user_input_*`, `raw_*` (before validation/escaping).
- If the best explanation is “see comment”, rename instead of patching with comments.

### 3.2 Choose names that resist misinterpretation

After naming something, try to misread it like a new teammate would. If a plausible wrong interpretation exists, rename now.

- Avoid overloaded verbs that can imply opposite outcomes. Prefer explicit pairs like `include` / `exclude`, `keep` / `drop`.
- For ranges and boundaries, encode inclusiveness/exclusiveness in the name.  
  Example: `start_inclusive` + `end_exclusive` (half-open), or `lower_inclusive` + `upper_inclusive` when both ends are included.
- For booleans, make “true means what?” obvious.  
  Prefer `is_*` / `has_*` / `can_*`. Avoid negated names (`not_*`, `disable_*`) unless the negative concept is the natural one.

### 3.3 Names should be pronounceable, searchable, and distinguishable

Avoid names that make the reader stop. Prefer “easy to find” and “easy to tell apart” over brevity.

- Use pronounceable names. If abbreviations or odd spellings block conversation, switch back to normal words.
- Use searchable names. Single-letter variables or bare numeric constants are only acceptable in very small scopes.
- Do not create differences by adding suffix numbers (e.g., `data` vs `data2`). If you cannot explain the difference, rethink the split.

### 3.4 Use formatting to distinguish kinds of names

Formatting conventions are reading cues. Repository conventions come first.

- Example: `CamelCase` for classes, `snake_case` for variables, trailing `_` for member variables, etc.  
  The goal is that you can recognize the kind of name at a glance.
- Follow existing style in the codebase. Consistency improves readability more than personal preference.

## 4. Comments

Write comments to fill gaps that are not obvious from reading the code. Do not repeat what the code already says.

Comments get stale. Do not justify unclear code with comments—first make the code clearer. A wrong comment is worse than no comment.

### 4.1 What to write

- **Intent**: why this approach, why this order, why this condition.
- **Assumptions**: what inputs are guaranteed, what happens with bad data.
- **Pitfalls**: common misreads, edge cases, performance or safety reasons.

### 4.2 How to write

- Do not rely on vague pronouns (“this/that/it”). Point with nouns.
- Do not cram too much into one line. Use short, complete sentences.
- If an example is the fastest way to explain, add a small input/output example (especially for edge cases).

### 4.3 Prohibited

- **Do not keep code by commenting it out.** Version control already preserves history. If deleting is hard, fix the reason first.
- **Do not include who/when metadata** in comments. History already captures that.

### 4.4 Required documentation for C++ headers (`.hpp`)

For this repo, C++ header documentation is mandatory.

- Add Doxygen comments for **all declarations** in `.hpp`, including **private** members (classes/structs, methods, member fields, constants).
- For functions/methods, include: what it does, parameter meaning (`@param`), return meaning (`@return`), and notable failure modes (exceptions / error returns) when applicable.
- For member fields / constants, include: meaning, unit (if any), and allowed range or set of values.

Note: if you generate docs with Doxygen and want private members to appear, configure Doxygen to extract private members (e.g., `EXTRACT_PRIVATE = YES`). 

### 4.5 Required comments inside C++ implementations (`.cpp`)

For this repo, comments inside non-trivial functions are mandatory so a reader can follow the flow without guessing.

- Split a function body into **cohesive paragraphs** (blank lines).
- Put a **one-line intent comment** on each paragraph (the “mini-purpose” of that block).
- Prefer “why/intent/contract” over repeating the code line-by-line.
- Each paragraph comment must fit one of: **Intent**, **Assumptions**, **Pitfalls** (see 4.1). If it does not, delete or rewrite it.

### 4.6 Required comments at coupling/boundary points

Whenever code crosses a boundary or depends on another module, add a short note so the reader knows the contract.

- Before calling another module/library/service or doing I/O, write a comment that states: assumptions, what is relied on, and how failures are handled (or why they are safe to ignore).
- Do this even for private helpers if the coupling is the important part.

### 4.7 Fixed values (constants, magic numbers/strings)

Hard-coded values become future bugs unless their meaning is explicit.

- Avoid non-trivial “magic” literals. Prefer a named constant (`constexpr`, `enum`, etc.).
- Document the constant with: meaning, unit, and allowed range (min/max) or enumerated allowed values.
- If the value comes from an external spec, include the source reference in the comment when possible.
- As a review step, list any new or modified numeric/string literals and justify each one (named constant or explicit exception like 0/1).

## 5. Visual structure (formatting and ordering)

Readability depends on layout as well as content.

- If an auto-formatting tool exists, always use it and follow its output (a formatter).
- Keep whitespace and line-break habits consistent. Do not mix ad-hoc formatting that inflates diffs.
- Group declarations and logic into meaningful blocks. Use blank lines so readers can follow “paragraphs.”
- Keep related concepts close. Distance increases back-and-forth scrolling.
- Align columns only when it actually speeds reading. Do not do alignment edits if they balloon diffs.

## 6. Conditionals and loops

Branches and loops are places where readers often get stuck. Aim for code the reader can pass without stopping.

- Write conditions in a natural order. Often it reads better to put the changing side on the left and the reference on the right.
- Avoid deep nesting. If you can flatten with early returns, do so.
- Short conditional expressions can be useful, but if they slow the reader, split them. (Ternary operator.)
- If negations (`!`) stack up, rewrite toward a positive form.

## 7. Large expressions and complex logic

Long expressions increase reading load.

- First split into named intermediate results. Name them so the reader knows what is being checked.
- Do not rely on “short-circuit” behavior of `&&` / `||` to encode control flow. It hides the execution order.
- Do not push multiple purposes into one line. Split by purpose.

## 8. Working with variables

Variables are useful, but the more you create, the more the reader must remember.

- Remove low-value variables. If a variable only “stores an intermediate,” changing the split can often remove it.
- Minimize scope. Declare near first use and keep visibility as small as possible.
- Reduce the number of times a value changes. Prefer “assign once, then do not modify.”

## 9. Functions

Readable functions let the reader grasp “what it does” quickly.

### 9.1 Reduce what a single function does

- Do not mix multiple tasks in one function. Split by task.
- First separate work into paragraphs; then consider extracting functions. If a paragraph needs a heading, it is a candidate.
- If splitting causes the reader to bounce around and slows understanding, change how you split. Smallness is a means, not the goal.

### 9.2 Keep one level of abstraction per function

Do not mix “the point” and “the details” in one function. Separate where you write the flow versus where you write the mechanics.

- Put the flow you want the reader to see first at the top.
- Push details down into helper functions or into other modules.

### 9.3 Make parameters and return values readable

- Fewer parameters are easier to read. If they grow, bundle a coherent group into one value (struct/class).
- Do not branch on boolean parameters. Calls like `render(true)` hide meaning; prefer separate function names.
- Avoid “mutate input then return it.” It causes readers to confuse input and output. Return a new value or only mutate owned state.

### 9.4 Do not hide side effects

Do not make changes that readers cannot infer from the function name. If you change state, make it obvious via naming and placement.

### 9.5 Do not mix “change state” and “answer”

If a function both changes state and returns a value, readers often misinterpret it.

First ask questions about state, then change state. This is called **Command Query Separation**. After introducing the term, we will refer to it as “do not mix.”

- Avoid patterns like `if (setX(...))`. Readers will wonder whether it “set” or “was already set.”
- Instead of returning success/failure codes everywhere, separate the “failure path” using exceptions or explicit branching at the call site.

### 9.6 Size guidelines (numbers)

“Make it small” is not the goal, but limits help avoid indecision. If you exceed these limits, split the function or leave a comment explaining why it must be larger.

- Lines: target ≤ 20 lines. As a rule, ≤ 30 lines. Even as an exception, cap at 40 lines.
- Nesting: at most 2 levels of `if/for/while/try`. Even as an exception, cap at 3 levels.
- Parameters: up to 3. If it would become 4+, bundle them.

(When counting, you may exclude blank lines and lines that contain only `}`.)

## 10. Turn your thinking into code

Before writing tricky logic, first explain it in Japanese. Then write code that matches the explanation.

- List what conditions mean “allow” and what conditions mean “fail,” and write code in that same order.
- Reuse keywords from the explanation (e.g., `admin`, `owner`, `document`) as variable and function names.

## 11. Write less new code

Every new line becomes future cost.

- First look for a “do not write it” option. If the standard library or existing features suffice, do not add new code.
- Question whether the requirement is truly necessary, and push toward the simplest form.
- Do not build heavy mechanisms early. Add them only when needed.
- When you find duplication, consolidate it in a readable way. Do not generalize too early and confuse readers.

## 12. Tests

Tests are read, too. If tests are hard to read, people become afraid to change code. Readability matters especially for tests.

### 12.1 Properties tests should satisfy

Aim for tests that satisfy the following five properties: fast, independent, repeatable, self-validating, and timely. This is known as **FIRST** (Fast, Independent, Repeatable, Self-Validating, Timely). After introducing the term, we will treat them as “the five properties.”

- **Fast**: run quickly so they can be run often.
- **Independent**: tests should not depend on each other’s order.
- **Repeatable**: the result should be the same across machines and environments.
- **Self-validating**: failures should be detected by the test, not by reading logs.
- **Timely**: write tests with changes, or clearly state why you cannot.

### 12.2 How to write

- Tests can serve as “documentation for implementation.” Put important conditions where the reader sees them first.
- Make it obvious **why** this test exists and **what** it guarantees. Prefer: a behavior-focused test name + a 1–2 line comment at the top of the test explaining the rationale.
- Do not bury the test in setup details. Make “input / action / expectation” easy to follow.
- Write assertions so failures guide the reader toward the cause. (Assert.)
- Do not cram too many checks into one test. Too much makes failures harder to diagnose.


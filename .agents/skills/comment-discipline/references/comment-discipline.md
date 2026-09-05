# Comment discipline reference (How / What / Why / Why-not)

## 1) The channel split

Code expresses implementation; test names/assertions express expected behavior;
history records change motivation. Implementation comments preserve durable
knowledge the adjacent code cannot express: a constraint, rejected alternative,
non-obvious hazard, external requirement, or surprising rationale.

This is an information test, not a blanket ban on explanatory comments. Public
API documentation is a separate contract channel, not redundant implementation
narration. Follow the repository's documentation requirements.

## 2) Before writing or keeping a comment

Ask what the reader would lose by deleting the comment. If only a paraphrase of
the next line disappears, omit it. If a necessary constraint or reason would be
lost, retain it concisely near the affected code. A clear local name can remove
ambiguity; comment cleanup alone does not justify a new abstraction or refactor.

Scope review to the requested diff. Do not add comments to unchanged code, delete
unrelated historical notes, or impose a comment-count/line-count target.

## 3) AI-specific anti-patterns

Remove redundant forms when they carry no additional contract information:
- diff narration such as "added validation" or "now handles empty inputs";
- unsupported assurances such as "safe and robust" or "cannot break anything";
- section banners that merely label obvious setup, validation, or return steps;
- prose copies of type signatures and boilerplate docstrings for private helpers;
- per-line narration and author/date metadata already recorded by version control.

Do not delete by wording alone. "Safe because the lock remains held" may convey
a real synchronization invariant. Preserve that invariant, not empty reassurance.

## 4) Test code

Names and assertions should state behavior without repeating it above each line.
Keep a concise explanation for non-obvious fixtures, historical regressions,
protocol constraints, or deliberately unusual inputs. No mandatory test-comment
quota or arrange/act/assert banners.

## 5) Commit messages

Use English to state motivation and meaningful constraints/trade-offs. Avoid a
file-by-file diff narration. Do not copy the development conversation into code.

## 6) Carve-out: public API documentation and directives

Preserve the C++ Doxygen gate in `code-readability` §4.4 and required public API
docstrings in other languages. Document real caller contracts such as units,
ownership, lifetime, errors, and compatibility; avoid speculative guarantees.

Licenses, copyright notices, generated-file markers, type-checker/linter/compiler
directives, and suppression reasons with a real constraint are not narration.
Do not remove them to reach a lower comment count.

## 7) Quick triage table

| Added text | Decision |
| --- | --- |
| `# Increment the attempt counter` above `attempt += 1` | Remove |
| `# Now validates input safely` | Remove unsupported narration |
| Boilerplate private-helper docstring repeating its typed signature | Omit |
| `# Register only after setting state: this callback may run synchronously.` | Keep the ordering hazard |
| `# This peer rejects chunked uploads; Content-Length is required.` | Keep the external requirement |
| Public API ownership/error contract, SPDX notice, or meaningful tool directive | Preserve |

Model-specific verbosity is an evaluation target, not a reason to ban all
comments from that model. Apply the same information standard to every author.

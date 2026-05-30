# Shared mechanical checks for study-note packs

Use these checks for publication or sync safety across textbook, narrative/problem-framing, and technical-essay packs.

## Scope and privacy

- Scan only the provided `<note-root>` values.
- Report relative paths and summaries only; do not print note bodies.
- Do not use network access, private configuration, private repository URLs, or user-specific paths.
- Keep examples generic, such as `<note-root>` and `<relative-note-path>`.

## Required shared checks

- Markdown files are discoverable under the provided roots.
- Frontmatter is either absent or has a detectable closing delimiter.
- Tags/frontmatter follow the pack convention when that convention is present.
- Wikilink syntax is balanced and parseable.
- Local wikilink targets resolve when the target can be inferred from files under the provided roots.
- Unicode replacement-character corruption and multilingual text encoding issues are absent.
- Obvious binary or corruption artifacts are absent from Markdown files.

## Mode boundary

In `shared-mechanical-only` mode, do not apply textbook required headings, definition-only checks, textbook note-type contracts, or textbook semantic spot-checks.

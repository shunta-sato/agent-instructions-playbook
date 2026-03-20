#!/usr/bin/env python3
"""Create a deterministic Bug Report (RCA) artifact from the skill template."""

from __future__ import annotations

from pathlib import Path

from _skill_helper_common import (
    build_parser,
    repo_root_from_script,
    resolve_output_path,
    validate_slug,
    write_artifact,
)


def main() -> int:
    parser = build_parser(
        "Initialize reports/bug-reports/<slug>.md from bug-report template"
    )
    args = parser.parse_args()

    validate_slug(args.slug)
    repo_root = repo_root_from_script(Path(__file__))
    template_path = (
        repo_root
        / ".agents"
        / "skills"
        / "bug-investigation-and-rca"
        / "references"
        / "bug-report-template.md"
    )
    output_path = resolve_output_path(
        repo_root, args.output, f"reports/bug-reports/{args.slug}.md"
    )

    template_content = template_path.read_text(encoding="utf-8")
    write_artifact(output_path, template_content, force=args.force)

    print(f"Created Bug Report artifact: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

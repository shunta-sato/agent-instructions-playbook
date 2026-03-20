#!/usr/bin/env python3
"""Create a deterministic Concurrency Verification Matrix artifact."""

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
        "Initialize reports/concurrency/<slug>.md from matrix template"
    )
    args = parser.parse_args()

    validate_slug(args.slug)
    repo_root = repo_root_from_script(Path(__file__))
    template_path = (
        repo_root
        / ".agents"
        / "skills"
        / "thread-safety-tooling"
        / "references"
        / "concurrency-verification-matrix-template.md"
    )
    output_path = resolve_output_path(
        repo_root, args.output, f"reports/concurrency/{args.slug}.md"
    )

    template_content = template_path.read_text(encoding="utf-8")
    write_artifact(output_path, template_content, force=args.force)

    print(f"Created Concurrency Verification Matrix artifact: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Create a deterministic ExecPlan artifact from the canonical template."""

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
    parser = build_parser("Initialize plans/<slug>.md from plans/_template_execplan.md")
    args = parser.parse_args()

    validate_slug(args.slug)
    repo_root = repo_root_from_script(Path(__file__))
    template_path = repo_root / "plans" / "_template_execplan.md"
    output_path = resolve_output_path(repo_root, args.output, f"plans/{args.slug}.md")

    template_content = template_path.read_text(encoding="utf-8")
    write_artifact(output_path, template_content, force=args.force)

    print(f"Created ExecPlan artifact: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

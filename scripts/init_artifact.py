#!/usr/bin/env python3
"""Create deterministic skill artifacts from canonical templates."""

from __future__ import annotations

import argparse
from pathlib import Path


ARTIFACT_SPECS = {
    "execplan": {
        "label": "ExecPlan",
        "template": "plans/_template_execplan.md",
        "default_output": "plans/{slug}.md",
    },
    "bug-report": {
        "label": "Bug Report",
        "template": ".agents/skills/bug-investigation-and-rca/references/bug-report-template.md",
        "default_output": "reports/bug-reports/{slug}.md",
    },
    "concurrency-matrix": {
        "label": "Concurrency Verification Matrix",
        "template": ".agents/skills/thread-safety-tooling/references/concurrency-verification-matrix-template.md",
        "default_output": "reports/concurrency/{slug}.md",
    },
}


def repo_root_from_script(script_path: Path) -> Path:
    return script_path.resolve().parent.parent


def resolve_output_path(repo_root: Path, explicit_output: str, default_relpath: str) -> Path:
    if explicit_output:
        output_path = Path(explicit_output)
        if not output_path.is_absolute():
            output_path = repo_root / output_path
        return output_path
    return repo_root / default_relpath


def write_artifact(path: Path, content: str, force: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists() and path.is_file():
        existing = path.read_text(encoding="utf-8")
        if existing and not force:
            raise FileExistsError(
                f"Refusing to overwrite non-empty file: {path}. Use --force to overwrite."
            )

    path.write_text(content, encoding="utf-8")


def validate_slug(slug: str) -> None:
    if "/" in slug or "\\" in slug:
        raise ValueError("--slug must not contain path separators")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Initialize deterministic artifact files from repository templates. "
            "Use --kind to choose which artifact to generate."
        )
    )
    parser.add_argument(
        "--kind",
        required=True,
        choices=sorted(ARTIFACT_SPECS.keys()),
        help="Artifact kind to initialize",
    )
    parser.add_argument(
        "--slug",
        required=True,
        help="Artifact slug (recommended: lowercase kebab-case, e.g. ticket-4-rca)",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional explicit output path (relative to repo root or absolute path)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow overwriting an existing non-empty file",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    validate_slug(args.slug)
    repo_root = repo_root_from_script(Path(__file__))
    spec = ARTIFACT_SPECS[args.kind]

    template_path = repo_root / spec["template"]
    default_output = spec["default_output"].format(slug=args.slug)
    output_path = resolve_output_path(repo_root, args.output, default_output)

    template_content = template_path.read_text(encoding="utf-8")
    write_artifact(output_path, template_content, force=args.force)

    print(f"Created {spec['label']} artifact: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

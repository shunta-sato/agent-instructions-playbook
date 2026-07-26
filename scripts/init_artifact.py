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
    "failure-retrospective": {
        "label": "Failure Retrospective",
        # Multi-file pack: "files" replaces the single-file "template" /
        # "default_output" pair. See create_artifact()'s branch below.
        "files": [
            {
                "template": ".agents/skills/failure-retrospective/templates/record.json",
                "default_output": "reports/retrospectives/{slug}/record.json",
            },
            {
                "template": ".agents/skills/failure-retrospective/templates/report.md",
                "default_output": "reports/retrospectives/{slug}/report.md",
            },
        ],
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

    if path.is_dir():
        raise IsADirectoryError(f"Refusing to write artifact over existing directory: {path}")

    if path.exists() and path.is_file():
        existing = path.read_text(encoding="utf-8")
        if existing and not force:
            raise FileExistsError(
                f"Refusing to overwrite non-empty file: {path}. Use --force to overwrite."
            )

    path.write_text(content, encoding="utf-8")


def validate_slug(slug: str) -> None:
    if "/" in slug or "\\" in slug or ".." in slug or Path(slug).is_absolute():
        raise ValueError(
            "--slug must not contain path separators, '..', or an absolute path marker"
        )


def _create_pack(repo_root: Path, spec: dict, slug: str, force: bool) -> list[Path]:
    """Create every file in a multi-file pack spec, or none at all.

    Files are written in spec order. If a later file cannot be created
    (conflict or unexpected error), the files this invocation itself just
    created are removed before re-raising, so no half-pack is left on
    disk. Pre-existing files — kept on refusal, or overwritten under
    --force — are never touched by the rollback.
    """
    entries = [
        (repo_root / entry["template"], repo_root / entry["default_output"].format(slug=slug))
        for entry in spec["files"]
    ]

    created: list[Path] = []
    try:
        for template_path, output_path in entries:
            existed_before = output_path.exists()
            template_content = template_path.read_text(encoding="utf-8")
            write_artifact(output_path, template_content, force=force)
            if not existed_before:
                created.append(output_path)
    except Exception:
        for path in created:
            path.unlink(missing_ok=True)
        raise

    return [output_path for _, output_path in entries]


def create_artifact(
    repo_root: Path, kind: str, slug: str, output: str = "", force: bool = False
) -> list[Path]:
    """Resolve and write the artifact(s) for one initializer invocation.

    Returns every path written, in spec order. Kept separate from main()
    so tests can call it directly against a temporary repo_root without
    touching the real repository tree or shelling out.
    """
    validate_slug(slug)
    spec = ARTIFACT_SPECS[kind]

    if "files" in spec:
        if output:
            raise ValueError("--output is not supported for multi-file pack kinds")
        return _create_pack(repo_root, spec, slug, force)

    template_path = repo_root / spec["template"]
    default_output = spec["default_output"].format(slug=slug)
    output_path = resolve_output_path(repo_root, output, default_output)
    template_content = template_path.read_text(encoding="utf-8")
    write_artifact(output_path, template_content, force=force)
    return [output_path]


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
        help=(
            "Optional explicit output path (relative to repo root or absolute path). "
            "Not supported for multi-file pack kinds."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow overwriting an existing non-empty file",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    repo_root = repo_root_from_script(Path(__file__))
    spec = ARTIFACT_SPECS[args.kind]
    output_paths = create_artifact(repo_root, args.kind, args.slug, args.output, args.force)

    for output_path in output_paths:
        print(f"Created {spec['label']} artifact: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Shared utilities for skill artifact bootstrap helpers."""

from __future__ import annotations

import argparse
from pathlib import Path


def repo_root_from_script(script_path: Path) -> Path:
    return script_path.resolve().parent.parent


def build_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
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

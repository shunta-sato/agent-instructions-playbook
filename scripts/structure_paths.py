#!/usr/bin/env python3
"""Repo-relative path normalization and confinement for baseline entries.

This module has one job: decide whether a baseline entry's ``path`` string
is safe to trust. It knows nothing about baseline schema, findings, or
reconciliation (see ``structure_baseline.py``, which is the only caller).

- ``normalize_entry_path`` is a pure string transform (no filesystem
  access) so path aliases like ``x.py`` and ``./x.py`` collapse to the same
  string before duplicate detection and finding-matching ever run.
- ``path_escape`` rejects anything that could let a baseline entry point
  outside the repository root: an absolute path, a ``..`` traversal
  segment, or a symlink anywhere in the path chain (parent directory or
  leaf) — even one that happens to resolve back inside the repo, since
  accepted debt must never depend on a detail of one particular checkout.
"""

from __future__ import annotations

from pathlib import Path, PurePosixPath


def normalize_entry_path(raw_path: str) -> str:
    """Collapse redundant ``.`` segments and duplicate slashes.

    A literal ``..`` segment is preserved (not collapsed) so
    :func:`path_escape` can still see and reject it.
    """
    return PurePosixPath(raw_path).as_posix()


def path_escape(normalized_path: str) -> str | None:
    """Return a detail message if ``normalized_path`` escapes repo-root
    confinement, or ``None`` if it is confined and symlink-free.

    Rejects an absolute path or a ``..`` segment outright, even one that
    would resolve back inside the repo. Rejects any symlink in the chain
    from ``Path.cwd()`` to the target (parent directory or leaf). Also
    rejects a path resolving outside ``Path.cwd().resolve()``, as defense
    in depth.
    """
    candidate = PurePosixPath(normalized_path)
    if candidate.is_absolute():
        return f"path {normalized_path!r} is absolute; must be repo-relative"
    if ".." in candidate.parts:
        return f"path {normalized_path!r} contains a '..' traversal segment"

    cwd = Path.cwd()
    current = cwd
    for part in candidate.parts:
        current = current / part
        if current.is_symlink():
            return (
                f"path {normalized_path!r} passes through a symlink at "
                f"{current.as_posix()!r}; baseline paths must be real files"
            )
    try:
        current.resolve().relative_to(cwd.resolve())
    except ValueError:
        return f"path {normalized_path!r} resolves outside the repository root"
    return None

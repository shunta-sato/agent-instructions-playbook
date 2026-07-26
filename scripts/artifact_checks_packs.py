#!/usr/bin/env python3
"""Pack-shaped artifact checks for the artifact lint (Wave 1, W-B).

Sibling of ``artifact_checks_docs`` (heading-based checks, owned by W-A).
Both share one signature so ``lint_artifacts.py`` can dispatch by
``spec["checker"]`` without knowing which module implements it::

    run_checks(repo_root: Path, artifact_path: Path, spec: dict, registry: dict) -> list[str]

``artifact_path`` is a directory for every check except ``subset_schema``,
where the registry's ``detect_glob`` matches a single instance file and
``artifact_path`` IS that file. Each check is driven entirely by the
presence of its spec key (``.agents/artifact-registry.json``); a key that is
absent means the check is skipped for that artifact kind. Findings are
stable id strings of the form ``<rule>:<detail>`` (or bare ``<rule>`` when
there is no natural per-item detail), designed to be diffed against a
committed baseline by the caller.

``subset_schema`` is an HONEST SUBSET of JSON Schema validation: it checks
only that the schema's top-level ``required`` keys are present in the
instance, and — if the schema constrains ``budget_results[].result`` to an
enum — that every ``result`` value in the instance is a member of that
enum. It does not validate types, formats, nested ``required``, additional
schema keywords, or anything else a full JSON Schema validator would.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

CATALOG_INDEX_FILENAME = "catalog_index.yaml"
# Any src/href pointing at an absolute or protocol-relative URL breaks the
# self-containment guarantee, regardless of casing or spacing.
REMOTE_REF_RE = re.compile(r"(?i)(?:src|href)\s*=\s*[\"']?(?:https?:)?//")


def _safe_get(node, *keys):
    """Walk a nested dict by key; return None at the first missing/non-dict step."""
    for key in keys:
        if not isinstance(node, dict) or key not in node:
            return None
        node = node[key]
    return node


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def _check_required_files(artifact_path: Path, spec: dict) -> list[str]:
    findings = []
    for rel in spec.get("required_files", []):
        if not (artifact_path / rel).is_file():
            findings.append(f"missing-file:{rel}")
    return findings


def _check_json_parse(artifact_path: Path, spec: dict) -> list[str]:
    findings = []
    for rel in spec.get("json_parse", []):
        path = artifact_path / rel
        if not path.exists():
            continue
        text = _read_text(path)
        try:
            json.loads(text if text is not None else "")
        except json.JSONDecodeError:
            findings.append(f"json-parse:{rel}")
    return findings


def _check_forbid_fill_sentinel(artifact_path: Path, spec: dict) -> list[str]:
    if not spec.get("forbid_fill_sentinel"):
        return []
    findings = []
    for dirpath, _dirnames, filenames in os.walk(artifact_path, followlinks=False):
        base = Path(dirpath)
        for name in filenames:
            path = base / name
            if path.is_symlink():
                continue  # reported by forbid_symlinks; do not read through it
            text = _read_text(path)
            if text is not None and "<fill" in text:
                rel = path.relative_to(artifact_path).as_posix()
                findings.append(f"fill-sentinel:{rel}")
    return findings


def _check_forbid_symlinks(artifact_path: Path, spec: dict) -> list[str]:
    if not spec.get("forbid_symlinks"):
        return []
    findings = []
    if artifact_path.is_symlink():
        findings.append("symlink-in-pack:.")
    for dirpath, dirnames, filenames in os.walk(artifact_path, followlinks=False):
        base = Path(dirpath)
        for name in list(dirnames) + list(filenames):
            path = base / name
            if path.is_symlink():
                rel = path.relative_to(artifact_path).as_posix()
                findings.append(f"symlink-in-pack:{rel}")
    return findings


def _check_token_refs_in(
    repo_root: Path, artifact_path: Path, spec: dict, registry: dict
) -> list[str]:
    rel = spec.get("token_refs_in")
    if not rel:
        return []
    path = artifact_path / rel
    if not path.exists():
        return []
    text = _read_text(path)
    try:
        data = json.loads(text if text is not None else "")
    except json.JSONDecodeError:
        return []  # json_parse (if configured) already reports the parse failure
    token_refs = _safe_get(data, "meta", "tone_and_manner", "token_refs")
    if token_refs is None:
        return []  # the block being absent is NOT a finding
    if not isinstance(token_refs, dict):
        return ["token-refs:bad-shape"]
    rule = registry.get("token_refs_rule", {})
    required_prefix = rule.get("required_prefix", "")
    suffixes = rule.get("suffixes", {})
    findings = []
    for kind, ref in token_refs.items():
        if kind not in suffixes:
            findings.append(f"token-refs:unknown-kind:{kind}")
            continue
        if not isinstance(ref, str) or not ref:
            findings.append(f"token-refs:bad-type:{kind}")
            continue
        if ref.startswith("/"):
            findings.append(f"token-refs:absolute:{ref}")
        if any(segment == ".." for segment in ref.split("/")):
            findings.append(f"token-refs:traversal:{ref}")
        if not ref.startswith(required_prefix):
            findings.append(f"token-refs:prefix:{ref}")
        if not ref.endswith(suffixes[kind]):
            findings.append(f"token-refs:suffix:{ref}")
        if not (repo_root / ref).exists():
            findings.append(f"token-refs:missing:{ref}")
    return findings


def _check_preview_addon(artifact_path: Path, spec: dict) -> list[str]:
    addon = spec.get("preview_addon")
    if not addon:
        return []
    trigger_rel = addon.get("trigger_file")
    if not trigger_rel:
        return []
    trigger_path = artifact_path / trigger_rel
    if not trigger_path.exists():
        return []  # addon is opt-in; absent trigger means the addon does not apply
    findings = []
    for rel in addon.get("required_files", []):
        if not (artifact_path / rel).is_file():
            findings.append(f"preview-missing:{rel}")
    text = _read_text(trigger_path) or ""
    must_contain = addon.get("trigger_file_must_contain")
    if must_contain and must_contain not in text:
        findings.append("preview:no-inline-spec")
    if addon.get("forbid_remote_script_src") and REMOTE_REF_RE.search(text):
        findings.append("preview:remote-script")
    return findings


def _check_catalog_cross_check(artifact_path: Path, spec: dict) -> list[str]:
    cc = spec.get("catalog_cross_check")
    if not cc:
        return []
    catalog_path = artifact_path / CATALOG_INDEX_FILENAME
    if not catalog_path.exists():
        return []  # required_files (if configured) already reports the missing file
    text = _read_text(catalog_path) or ""
    if "id_pattern" not in cc:
        raise SystemExit("artifact-lint: catalog_cross_check needs id_pattern")
    ids = re.findall(cc["id_pattern"], text, re.MULTILINE)
    if not ids:
        return ["catalog-empty"]
    findings = []
    for artifact_id in ids:
        for template in cc.get("per_id_files", []):
            rel = template.format(id=artifact_id)
            if not (artifact_path / rel).is_file():
                findings.append(f"catalog-missing:{rel}")
    return findings


def _check_subset_schema(repo_root: Path, artifact_path: Path, spec: dict) -> list[str]:
    schema_rel = spec.get("subset_schema")
    if not schema_rel:
        return []
    schema_path = repo_root / schema_rel
    if not schema_path.is_file():
        raise SystemExit(f"artifact-lint: subset_schema file not found: {schema_path}")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    text = _read_text(artifact_path)
    try:
        instance = json.loads(text if text is not None else "")
    except json.JSONDecodeError:
        return [f"json-parse:{artifact_path.name}"]
    findings = []
    for key in schema.get("required", []):
        if not isinstance(instance, dict) or key not in instance:
            findings.append(f"subset-schema:missing-key:{key}")
    enum = _safe_get(
        schema, "properties", "budget_results", "items", "properties", "result", "enum"
    )
    if enum and isinstance(instance, dict):
        for item in instance.get("budget_results") or []:
            if isinstance(item, dict) and "result" in item and item["result"] not in enum:
                findings.append(f"subset-schema:bad-result:{item['result']}")
    return findings


def run_checks(repo_root: Path, artifact_path: Path, spec: dict, registry: dict) -> list[str]:
    """Run every pack check whose spec key is present; return stable finding ids."""
    findings: list[str] = []
    findings += _check_required_files(artifact_path, spec)
    findings += _check_json_parse(artifact_path, spec)
    findings += _check_forbid_fill_sentinel(artifact_path, spec)
    findings += _check_forbid_symlinks(artifact_path, spec)
    findings += _check_token_refs_in(repo_root, artifact_path, spec, registry)
    findings += _check_preview_addon(artifact_path, spec)
    findings += _check_catalog_cross_check(artifact_path, spec)
    findings += _check_subset_schema(repo_root, artifact_path, spec)
    return findings

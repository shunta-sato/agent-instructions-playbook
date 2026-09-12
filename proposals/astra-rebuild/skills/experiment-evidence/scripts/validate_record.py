#!/usr/bin/env python3
"""Check an evidence record against an independently supplied claim contract."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any

IDENTITY_KEYS = {"source", "build", "target", "workload", "configuration", "environment"}
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def evidence_file(root: Path, value: Any) -> Path:
    if not text(value) or "\\" in value:
        raise ValueError("evidence path must be a relative POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or ":" in value:
        raise ValueError("evidence path escapes its dedicated root")
    current = root
    for part in path.parts:
        current /= part
        if current.is_symlink():
            raise ValueError("evidence symlinks are not allowed")
    if not current.is_file() or not current.resolve().is_relative_to(root.resolve()):
        raise ValueError("evidence artifact is missing or outside its dedicated root")
    return current


def validate(contract: dict[str, Any], record: dict[str, Any], root: Path,
             contract_digest: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(contract, dict) or not isinstance(record, dict):
        return ["contract and record must be objects"]
    if contract.get("version") != 1 or record.get("version") != 1:
        errors.append("contract and record version must be 1")
    if not text(contract.get("use_id")) or record.get("use_id") != contract.get("use_id"):
        errors.append("use_id mismatch or missing")
    if record.get("contract_sha256") != contract_digest:
        errors.append("contract digest mismatch")
    identity = contract.get("identity")
    if not isinstance(identity, dict) or set(identity) != IDENTITY_KEYS or not all(map(text, identity.values())):
        errors.append("contract identity must identify source/build/target/workload/configuration/environment")
    if record.get("identity") != identity:
        errors.append("record identity does not match the claim contract")
    conditions = contract.get("conditions")
    results = record.get("results")
    if not isinstance(conditions, list) or not conditions:
        return errors + ["conditions must be a non-empty list"]
    if not isinstance(results, list):
        return errors + ["results must be a list"]
    expected: dict[str, dict[str, Any]] = {}
    for condition in conditions:
        if not isinstance(condition, dict) or not text(condition.get("id")):
            errors.append("condition needs an id")
            continue
        key = condition["id"]
        if key in expected:
            errors.append(f"duplicate condition: {key}")
        expected[key] = condition
        if not isinstance(condition.get("obligation"), str) or condition.get("obligation") not in {"required", "target", "out-of-scope"}:
            errors.append(f"invalid obligation: {key}")
        if not all(text(condition.get(field)) for field in ("source", "criterion", "method")):
            errors.append(f"condition lacks source/criterion/method: {key}")
        if condition.get("obligation") == "out-of-scope" and not text(condition.get("reason")):
            errors.append(f"out-of-scope condition needs a reason: {key}")
    seen: set[str] = set()
    for result in results:
        if not isinstance(result, dict) or not text(result.get("id")):
            errors.append("result needs an id")
            continue
        key = result["id"]
        if key in seen:
            errors.append(f"duplicate result: {key}")
        seen.add(key)
        if key not in expected:
            errors.append(f"unknown result: {key}")
            continue
        condition = expected[key]
        if set(result) - {"id", "status", "method", "artifacts", "limits"}:
            errors.append(f"unsupported result fields (a record cannot change obligations): {key}")
        status = result.get("status")
        if not isinstance(status, str) or status not in {"pass", "fail", "not-measured", "not-applicable"}:
            errors.append(f"invalid result status: {key}")
        if condition.get("obligation") == "required" and status != "pass":
            errors.append(f"required condition has not passed: {key}")
        if status == "pass" and condition.get("obligation") == "out-of-scope":
            errors.append(f"out-of-scope is not a passing measurement: {key}")
        if result.get("method") != condition.get("method"):
            errors.append(f"method mismatch: {key}")
        artifacts = result.get("artifacts", [])
        if not isinstance(artifacts, list):
            errors.append(f"artifacts must be a list: {key}")
            continue
        if status == "pass" and not artifacts:
            errors.append(f"pass has no artifacts: {key}")
        for artifact in artifacts:
            if not isinstance(artifact, dict) or not isinstance(artifact.get("sha256"), str) or not SHA256.fullmatch(artifact["sha256"]):
                errors.append(f"invalid artifact digest: {key}")
                continue
            try:
                path = evidence_file(root, artifact.get("path"))
                if digest(path) != artifact["sha256"]:
                    errors.append(f"artifact digest mismatch: {key}")
            except (ValueError, OSError) as exc:
                errors.append(f"{key}: {exc}")
    for key, condition in expected.items():
        if condition.get("obligation") == "required" and key not in seen:
            errors.append(f"missing required result: {key}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("record", type=Path)
    parser.add_argument("--evidence-root", required=True, type=Path,
                        help="dedicated artifact directory; never a secrets directory")
    args = parser.parse_args()
    try:
        errors = validate(json.loads(args.contract.read_text()), json.loads(args.record.read_text()),
                          args.evidence_root.resolve(strict=True), digest(args.contract))
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    if errors:
        print("Evidence rejected:\n" + "\n".join(f"- {error}" for error in errors))
        return 1
    print("Declared contract is structurally supported. This is not authentication, scientific validation or release authorization.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Extract optional token usage from Codex CLI JSONL output."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any


TOKEN_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
)


def iter_json_events(path: Path) -> Iterator[dict[str, Any]]:
    if not path.is_file():
        raise ValueError(f"{path}: file is missing")

    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON: {exc.msg}") from exc
        if not isinstance(event, dict):
            raise ValueError(f"{path}:{line_no}: expected JSON object")
        yield event


def token_payloads(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        if any(field in value for field in TOKEN_FIELDS):
            yield value
        for child in value.values():
            yield from token_payloads(child)
    elif isinstance(value, list):
        for child in value:
            yield from token_payloads(child)


def integer_token(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def normalize_token_payload(payload: dict[str, Any]) -> dict[str, int] | None:
    normalized: dict[str, int] = {}
    for field in TOKEN_FIELDS:
        token_value = integer_token(payload.get(field))
        if token_value is not None:
            normalized[field] = token_value
    return normalized or None


def extract_telemetry_from_file(path: Path) -> dict[str, Any]:
    events_read = 0
    latest_tokens: dict[str, int] | None = None

    for event in iter_json_events(path):
        events_read += 1
        for payload in token_payloads(event):
            normalized = normalize_token_payload(payload)
            if normalized is not None:
                latest_tokens = normalized

    result: dict[str, Any] = {
        "status": "not_collected",
        "source": "codex_jsonl",
        "source_path": path.as_posix(),
        "events_read": events_read,
    }
    if latest_tokens is not None:
        result.update(latest_tokens)
        result["status"] = "collected"
    return result


def render_text(telemetry: dict[str, Any]) -> str:
    lines = [
        f"status: {telemetry['status']}",
        f"source: {telemetry['source']}",
        f"events_read: {telemetry['events_read']}",
    ]
    for field in TOKEN_FIELDS:
        if field in telemetry:
            lines.append(f"{field}: {telemetry[field]}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract optional token usage from Codex CLI JSONL output."
    )
    parser.add_argument("jsonl_path", help="Path to Codex CLI JSONL output.")
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="text",
        help="Output format.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        telemetry = extract_telemetry_from_file(Path(args.jsonl_path))
    except ValueError as exc:
        print(f"Codex JSONL parse failed: {exc}")
        return 1

    if args.format == "json":
        print(json.dumps(telemetry, indent=2, sort_keys=True))
    else:
        print(render_text(telemetry))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

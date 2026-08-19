#!/usr/bin/env python3
"""Collect read-only mobile project facts for preflight-mobile-app."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SECRET_NAMES = {
    ".env",
    "google-services.json",
    "GoogleService-Info.plist",
    "key.properties",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect mobile project structure without reading secret values.")
    parser.add_argument("--root", default=".", help="Repository root to inspect.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--markdown", action="store_true", help="Emit Markdown output.")
    return parser.parse_args()


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def existing(root: Path, patterns: list[str]) -> list[str]:
    values: set[str] = set()
    for pattern in patterns:
        for path in root.glob(pattern):
            if path.exists():
                values.add(rel(path, root))
    return sorted(values)


def safe_text(path: Path) -> str:
    if path.name in SECRET_NAMES or any(part.lower() in {"secrets", "credentials"} for part in path.parts):
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def inspect(root: Path) -> dict[str, Any]:
    root = root.resolve()
    pubspec = root / "pubspec.yaml"
    pubspec_text = safe_text(pubspec) if pubspec.exists() else ""

    flutter_signals = existing(
        root,
        [
            "pubspec.yaml",
            ".metadata",
            "lib/main.dart",
            ".fvmrc",
            ".fvm/fvm_config.json",
            "mise.toml",
        ],
    )
    flutter_detected = pubspec.exists() and ("sdk: flutter" in pubspec_text or "flutter:" in pubspec_text)

    ios_paths = existing(
        root,
        [
            "ios/*.xcodeproj",
            "ios/*.xcworkspace",
            "ios/**/Info.plist",
            "ios/**/*.entitlements",
            "ios/Podfile",
            "*.xcodeproj",
            "*.xcworkspace",
        ],
    )
    android_paths = existing(
        root,
        [
            "android/settings.gradle",
            "android/settings.gradle.kts",
            "android/build.gradle",
            "android/build.gradle.kts",
            "android/gradlew",
            "android/**/AndroidManifest.xml",
            "settings.gradle",
            "settings.gradle.kts",
            "gradlew",
            "**/AndroidManifest.xml",
        ],
    )
    native_paths = existing(
        root,
        [
            "android/**/*.kt",
            "android/**/*.java",
            "ios/**/*.swift",
            "ios/**/*.m",
            "ios/**/*.mm",
            "ios/**/*.h",
            "lib/**/*.dart",
        ],
    )
    ffi_candidates = []
    for path_text in native_paths:
        if not path_text.endswith(".dart"):
            continue
        text = safe_text(root / path_text)
        if "dart:ffi" in text or "package:ffi/" in text or "NativeAssets" in text:
            ffi_candidates.append(path_text)

    implementation_model = "unknown"
    evidence: list[str] = []
    if flutter_detected:
        implementation_model = "flutter"
        evidence.append("pubspec.yaml declares Flutter SDK usage")
    elif ios_paths and android_paths:
        implementation_model = "dual-native-or-other-cross-platform"
        evidence.append("both iOS and Android project surfaces detected without confirmed Flutter SDK declaration")
    elif ios_paths:
        implementation_model = "ios-native-or-unknown"
        evidence.append("iOS project surface detected")
    elif android_paths:
        implementation_model = "android-native-or-unknown"
        evidence.append("Android project surface detected")

    secret_like_paths = existing(
        root,
        [
            "**/.env",
            "**/.env.*",
            "**/*.pem",
            "**/*.p12",
            "**/*.jks",
            "**/*.keystore",
            "**/google-services.json",
            "**/GoogleService-Info.plist",
            "**/key.properties",
        ],
    )

    return {
        "implementation_model": implementation_model,
        "evidence": evidence,
        "flutter": {
            "detected": flutter_detected,
            "signals": flutter_signals,
            "test_paths": existing(root, ["test", "integration_test"]),
        },
        "ios": {"detected": bool(ios_paths), "paths": ios_paths},
        "android": {"detected": bool(android_paths), "paths": android_paths},
        "native_boundaries": {
            "ffi_candidates": sorted(ffi_candidates),
            "platform_source_count": len([p for p in native_paths if not p.endswith(".dart")]),
        },
        "secret_like_paths": secret_like_paths,
        "notes": [
            "Secret-like paths are reported by path only; contents are not read.",
            "Toolchain versions, signing readiness, devices, and canonical commands require executable/project evidence and remain unknown here.",
        ],
    }


def render_markdown(result: dict[str, Any]) -> str:
    lines = ["# Mobile project inspection", ""]
    lines.append(f"- Implementation model: `{result['implementation_model']}`")
    lines.append(f"- Flutter detected: `{result['flutter']['detected']}`")
    lines.append(f"- iOS surface detected: `{result['ios']['detected']}`")
    lines.append(f"- Android surface detected: `{result['android']['detected']}`")
    lines.append("")

    for title, values in (
        ("Evidence", result["evidence"]),
        ("Flutter signals", result["flutter"]["signals"]),
        ("iOS paths", result["ios"]["paths"]),
        ("Android paths", result["android"]["paths"]),
        ("FFI candidates", result["native_boundaries"]["ffi_candidates"]),
        ("Secret-like paths (path only)", result["secret_like_paths"]),
        ("Notes", result["notes"]),
    ):
        lines.extend([f"## {title}", ""])
        lines.extend([f"- `{value}`" for value in values] or ["- none found"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    result = inspect(Path(args.root))
    emit_json = args.json or not args.markdown
    if emit_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    if args.markdown:
        if emit_json:
            print()
        print(render_markdown(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

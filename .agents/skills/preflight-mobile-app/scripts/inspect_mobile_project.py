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
SKIP_PARTS = {
    ".git",
    ".dart_tool",
    ".expo",
    ".gradle",
    ".idea",
    ".next",
    "Pods",
    "build",
    "dist",
    "node_modules",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect mobile project structure without reading secret values.")
    parser.add_argument("--root", default=".", help="Repository root to inspect.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--markdown", action="store_true", help="Emit Markdown output.")
    return parser.parse_args()


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def allowed(path: Path, root: Path) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return False
    return not any(part in SKIP_PARTS for part in parts)


def existing(root: Path, patterns: list[str]) -> list[str]:
    values: set[str] = set()
    for pattern in patterns:
        for path in root.glob(pattern):
            if path.exists() and allowed(path, root):
                values.add(rel(path, root))
    return sorted(values)


def safe_text(path: Path) -> str:
    if path.name in SECRET_NAMES or any(part.lower() in {"secrets", "credentials"} for part in path.parts):
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def json_object(path: Path) -> dict[str, Any]:
    text = safe_text(path)
    if not text:
        return {}
    try:
        value = json.loads(text)
    except (json.JSONDecodeError, OSError):
        return {}
    return value if isinstance(value, dict) else {}


def string_map(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {str(key): str(item) for key, item in value.items() if isinstance(item, (str, int, float))}


def dependency_map(package: dict[str, Any]) -> dict[str, str]:
    merged: dict[str, str] = {}
    for field in ("dependencies", "devDependencies", "peerDependencies"):
        merged.update(string_map(package.get(field)))
    return merged


def inspect(root: Path) -> dict[str, Any]:
    root = root.resolve()
    pubspec = root / "pubspec.yaml"
    pubspec_text = safe_text(pubspec) if pubspec.exists() else ""
    package_path = root / "package.json"
    package = json_object(package_path) if package_path.exists() else {}
    dependencies = dependency_map(package)
    scripts = string_map(package.get("scripts"))
    script_names = sorted(scripts)

    flutter_signals = existing(
        root,
        ["pubspec.yaml", ".metadata", "lib/main.dart", ".fvmrc", ".fvm/fvm_config.json", "mise.toml"],
    )
    flutter_detected = pubspec.exists() and ("sdk: flutter" in pubspec_text or "flutter:" in pubspec_text)

    app_config_paths = existing(root, ["app.json", "app.config.js", "app.config.ts"])
    app_json = json_object(root / "app.json") if (root / "app.json").is_file() else {}
    app_json_has_expo = isinstance(app_json.get("expo"), dict)
    react_native_detected = "react-native" in dependencies
    expo_detected = "expo" in dependencies or app_json_has_expo or bool(app_config_paths and react_native_detected)

    ios_paths = existing(
        root,
        ["ios/*.xcodeproj", "ios/*.xcworkspace", "ios/**/Info.plist", "ios/**/*.entitlements", "ios/Podfile", "*.xcodeproj", "*.xcworkspace"],
    )
    android_paths = existing(
        root,
        ["android/settings.gradle", "android/settings.gradle.kts", "android/build.gradle", "android/build.gradle.kts", "android/gradlew", "android/**/AndroidManifest.xml", "settings.gradle", "settings.gradle.kts", "gradlew", "**/AndroidManifest.xml"],
    )
    native_paths = existing(
        root,
        ["android/**/*.kt", "android/**/*.java", "ios/**/*.swift", "ios/**/*.m", "ios/**/*.mm", "ios/**/*.h", "lib/**/*.dart", "modules/**/*.kt", "modules/**/*.swift", "packages/**/*.kt", "packages/**/*.swift"],
    )
    ffi_candidates: list[str] = []
    for path_text in native_paths:
        if not path_text.endswith(".dart"):
            continue
        text = safe_text(root / path_text)
        if "dart:ffi" in text or "package:ffi/" in text or "NativeAssets" in text:
            ffi_candidates.append(path_text)

    package_manager = "unknown"
    lockfiles = existing(root, ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lock", "bun.lockb"])
    package_manager_field = package.get("packageManager")
    if isinstance(package_manager_field, str) and package_manager_field.strip():
        package_manager = package_manager_field.split("@", 1)[0]
    elif "pnpm-lock.yaml" in lockfiles:
        package_manager = "pnpm"
    elif "yarn.lock" in lockfiles:
        package_manager = "yarn"
    elif any(path in lockfiles for path in ("bun.lock", "bun.lockb")):
        package_manager = "bun"
    elif "package-lock.json" in lockfiles:
        package_manager = "npm"

    implementation_model = "unknown"
    evidence: list[str] = []
    if expo_detected and react_native_detected:
        implementation_model = "react-native-expo"
        evidence.append("package/app configuration declares React Native with Expo")
    elif react_native_detected:
        implementation_model = "react-native-bare-or-brownfield"
        evidence.append("package.json declares React Native without confirmed Expo usage")
    elif flutter_detected:
        implementation_model = "flutter"
        evidence.append("pubspec.yaml declares Flutter SDK usage")
    elif ios_paths and android_paths:
        implementation_model = "dual-native-or-other-cross-platform"
        evidence.append("both iOS and Android project surfaces detected without a confirmed cross-platform framework")
    elif ios_paths:
        implementation_model = "ios-native-or-unknown"
        evidence.append("iOS project surface detected")
    elif android_paths:
        implementation_model = "android-native-or-unknown"
        evidence.append("Android project surface detected")

    native_project_model = "unknown"
    if expo_detected and ios_paths and android_paths:
        native_project_model = "committed-native-projects"
    elif expo_detected and not ios_paths and not android_paths:
        native_project_model = "expo-cng"
    elif react_native_detected and (ios_paths or android_paths):
        native_project_model = "bare-or-brownfield"

    development_build = "expo-dev-client" in dependencies
    runtime_path = "unknown"
    if development_build:
        runtime_path = "development-build"
    elif expo_detected:
        runtime_path = "expo-go-or-development-build"

    maestro_paths = existing(root, [".maestro", ".maestro/**/*.yaml", ".maestro/**/*.yml", "maestro/**/*.yaml", "maestro/**/*.yml"])
    playwright_paths = existing(root, ["playwright.config.js", "playwright.config.ts", "playwright.config.mjs", "playwright.config.cjs"])
    eas_paths = existing(root, ["eas.json", ".eas/workflows", ".eas/workflows/**/*.yml", ".eas/workflows/**/*.yaml"])

    agent_device_detected = (
        "agent-device" in dependencies
        or any("agent-device" in command for command in scripts.values())
        or bool(existing(root, ["**/*.ad"]))
    )
    argent_detected = "argent" in dependencies or any("argent" in command for command in scripts.values())

    secret_like_paths = existing(
        root,
        ["**/.env", "**/.env.*", "**/*.pem", "**/*.p12", "**/*.jks", "**/*.keystore", "**/google-services.json", "**/GoogleService-Info.plist", "**/key.properties"],
    )

    return {
        "implementation_model": implementation_model,
        "evidence": evidence,
        "javascript": {
            "package_json": "package.json" if package_path.is_file() else None,
            "package_manager": package_manager,
            "lockfiles": lockfiles,
            "node_engine": string_map(package.get("engines")).get("node", "unknown"),
            "script_names": script_names,
        },
        "react_native": {
            "detected": react_native_detected,
            "version_range": dependencies.get("react-native", "unknown"),
            "native_project_model": native_project_model,
        },
        "expo": {
            "detected": expo_detected,
            "version_range": dependencies.get("expo", "unknown"),
            "config_paths": app_config_paths,
            "eas_paths": eas_paths,
            "router": "expo-router" in dependencies,
            "updates": "expo-updates" in dependencies,
            "development_build": development_build,
            "runtime_path": runtime_path,
        },
        "testing": {
            "jest": "jest" in dependencies or "jest-expo" in dependencies,
            "react_native_testing_library": "@testing-library/react-native" in dependencies,
            "maestro_paths": maestro_paths,
            "playwright_paths": playwright_paths,
        },
        "runtime_harness": {
            "agent_device_detected": agent_device_detected,
            "argent_detected": argent_detected,
        },
        "flutter": {
            "detected": flutter_detected,
            "signals": flutter_signals,
            "test_paths": existing(root, ["test", "integration_test"]),
        },
        "ios": {"detected": bool(ios_paths) or (expo_detected and native_project_model == "expo-cng"), "paths": ios_paths},
        "android": {"detected": bool(android_paths) or (expo_detected and native_project_model == "expo-cng"), "paths": android_paths},
        "native_boundaries": {
            "ffi_candidates": sorted(ffi_candidates),
            "platform_source_count": len([path for path in native_paths if not path.endswith(".dart")]),
        },
        "secret_like_paths": secret_like_paths,
        "notes": [
            "Secret-like paths are reported by path only; contents are not read.",
            "Dynamic Expo app config files are detected by path and are not executed.",
            "Toolchain versions, signing readiness, devices, accounts, endpoints, and canonical command results require executable/project evidence and remain unknown here.",
        ],
    }


def render_markdown(result: dict[str, Any]) -> str:
    lines = ["# Mobile project inspection", ""]
    lines.append(f"- Implementation model: `{result['implementation_model']}`")
    lines.append(f"- React Native detected: `{result['react_native']['detected']}`")
    lines.append(f"- Expo detected: `{result['expo']['detected']}`")
    lines.append(f"- Flutter detected: `{result['flutter']['detected']}`")
    lines.append(f"- iOS surface enabled/detected: `{result['ios']['detected']}`")
    lines.append(f"- Android surface enabled/detected: `{result['android']['detected']}`")
    lines.append(f"- Maestro paths: `{len(result['testing']['maestro_paths'])}`")
    lines.append(f"- agent-device detected: `{result['runtime_harness']['agent_device_detected']}`")
    lines.append("")

    for title, values in (
        ("Evidence", result["evidence"]),
        ("JavaScript lockfiles", result["javascript"]["lockfiles"]),
        ("Expo config/EAS paths", result["expo"]["config_paths"] + result["expo"]["eas_paths"]),
        ("Maestro paths", result["testing"]["maestro_paths"]),
        ("Playwright paths", result["testing"]["playwright_paths"]),
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

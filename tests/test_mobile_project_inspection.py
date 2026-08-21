from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / ".agents/skills/preflight-mobile-app/scripts/inspect_mobile_project.py"
SPEC = importlib.util.spec_from_file_location("inspect_mobile_project", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class MobileProjectInspectionTest(unittest.TestCase):
    def test_detects_expo_react_native_maestro_and_agent_device(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "packageManager": "pnpm@10.0.0",
                        "engines": {"node": ">=22"},
                        "dependencies": {
                            "expo": "~55.0.0",
                            "react-native": "0.82.0",
                            "expo-router": "~7.0.0",
                            "expo-dev-client": "~7.0.0",
                        },
                        "devDependencies": {
                            "jest-expo": "~55.0.0",
                            "@testing-library/react-native": "14.0.0",
                            "agent-device": "1.0.0",
                        },
                        "scripts": {"test:e2e": "maestro test .maestro"},
                    }
                ),
                encoding="utf-8",
            )
            (root / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\n", encoding="utf-8")
            (root / "app.config.ts").write_text("throw new Error('must not execute');\n", encoding="utf-8")
            (root / "eas.json").write_text("{}\n", encoding="utf-8")
            (root / ".maestro").mkdir()
            (root / ".maestro/login.yaml").write_text("appId: example\n---\n- launchApp\n", encoding="utf-8")
            (root / ".env").write_text("SECRET=do-not-read\n", encoding="utf-8")

            result = MODULE.inspect(root)

            self.assertEqual(result["implementation_model"], "react-native-expo")
            self.assertEqual(result["javascript"]["package_manager"], "pnpm")
            self.assertTrue(result["react_native"]["detected"])
            self.assertTrue(result["expo"]["detected"])
            self.assertEqual(result["react_native"]["native_project_model"], "expo-cng")
            self.assertEqual(result["expo"]["runtime_path"], "development-build")
            self.assertTrue(result["testing"]["react_native_testing_library"])
            self.assertIn(".maestro/login.yaml", result["testing"]["maestro_paths"])
            self.assertTrue(result["runtime_harness"]["agent_device_detected"])
            self.assertIn(".env", result["secret_like_paths"])

    def test_preserves_flutter_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pubspec.yaml").write_text("dependencies:\n  flutter:\n    sdk: flutter\n", encoding="utf-8")
            result = MODULE.inspect(root)
            self.assertEqual(result["implementation_model"], "flutter")
            self.assertTrue(result["flutter"]["detected"])


if __name__ == "__main__":
    unittest.main()

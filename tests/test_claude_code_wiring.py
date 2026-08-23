from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.generate_route_lockfile import build_lockfile
from scripts.resolve_model_route import load_model_routing, resolve_route
from scripts.sync_claude_skills import expected_link_target, sync_state

REPO_ROOT = Path(__file__).resolve().parent.parent


class SyncClaudeSkillsTests(unittest.TestCase):
    def test_repo_mirror_is_in_sync(self) -> None:
        missing, wrong, orphaned = sync_state(REPO_ROOT)
        self.assertEqual((missing, wrong, orphaned), ([], [], []))

    def test_detects_missing_and_orphaned_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / ".agents" / "skills" / "sample-skill"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("---\nname: sample-skill\n---\nbody")
            target = root / ".claude" / "skills"
            target.mkdir(parents=True)
            (target / "stale-skill").symlink_to(expected_link_target("stale-skill"))
            missing, wrong, orphaned = sync_state(root)
            self.assertEqual(missing, ["sample-skill"])
            self.assertEqual(wrong, [])
            self.assertEqual(orphaned, ["stale-skill"])


class RouteLockfileTests(unittest.TestCase):
    def test_lockfile_matches_regeneration(self) -> None:
        lock_path = REPO_ROOT / ".agents" / "model-routing" / "route-lockfile.json"
        current = json.loads(lock_path.read_text(encoding="utf-8"))
        expected = build_lockfile(REPO_ROOT)
        self.assertEqual(current, expected)
        self.assertEqual(current["harness"], "claude-code")

    def test_every_task_class_has_profile_detail_and_harness(self) -> None:
        lockfile = build_lockfile(REPO_ROOT)
        self.assertGreaterEqual(len(lockfile["routes"]), 5)
        for name, route in lockfile["routes"].items():
            self.assertEqual(route.get("harness"), "claude-code", name)
            self.assertEqual(route.get("catalog_harness"), "claude-code", name)
            self.assertTrue(route.get("capability_profile"), name)
            self.assertIn(route.get("prompt_detail"), {"compact", "normal", "strict"}, name)

    def test_claude_catalog_is_not_selectable_from_codex(self) -> None:
        routing = load_model_routing(REPO_ROOT)
        catalog_path = REPO_ROOT / ".agents" / "model-routing" / "model-catalog.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        result = resolve_route(
            "codebase_exploration",
            routing,
            catalog,
            harness="codex",
        )
        self.assertFalse(result["selected"])
        self.assertIsNone(result["selected_model"])
        self.assertIn(
            "catalog_harness_mismatch:claude-code:codex",
            result["fallback_reasons"],
        )


if __name__ == "__main__":
    unittest.main()

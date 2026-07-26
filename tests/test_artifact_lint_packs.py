"""Tests for scripts/artifact_checks_packs.py: at least one positive and one
negative case per check (required_files, json_parse, forbid_fill_sentinel,
forbid_symlinks, token_refs_in, preview_addon, catalog_cross_check,
subset_schema). Fixture style mirrors tests/test_context_budget.py (real
temp dirs via tempfile.TemporaryDirectory, no mocking). Imports the module
directly (dual-path pattern, see scripts/skill_inventory_checks.py) — never
through W-A's lint_artifacts CLI."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from scripts.artifact_checks_packs import run_checks
except ImportError:  # pragma: no cover - direct execution without repo root on sys.path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from scripts.artifact_checks_packs import run_checks


TOKEN_REFS_RULE = {
    "required_prefix": "tonemana/catalog/tokens/",
    "suffixes": {"json": ".tokens.json", "css": ".tokens.css"},
}
REGISTRY = {"token_refs_rule": TOKEN_REFS_RULE}

SCHEMA = {
    "required": ["feature", "status", "budget_results"],
    "properties": {
        "budget_results": {
            "items": {"properties": {"result": {"enum": ["pass", "fail", "unknown"]}}}
        }
    },
}


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, obj) -> None:
    _write(path, json.dumps(obj))


class RequiredFilesTests(unittest.TestCase):
    def test_all_present_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "uiux" / "p1"
            _write(pack / "a.yaml", "x: 1\n")
            findings = run_checks(root, pack, {"required_files": ["a.yaml"]}, {})
        self.assertEqual(findings, [])

    def test_missing_file_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "uiux" / "p1"
            pack.mkdir(parents=True)
            findings = run_checks(root, pack, {"required_files": ["a.yaml"]}, {})
        self.assertEqual(findings, ["missing-file:a.yaml"])


class JsonParseTests(unittest.TestCase):
    def test_valid_json_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "uiux" / "p1"
            _write_json(pack / "spec.json", {"a": 1})
            findings = run_checks(root, pack, {"json_parse": ["spec.json"]}, {})
        self.assertEqual(findings, [])

    def test_invalid_json_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "uiux" / "p1"
            _write(pack / "spec.json", "{not json")
            findings = run_checks(root, pack, {"json_parse": ["spec.json"]}, {})
        self.assertEqual(findings, ["json-parse:spec.json"])

    def test_absent_listed_file_is_not_a_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "uiux" / "p1"
            pack.mkdir(parents=True)
            findings = run_checks(root, pack, {"json_parse": ["spec.json"]}, {})
        self.assertEqual(findings, [])


class FillSentinelTests(unittest.TestCase):
    def test_clean_tree_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "uiux" / "p1"
            _write(pack / "a.yaml", "x: 1\n")
            findings = run_checks(root, pack, {"forbid_fill_sentinel": True}, {})
        self.assertEqual(findings, [])

    def test_fill_sentinel_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "uiux" / "p1"
            _write(pack / "a.yaml", "x: <fill>\n")
            findings = run_checks(root, pack, {"forbid_fill_sentinel": True}, {})
        self.assertEqual(findings, ["fill-sentinel:a.yaml"])


class SymlinkTests(unittest.TestCase):
    def test_clean_tree_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "uiux" / "p1"
            _write(pack / "a.yaml", "x: 1\n")
            findings = run_checks(root, pack, {"forbid_symlinks": True}, {})
        self.assertEqual(findings, [])

    def test_symlink_to_file_inside_pack_still_fires(self) -> None:
        # Forbid is absolute: even a symlink whose target is inside the pack
        # (not escaping it) must fire.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "uiux" / "p1"
            _write(pack / "real.yaml", "x: 1\n")
            os.symlink(pack / "real.yaml", pack / "link.yaml")
            findings = run_checks(root, pack, {"forbid_symlinks": True}, {})
        self.assertEqual(findings, ["symlink-in-pack:link.yaml"])

    def test_pack_root_itself_a_symlink_fires(self) -> None:
        # F4: os.walk follows the top-level symlink and never reports it.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real = root / "elsewhere" / "realpack"
            _write(real / "a.yaml", "x: 1\n")
            (root / "uiux").mkdir()
            pack = root / "uiux" / "p1"
            os.symlink(real, pack)
            findings = run_checks(root, pack, {"forbid_symlinks": True}, {})
        self.assertIn("symlink-in-pack:.", findings)


class TokenRefsTests(unittest.TestCase):
    SPEC = {"token_refs_in": "spec.json"}

    def _spec_json(self, root: Path, pack: Path, token_refs: dict) -> None:
        _write_json(
            pack / "spec.json",
            {"meta": {"tone_and_manner": {"token_refs": token_refs}}},
        )

    def test_block_absent_is_not_a_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "uiux" / "p1"
            _write_json(pack / "spec.json", {"meta": {}})
            findings = run_checks(root, pack, self.SPEC, REGISTRY)
        self.assertEqual(findings, [])

    def test_valid_refs_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "uiux" / "p1"
            _write(root / "tonemana/catalog/tokens/warm.tokens.json", "{}")
            _write(root / "tonemana/catalog/tokens/warm.tokens.css", ":root{}")
            self._spec_json(
                root,
                pack,
                {
                    "json": "tonemana/catalog/tokens/warm.tokens.json",
                    "css": "tonemana/catalog/tokens/warm.tokens.css",
                },
            )
            findings = run_checks(root, pack, self.SPEC, REGISTRY)
        self.assertEqual(findings, [])

    def test_list_shaped_block_is_a_finding(self) -> None:
        # F5: a malformed block must fail, not silently skip validation.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "uiux" / "p1"
            _write_json(
                pack / "spec.json",
                {"meta": {"tone_and_manner": {"token_refs": ["../../etc/passwd"]}}},
            )
            findings = run_checks(root, pack, self.SPEC, REGISTRY)
        self.assertEqual(findings, ["token-refs:bad-shape"])

    def test_unknown_kind_key_is_a_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "uiux" / "p1"
            self._spec_json(root, pack, {"Json": "/etc/passwd"})
            findings = run_checks(root, pack, self.SPEC, REGISTRY)
        self.assertEqual(findings, ["token-refs:unknown-kind:Json"])

    def test_non_string_and_empty_values_are_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "uiux" / "p1"
            self._spec_json(root, pack, {"json": {"a": 1}, "css": ""})
            findings = run_checks(root, pack, self.SPEC, REGISTRY)
        self.assertEqual(
            sorted(findings),
            ["token-refs:bad-type:css", "token-refs:bad-type:json"],
        )

    def test_traversal_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "uiux" / "p1"
            ref = "tonemana/catalog/tokens/../../../etc/passwd.tokens.json"
            self._spec_json(root, pack, {"json": ref})
            findings = run_checks(root, pack, self.SPEC, REGISTRY)
        self.assertIn(f"token-refs:traversal:{ref}", findings)

    def test_absolute_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "uiux" / "p1"
            ref = "/etc/tonemana/catalog/tokens/warm.tokens.json"
            self._spec_json(root, pack, {"json": ref})
            findings = run_checks(root, pack, self.SPEC, REGISTRY)
        self.assertIn(f"token-refs:absolute:{ref}", findings)

    def test_prefix_mismatch_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "uiux" / "p1"
            ref = "other/place/warm.tokens.json"
            _write(root / ref, "{}")
            self._spec_json(root, pack, {"json": ref})
            findings = run_checks(root, pack, self.SPEC, REGISTRY)
        self.assertIn(f"token-refs:prefix:{ref}", findings)

    def test_suffix_mismatch_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "uiux" / "p1"
            ref = "tonemana/catalog/tokens/warm.txt"
            _write(root / ref, "{}")
            self._spec_json(root, pack, {"json": ref})
            findings = run_checks(root, pack, self.SPEC, REGISTRY)
        self.assertIn(f"token-refs:suffix:{ref}", findings)

    def test_missing_target_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "uiux" / "p1"
            ref = "tonemana/catalog/tokens/ghost.tokens.json"
            self._spec_json(root, pack, {"json": ref})
            findings = run_checks(root, pack, self.SPEC, REGISTRY)
        self.assertIn(f"token-refs:missing:{ref}", findings)


class PreviewAddonTests(unittest.TestCase):
    SPEC = {
        "preview_addon": {
            "trigger_file": "previews/flow-map.html",
            "required_files": ["previews/flow-map.css"],
            "trigger_file_must_contain": "window.UIUX_SPEC",
            "forbid_remote_script_src": True,
        }
    }

    def test_trigger_absent_is_not_checked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "uiux" / "p1"
            pack.mkdir(parents=True)
            findings = run_checks(root, pack, self.SPEC, {})
        self.assertEqual(findings, [])

    def test_triggered_and_valid_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "uiux" / "p1"
            _write(pack / "previews/flow-map.html", "<script>window.UIUX_SPEC = {}</script>")
            _write(pack / "previews/flow-map.css", "body{}")
            findings = run_checks(root, pack, self.SPEC, {})
        self.assertEqual(findings, [])

    def test_triggered_missing_marker_and_remote_script_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "uiux" / "p1"
            _write(
                pack / "previews/flow-map.html",
                '<script src="http://evil.example/x.js"></script>',
            )
            findings = run_checks(root, pack, self.SPEC, {})
        self.assertIn("preview-missing:previews/flow-map.css", findings)
        self.assertIn("preview:no-inline-spec", findings)
        self.assertIn("preview:remote-script", findings)


class CatalogCrossCheckTests(unittest.TestCase):
    SPEC = {
        "catalog_cross_check": {
            "id_pattern": r"^\s*-\s+id:\s+([a-z0-9-]+)\s*$",
            "per_id_files": [
                "patterns/{id}.yaml",
                "tokens/{id}.tokens.json",
                "tokens/{id}.tokens.css",
            ],
        }
    }

    def test_all_ids_have_files_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "tonemana" / "catalog"
            _write(pack / "catalog_index.yaml", "patterns:\n  - id: warm\n")
            _write(pack / "patterns/warm.yaml", "x: 1\n")
            _write(pack / "tokens/warm.tokens.json", "{}")
            _write(pack / "tokens/warm.tokens.css", ":root{}")
            findings = run_checks(root, pack, self.SPEC, {})
        self.assertEqual(findings, [])

    def test_missing_per_id_file_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "tonemana" / "catalog"
            _write(pack / "catalog_index.yaml", "patterns:\n  - id: warm\n")
            _write(pack / "patterns/warm.yaml", "x: 1\n")
            _write(pack / "tokens/warm.tokens.json", "{}")
            # tokens/warm.tokens.css intentionally left missing
            findings = run_checks(root, pack, self.SPEC, {})
        self.assertEqual(findings, ["catalog-missing:tokens/warm.tokens.css"])

    def test_zero_ids_flagged_as_catalog_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "tonemana" / "catalog"
            _write(pack / "catalog_index.yaml", "no ids in here\n")
            findings = run_checks(root, pack, self.SPEC, {})
        self.assertEqual(findings, ["catalog-empty"])


class SubsetSchemaTests(unittest.TestCase):
    SPEC = {"subset_schema": "schema.json"}

    def test_valid_instance_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_json(root / "schema.json", SCHEMA)
            instance = root / "reports" / "resource" / "r1.json"
            _write_json(
                instance,
                {"feature": "x", "status": "pass", "budget_results": [{"result": "pass"}]},
            )
            findings = run_checks(root, instance, self.SPEC, {})
        self.assertEqual(findings, [])

    def test_missing_required_key_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_json(root / "schema.json", SCHEMA)
            instance = root / "reports" / "resource" / "r1.json"
            _write_json(instance, {"feature": "x", "budget_results": []})
            findings = run_checks(root, instance, self.SPEC, {})
        self.assertIn("subset-schema:missing-key:status", findings)

    def test_bad_enum_result_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_json(root / "schema.json", SCHEMA)
            instance = root / "reports" / "resource" / "r1.json"
            _write_json(
                instance,
                {"feature": "x", "status": "pass", "budget_results": [{"result": "nope"}]},
            )
            findings = run_checks(root, instance, self.SPEC, {})
        self.assertIn("subset-schema:bad-result:nope", findings)

    def test_unparseable_instance_flagged_as_json_parse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_json(root / "schema.json", SCHEMA)
            instance = root / "reports" / "resource" / "r1.json"
            _write(instance, "{not json")
            findings = run_checks(root, instance, self.SPEC, {})
        self.assertEqual(findings, ["json-parse:r1.json"])


if __name__ == "__main__":
    unittest.main()

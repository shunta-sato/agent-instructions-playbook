from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts import artifact_checks_docs, lint_artifacts


def _capture(fn, *args) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(*args)
    return rc, buf.getvalue()


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_registry(root: Path, artifacts: dict, schema_version: object = 1) -> None:
    registry = {"schema_version": schema_version, "artifacts": artifacts}
    _write(root / ".agents" / "artifact-registry.json", json.dumps(registry))


EXACT_KIND = {
    "test-doc": {
        "checker": "docs",
        "detect_glob": "reports/test-docs/*.md",
        "heading_mode": "exact",
        "required_headings": ["Alpha", "Beta", "Gamma"],
    }
}

KEYWORD_KIND = {
    "test-plan": {
        "checker": "docs",
        "detect_glob": "plans/*.md",
        "exclude": ["plans/_template.md"],
        "heading_mode": "keyword-sections",
        "design_record_title_marker": "design record",
        "required_section_keywords": [["purpose", "big picture"], ["scope"], ["handoff"]],
        "design_record_required_section_keywords": [["handoff"]],
    }
}


class ExactHeadingUnitTests(unittest.TestCase):
    def test_all_headings_present_passes(self) -> None:
        lines = ["## Alpha", "text", "## Beta", "text", "### Gamma", "text"]
        self.assertEqual(
            artifact_checks_docs.check_exact_headings(lines, ["Alpha", "Beta", "Gamma"]), []
        )

    def test_missing_heading_reported(self) -> None:
        lines = ["## Alpha", "text", "## Beta", "text"]
        findings = artifact_checks_docs.check_exact_headings(lines, ["Alpha", "Beta", "Gamma"])
        self.assertEqual(findings, ["missing-heading:Gamma"])


class KeywordSectionUnitTests(unittest.TestCase):
    SPEC = KEYWORD_KIND["test-plan"]

    def test_all_groups_satisfied_passes(self) -> None:
        lines = ["# A Plan", "## Purpose", "## Scope", "## Handoff"]
        self.assertEqual(artifact_checks_docs.check_keyword_sections(lines, self.SPEC), [])

    def test_missing_group_reported(self) -> None:
        lines = ["# A Plan", "## Purpose"]
        findings = artifact_checks_docs.check_keyword_sections(lines, self.SPEC)
        self.assertEqual(findings, ["missing-section:scope", "missing-section:handoff"])

    def test_design_record_marker_selects_lighter_contract(self) -> None:
        lines = ["# Something — design record", "## Handoff", "state and next steps"]
        self.assertEqual(artifact_checks_docs.check_keyword_sections(lines, self.SPEC), [])

    def test_design_record_empty_required_section_fires(self) -> None:
        # F2: for the design-record contract, heading presence alone is not
        # enough — the section needs body content.
        lines = ["# Something — design record", "## Handoff"]
        findings = artifact_checks_docs.check_keyword_sections(lines, self.SPEC)
        self.assertEqual(findings, ["empty-section:handoff"])

    def test_full_contract_does_not_require_body_content(self) -> None:
        lines = ["# A Plan", "## Purpose", "## Scope", "## Handoff"]
        self.assertEqual(artifact_checks_docs.check_keyword_sections(lines, self.SPEC), [])

    def test_heading_inside_fenced_block_does_not_satisfy(self) -> None:
        # F1: fences are blanked before matching in both modes.
        with tempfile.TemporaryDirectory() as td:
            doc = Path(td) / "doc.md"
            doc.write_text(
                "# A Plan\n```text\n## Purpose\n## Scope\n## Handoff\n```\n",
                encoding="utf-8",
            )
            lines = artifact_checks_docs._read_lines(doc)
        findings = artifact_checks_docs.check_keyword_sections(lines, self.SPEC)
        self.assertEqual(
            findings,
            ["missing-section:purpose", "missing-section:scope", "missing-section:handoff"],
        )

    def test_same_content_without_marker_uses_full_contract(self) -> None:
        # Same body as the design-record case above, minus the H1 marker:
        # the full (heavier) required set applies, so purpose/scope now fire.
        lines = ["# Something", "## Handoff"]
        findings = artifact_checks_docs.check_keyword_sections(lines, self.SPEC)
        self.assertEqual(findings, ["missing-section:purpose", "missing-section:scope"])


class DiscoveryAndExcludeTests(unittest.TestCase):
    def test_exclude_honored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_registry(root, KEYWORD_KIND)
            _write(root / "plans" / "keep.md", "# Keep\n## Purpose\n## Scope\n## Handoff\n")
            _write(root / "plans" / "_template.md", "no headings at all\n")
            spec = KEYWORD_KIND["test-plan"]
            paths = lint_artifacts.discover_instances(root, "test-plan", spec)
        rels = {lint_artifacts.repo_relative(root, p) for p in paths}
        self.assertEqual(rels, {"plans/keep.md"})
        self.assertNotIn("plans/_template.md", rels)


class BaselineRatchetTests(unittest.TestCase):
    def _make_tree(self, root: Path) -> None:
        _write_registry(root, EXACT_KIND)
        _write(root / "reports" / "test-docs" / "bad.md", "## Alpha\n## Beta\n")

    def test_unbaselined_finding_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_tree(root)
            rc, output = _capture(lint_artifacts.main, ["--repo-root", str(root)])
        self.assertEqual(rc, 1)
        self.assertIn("FINDING reports/test-docs/bad.md: missing-heading:Gamma", output)

    def test_baselined_finding_passes_and_stale_is_informational(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_tree(root)
            _write(
                root / "scripts" / "artifact_lint_baseline.json",
                json.dumps(
                    {
                        "reports/test-docs/bad.md": [
                            "missing-heading:Gamma",
                            "missing-heading:Old",
                        ]
                    }
                ),
            )
            rc, output = _capture(lint_artifacts.main, ["--repo-root", str(root)])
        self.assertEqual(rc, 0)
        self.assertIn("artifact-lint: pass", output)
        self.assertIn(
            "stale-baseline: reports/test-docs/bad.md: missing-heading:Old", output
        )
        self.assertNotIn("FINDING", output)

    def test_write_baseline_writes_current_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_tree(root)
            rc, output = _capture(
                lint_artifacts.main, ["--repo-root", str(root), "--write-baseline"]
            )
            written = json.loads(
                (root / "scripts" / "artifact_lint_baseline.json").read_text()
            )
        self.assertEqual(rc, 0)
        self.assertIn("wrote 1 artifact path(s)", output)
        self.assertEqual(written, {"reports/test-docs/bad.md": ["missing-heading:Gamma"]})


class SchemaVersionTests(unittest.TestCase):
    def test_unknown_schema_version_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_registry(root, EXACT_KIND, schema_version=2)
            with self.assertRaises(SystemExit) as ctx:
                lint_artifacts.main(["--repo-root", str(root)])
        self.assertIn("schema_version", str(ctx.exception))

    def test_missing_schema_version_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = {"artifacts": EXACT_KIND}
            _write(root / ".agents" / "artifact-registry.json", json.dumps(registry))
            with self.assertRaises(SystemExit):
                lint_artifacts.main(["--repo-root", str(root)])


if __name__ == "__main__":
    unittest.main()

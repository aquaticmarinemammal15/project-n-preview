import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from stage_site import stage
from validate_site import InvalidSite, validate


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.export = self.root / "export"
        self.repo = self.root / "repo"
        self.export.mkdir()
        self.repo.mkdir()
        (self.export / "index.html").write_text('<!doctype html><title>NovusPal preview</title><script src="/project-n-preview/app.js"></script>', encoding="utf-8")
        (self.export / "app.js").write_text('console.log("Preview");', encoding="utf-8")

    def test_stage_preserves_source_and_records_integrity(self):
        before = (self.export / "index.html").read_bytes()
        site = stage(self.export, "approved-demo-1", spa=True, repo=self.repo)
        validate(site)
        self.assertEqual(before, (self.export / "index.html").read_bytes())
        self.assertFalse((self.export / "404.html").exists())
        self.assertEqual(before, (site / "404.html").read_bytes())
        self.assertEqual("approved-demo-1", json.loads((site / "release-manifest.json").read_text())["source_version"])

    def test_restage_backs_up_previous_artifact(self):
        stage(self.export, "v1", repo=self.repo)
        (self.export / "app.js").write_text("// v2", encoding="utf-8")
        validate(stage(self.export, "v2", repo=self.repo))
        backups = list((self.repo / ".deployment-backups").iterdir())
        self.assertEqual(1, len(backups))
        self.assertEqual('console.log("Preview");', (backups[0] / "app.js").read_text())

    def test_invalid_export_does_not_replace_existing_site(self):
        site = stage(self.export, "v1", repo=self.repo)
        before = (site / "release-manifest.json").read_bytes()
        (self.export / "app.js").unlink()
        with self.assertRaises(InvalidSite):
            stage(self.export, "bad", repo=self.repo)
        self.assertEqual(before, (site / "release-manifest.json").read_bytes())

    def test_modified_artifact_is_rejected(self):
        site = stage(self.export, "v1", repo=self.repo)
        (site / "app.js").write_text("// changed", encoding="utf-8")
        with self.assertRaisesRegex(InvalidSite, "differs"):
            validate(site)

    def test_missing_entrypoint(self):
        (self.export / "index.html").unlink()
        with self.assertRaisesRegex(InvalidSite, "index.html"):
            validate(self.export, False)

    def test_missing_asset(self):
        (self.export / "app.js").unlink()
        with self.assertRaisesRegex(InvalidSite, "Missing local resource"):
            validate(self.export, False)

    def test_domain_root_assets_are_rejected(self):
        (self.export / "index.html").write_text('<title>Preview</title><script src="/app.js"></script>', encoding="utf-8")
        with self.assertRaisesRegex(InvalidSite, "outside"):
            validate(self.export, False)

    def test_css_assets_are_checked(self):
        (self.export / "style.css").write_text('body { background: url("missing.png"); }', encoding="utf-8")
        with self.assertRaisesRegex(InvalidSite, "Missing local resource"):
            validate(self.export, False)

    def test_source_maps_and_environment_files_are_rejected(self):
        for name in ("bundle.js.map", ".env", "src.tsx"):
            with self.subTest(name=name):
                bad = self.export / name
                bad.write_text("not for publishing", encoding="utf-8")
                with self.assertRaises(InvalidSite):
                    validate(self.export, False)
                bad.unlink()

    def test_embedded_credentials_are_rejected_without_echoing_value(self):
        (self.export / "app.js").write_text("ghp_" + "a" * 36, encoding="utf-8")
        with self.assertRaisesRegex(InvalidSite, "Possible embedded credential"):
            validate(self.export, False)

    def test_traversal_is_rejected(self):
        (self.export / "index.html").write_text('<title>Preview</title><script src="../outside.js"></script>', encoding="utf-8")
        with self.assertRaisesRegex(InvalidSite, "escapes"):
            validate(self.export, False)

    def test_local_development_resource_is_rejected(self):
        (self.export / "index.html").write_text('<title>Preview</title><script src="http://localhost:8081/app.js"></script>', encoding="utf-8")
        with self.assertRaisesRegex(InvalidSite, "Local development"):
            validate(self.export, False)

    def test_unstaged_export_cannot_deploy(self):
        with self.assertRaisesRegex(InvalidSite, "nojekyll"):
            validate(self.export)

    def test_source_and_destination_cannot_overlap(self):
        with self.assertRaisesRegex(InvalidSite, "separate"):
            stage(self.repo, "v1", repo=self.repo)


if __name__ == "__main__":
    unittest.main()

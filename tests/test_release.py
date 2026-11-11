"""Offline package checks. These are not model-behavior evaluations."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("workflow_release", ROOT / "scripts/release.py")
RELEASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RELEASE)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name) / "kit"
        self.root.mkdir()
        for name in RELEASE.PUBLIC_FILES:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}\n" if path.suffix == ".json" else "public text\n")
        (self.root / "VERSION").write_text("0.1.1-alpha\n")
        (self.root / "docs").mkdir()

    def test_archive_uses_allowlist_and_manifest_hashes(self):
        private = self.root / "research/evidence"
        private.mkdir()
        (private / "local-only.txt").write_text("not for redistribution")
        (self.root / "unexpected-local.txt").write_text("not for redistribution")
        output = Path(self.workspace.name) / "release.zip"
        manifest = RELEASE.build(self.root, output)
        with zipfile.ZipFile(output) as archive:
            names = archive.namelist()
            self.assertFalse(any("evidence" in name or "unexpected-local" in name for name in names))
            saved = json.loads(archive.read("agent-workflow-kit/RELEASE-MANIFEST.json"))
            self.assertEqual(manifest, saved)
            for path, digest in saved["files"].items():
                self.assertEqual(hashlib.sha256(archive.read("agent-workflow-kit/" + path)).hexdigest(), digest)

    def test_personal_paths_and_tokens_are_rejected(self):
        examples = [
            "sample-person" + "@" + "example.invalid",
            "/".join(("", "home", "example-user", "private-task")),
            "\\".join(("C:", "Users", "example-user", "private-task")),
            "s" + "k-" + "x" * 24,
            "gh" + "p_" + "x" * 32,
            "-----BEGIN " + "PRIVATE KEY-----",
        ]
        for text in examples:
            with self.subTest(kind=examples.index(text)):
                (self.root / "docs/example.md").write_text(text)
                _, errors = RELEASE.check(self.root)
                self.assertTrue(errors)
                with self.assertRaises(ValueError):
                    RELEASE.build(self.root, Path(self.workspace.name) / "blocked.zip")

    def test_custom_private_terms_are_not_echoed(self):
        term = "sensitive" + "-fixture-name"
        (self.root / "docs/example.md").write_text(term)
        _, errors = RELEASE.check(self.root, [term])
        self.assertTrue(errors)
        self.assertNotIn(term, " ".join(errors))

    def test_public_symlinks_are_rejected(self):
        outside = Path(self.workspace.name) / "outside.txt"
        outside.write_text("local source")
        try:
            (self.root / "docs/link.txt").symlink_to(outside)
        except OSError:
            self.skipTest("Host does not permit test symlinks")
        with self.assertRaises(ValueError):
            RELEASE.check(self.root)

    def test_private_filename_is_rejected_without_echo(self):
        term = "private" + "-fixture-label"
        (self.root / "docs" / (term + ".md")).write_text("public content")
        _, errors = RELEASE.check(self.root, [term])
        self.assertTrue(errors)
        self.assertNotIn(term, " ".join(errors))
        with self.assertRaises(ValueError):
            RELEASE.build(self.root, Path(self.workspace.name) / "blocked.zip", [term])

    def test_missing_and_excluded_markdown_targets_fail(self):
        for target in ["missing.md", "../research/evidence/raw.txt"]:
            with self.subTest(target=target):
                (self.root / "docs/example.md").write_text("[source](" + target + ")")
                _, errors = RELEASE.check(self.root)
                self.assertTrue(errors)

    def test_invalid_json_and_credential_file_fail(self):
        (self.root / "docs/bad.json").write_text("not JSON")
        (self.root / "docs/.env").write_text("example=value")
        _, errors = RELEASE.check(self.root)
        self.assertTrue(any("invalid JSON" in error for error in errors))
        self.assertTrue(any("credential file" in error for error in errors))

    def test_missing_required_file_fails(self):
        (self.root / "LICENSE").unlink()
        with self.assertRaises(ValueError):
            RELEASE.check(self.root)

    def test_in_tree_output_is_rejected(self):
        with self.assertRaises(ValueError):
            RELEASE.build(self.root, self.root / "release.zip")

    def test_same_source_build_is_byte_reproducible(self):
        first = Path(self.workspace.name) / "first.zip"
        second = Path(self.workspace.name) / "second.zip"
        RELEASE.build(self.root, first)
        RELEASE.build(self.root, second)
        self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_project_public_files_pass(self):
        contents, errors = RELEASE.check(ROOT)
        self.assertEqual(errors, [])
        self.assertIn("skills/agent-workflow/SKILL.md", contents)


class ArtifactTests(unittest.TestCase):
    def test_installed_skill_references_stay_inside_the_skill(self):
        skill = ROOT / "skills/agent-workflow"
        for path in skill.rglob("*.md"):
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text()):
                if "://" in target or target.startswith("#"):
                    continue
                destination = (path.parent / target.split("#")[0]).resolve()
                self.assertTrue(destination.is_relative_to(skill), (path.name, target))
                self.assertTrue(destination.is_file(), (path.name, target))

    def test_templates_do_not_claim_authorization_or_scheduler(self):
        assets = ROOT / "skills/agent-workflow/assets"
        workflow = json.loads((assets / "workflow.json").read_text())
        state = json.loads((assets / "state.json").read_text())
        self.assertEqual(workflow["task_id"], state["task_id"])
        self.assertEqual(workflow["authorization"]["allowed_actions"], [])
        self.assertIsNone(workflow["authorization"]["source"])
        self.assertFalse(workflow["scheduler"]["configured"])
        self.assertIsNone(state["active_attempt"])

    def test_eval_inputs_do_not_contain_expected_answers(self):
        prompts = json.loads((ROOT / "evals/prompts.json").read_text())["prompts"]
        rubric = json.loads((ROOT / "evals/rubric.json").read_text())["criteria"]
        self.assertEqual(len({p["id"] for p in prompts}), len(prompts))
        for prompt in prompts:
            self.assertNotIn("expected_behavior", prompt)
            self.assertNotIn("assertions", prompt)
            self.assertIn(prompt["id"], rubric)
            if prompt.get("fixture"):
                self.assertTrue((ROOT / "evals" / prompt["fixture"]).is_file())


if __name__ == "__main__":
    unittest.main()

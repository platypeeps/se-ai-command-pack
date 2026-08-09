"""Regression tests for .github/scripts/check-trellis-provenance.py.

The checker gates coverage and integrity of tracked platform files that have
no upstream receipt, plus the .claude gitignore-durability assertion. These
tests run it against disposable fixture git repositories — never the live
tree — and lock the wiring text in the Makefile, check.json, and tests.yml.
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / ".github" / "scripts" / "check-trellis-provenance.py"

_spec = importlib.util.spec_from_file_location("check_trellis_provenance", SCRIPT_PATH)
assert _spec is not None and _spec.loader is not None
checker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(checker)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class FixtureRepo:
    """Minimal git repo with one covered file per platform surface."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.agents_file = ".agents/skills/demo/SKILL.md"
        self.claude_file = ".claude/commands/sd/demo.md"
        self.manifest_path = ".github/trellis-provenance.json"

    def git(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", "-C", str(self.root), *args],
            capture_output=True,
            text=True,
            check=True,
        )

    def write(self, rel: str, content: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def build(self) -> None:
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Fixture")
        self.write(self.agents_file, "agents content\n")
        self.write(self.claude_file, "claude content\n")
        self.write(".gitignore", "# nothing ignored\n")
        self.write(".sd-ai-command-pack/provenance.json", json.dumps({"files": {}}))
        self.write_manifest()
        self.git("add", "-A")
        self.git("commit", "--quiet", "-m", "fixture")

    def manifest_files(self) -> dict[str, str]:
        return {
            rel: sha256((self.root / rel).read_bytes())
            for rel in (self.agents_file, self.claude_file, ".gitignore")
        }

    def write_manifest(self, **overrides: object) -> None:
        manifest: dict = {
            "__version": 1,
            "files": self.manifest_files(),
            "repoOwn": [self.manifest_path],
            "templateReceipted": [],
        }
        manifest.update(overrides)
        self.write(self.manifest_path, json.dumps(manifest, indent=2) + "\n")

    def run_checker(self, *args: str) -> tuple[int, str]:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stdout):
            status = checker.main(["--repo", str(self.root), *args])
        return status, stdout.getvalue()


class ProvenanceCheckerTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = FixtureRepo(Path(self._tmp.name))
        self.repo.build()

    def manifest_bytes(self) -> bytes:
        return (self.repo.root / self.repo.manifest_path).read_bytes()

    def test_clean_fixture_passes(self) -> None:
        status, output = self.repo.run_checker()
        self.assertEqual(status, 0, output)
        self.assertIn("trellis-provenance check: ok", output)

    # -- strict manifest parsing ------------------------------------------

    def assert_malformed(self, output_fragment: str, **overrides: object) -> None:
        self.repo.write_manifest(**overrides)
        status, output = self.repo.run_checker()
        self.assertEqual(status, 2, output)
        self.assertIn(output_fragment, output)

    def test_bad_version_is_malformed(self) -> None:
        self.assert_malformed("__version", __version=2)

    def test_bad_hash_format_is_malformed(self) -> None:
        self.assert_malformed("sha256", files={self.repo.agents_file: "abc"})

    def test_overlapping_sets_are_malformed(self) -> None:
        self.assert_malformed("overlap", repoOwn=[self.repo.manifest_path, self.repo.agents_file])

    def test_noncanonical_path_is_malformed(self) -> None:
        self.assert_malformed("non-canonical", repoOwn=["../escape.md"])

    def test_duplicate_array_entry_is_malformed(self) -> None:
        self.assert_malformed("duplicate", repoOwn=[self.repo.manifest_path, self.repo.manifest_path])

    def test_unexpected_key_is_malformed(self) -> None:
        self.assert_malformed("exactly the keys", extra=True)

    def test_duplicate_json_member_is_malformed(self) -> None:
        raw = (self.repo.root / self.repo.manifest_path).read_text(encoding="utf-8")
        raw = raw.replace('"repoOwn"', '"templateReceipted"', 1)
        self.repo.write(self.repo.manifest_path, raw)
        status, output = self.repo.run_checker()
        self.assertEqual(status, 2, output)
        self.assertIn("duplicate JSON member", output)

    # -- check-mode findings ----------------------------------------------

    def test_uncovered_new_file_fails(self) -> None:
        self.repo.write(".codex/hooks/new.py", "print()\n")
        self.repo.git("add", ".codex/hooks/new.py")
        status, output = self.repo.run_checker()
        self.assertEqual(status, 1, output)
        self.assertIn("uncovered: .codex/hooks/new.py", output)

    def test_drifted_file_fails(self) -> None:
        self.repo.write(self.repo.agents_file, "tampered\n")
        status, output = self.repo.run_checker()
        self.assertEqual(status, 1, output)
        self.assertIn(f"drifted: {self.repo.agents_file}", output)

    def test_missing_file_fails(self) -> None:
        self.repo.git("rm", "--quiet", self.repo.agents_file)
        status, output = self.repo.run_checker()
        self.assertEqual(status, 1, output)
        self.assertIn(f"missing: {self.repo.agents_file}", output)

    def test_symlink_fails_as_not_regular(self) -> None:
        target = self.repo.root / self.repo.agents_file
        target.unlink()
        target.symlink_to(self.repo.root / ".gitignore")
        status, output = self.repo.run_checker()
        self.assertEqual(status, 1, output)
        self.assertIn(f"not-regular-file: {self.repo.agents_file}", output)

    def test_wholesale_claude_ignore_fails(self) -> None:
        self.repo.write(".gitignore", ".claude/\n")
        status, output = self.repo.run_checker()
        self.assertEqual(status, 1, output)
        self.assertIn(f"ignored-tracked-path: {self.repo.claude_file}", output)
        self.assertIn("drifted: .gitignore", output)

    def test_stale_template_snapshot_fails(self) -> None:
        self.repo.write(
            ".trellis/.template-hashes.json",
            json.dumps({"__version": 2, "hashes": {self.repo.agents_file: "0" * 64}}),
        )
        status, output = self.repo.run_checker()
        self.assertEqual(status, 1, output)
        self.assertIn("template-snapshot-stale", output)

    def test_invalid_template_registry_is_environment_error(self) -> None:
        before = self.manifest_bytes()
        self.repo.write(".trellis/.template-hashes.json", json.dumps({"__version": 1}))
        status, output = self.repo.run_checker()
        self.assertEqual(status, 2, output)
        self.assertIn("not a v2 registry", output)
        self.assertEqual(self.manifest_bytes(), before)

    def test_check_ignore_fatal_status_is_error_not_pass(self) -> None:
        with self.assertRaises(checker.CheckError):
            checker.check_ignored_tracked_paths(
                self.repo.root / "no-such-subdir", [".claude/x.md"]
            )

    # -- write mode --------------------------------------------------------

    def test_write_is_byte_stable(self) -> None:
        status, output = self.repo.run_checker("--write")
        self.assertEqual(status, 0, output)
        first = self.manifest_bytes()
        status, output = self.repo.run_checker("--write")
        self.assertEqual(status, 0, output)
        self.assertEqual(self.manifest_bytes(), first)

    def test_write_refuses_unaccepted_new_path_atomically(self) -> None:
        status, _ = self.repo.run_checker("--write")
        self.assertEqual(status, 0)
        before = self.manifest_bytes()
        self.repo.write(".codex/hooks/new.py", "print()\n")
        self.repo.git("add", ".codex/hooks/new.py")
        status, output = self.repo.run_checker("--write")
        self.assertEqual(status, 1, output)
        self.assertIn("uncovered: .codex/hooks/new.py", output)
        self.assertEqual(self.manifest_bytes(), before)

    def test_write_accept_absorbs_named_path(self) -> None:
        self.repo.write(".codex/hooks/new.py", "print()\n")
        self.repo.git("add", ".codex/hooks/new.py")
        status, output = self.repo.run_checker("--write", "--accept", ".codex/hooks/new.py")
        self.assertEqual(status, 0, output)
        self.assertIn("added: .codex/hooks/new.py", output)
        manifest = json.loads(self.manifest_bytes())
        self.assertIn(".codex/hooks/new.py", manifest["files"])

    def test_write_preserves_repo_own(self) -> None:
        before = json.loads(self.manifest_bytes())["repoOwn"]
        status, _ = self.repo.run_checker("--write")
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(self.manifest_bytes())["repoOwn"], before)

    def test_accept_without_write_is_usage_error(self) -> None:
        with self.assertRaises(SystemExit):
            self.repo.run_checker("--accept", ".gitignore")


class WiringTest(unittest.TestCase):
    """The gate stays wired: Makefile, check.json, and CI all invoke it."""

    def test_makefile_check_chain_includes_provenance(self) -> None:
        makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
        self.assertIn("check-trellis-provenance.py", makefile)
        self.assertRegex(makefile, r"(?m)^check:.*\btrellis-provenance\b")

    def test_check_json_registers_provenance(self) -> None:
        data = json.loads((REPO_ROOT / ".sd-ai-command-pack" / "check.json").read_text())
        ids = [entry["id"] for entry in data["checks"]]
        self.assertIn("repo.trellis-provenance", ids)

    def test_release_payload_gate_job_invokes_checker(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
        gate_job = workflow.split("release-payload-gate:", 1)[1].split("\n  review-preflight:", 1)[0]
        self.assertIn("python .github/scripts/check-trellis-provenance.py", gate_job)


if __name__ == "__main__":
    unittest.main()

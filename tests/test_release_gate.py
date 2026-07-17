"""Release payload gate tests against synthetic git repositories."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from install_test_support import PACK_ROOT, TempDirTestCase

GATE_SCRIPT = PACK_ROOT / ".github" / "scripts" / "check-release-payload.py"
TAG_SCRIPT = PACK_ROOT / ".github" / "scripts" / "create-release-tag.py"


def git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        text=True,
        capture_output=True,
        check=False,
    )


class ReleaseGateTest(TempDirTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.repo = self.base / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-b", "main")
        git(self.repo, "config", "user.email", "test@example.com")
        git(self.repo, "config", "user.name", "Test")
        self.write_manifest("1.0.0")
        self.write_changelog("1.0.0")
        (self.repo / "templates").mkdir()
        (self.repo / "templates" / "skill.md").write_text("v1\n", encoding="utf-8")
        (self.repo / "README.md").write_text("readme\n", encoding="utf-8")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-m", "initial")

    def write_manifest(self, version: str) -> None:
        (self.repo / "manifest.json").write_text(
            json.dumps({"name": "se-ai-command-pack", "version": version}) + "\n",
            encoding="utf-8",
        )

    def write_changelog(self, version: str, date: str = "2026-07-16") -> None:
        (self.repo / "CHANGELOG.md").write_text(
            f"# Changelog\n\n## {version} - {date}\n\n- Notes.\n",
            encoding="utf-8",
        )

    def gate(self, base: str = "HEAD") -> subprocess.CompletedProcess:
        return run_script(GATE_SCRIPT, "--repo", str(self.repo), "--base", base)

    def test_clean_tree_passes(self) -> None:
        result = self.gate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("no payload change", result.stdout)

    def test_payload_change_without_bump_fails(self) -> None:
        (self.repo / "templates" / "skill.md").write_text("v2\n", encoding="utf-8")
        result = self.gate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("without a version bump", result.stderr)

    def test_untracked_payload_file_without_bump_fails(self) -> None:
        (self.repo / "templates" / "new.md").write_text("new\n", encoding="utf-8")
        result = self.gate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("without a version bump", result.stderr)

    def test_payload_change_with_bump_and_changelog_passes(self) -> None:
        (self.repo / "templates" / "skill.md").write_text("v2\n", encoding="utf-8")
        self.write_manifest("1.1.0")
        self.write_changelog("1.1.0")
        result = self.gate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1.0.0 -> 1.1.0", result.stdout)

    def test_bump_with_stale_changelog_fails(self) -> None:
        self.write_manifest("1.1.0")
        result = self.gate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("manifest version is 1.1.0", result.stderr)

    def test_bump_with_undated_heading_fails(self) -> None:
        self.write_manifest("1.1.0")
        (self.repo / "CHANGELOG.md").write_text(
            "# Changelog\n\n## 1.1.0\n\n- Notes.\n", encoding="utf-8"
        )
        result = self.gate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("YYYY-MM-DD", result.stderr)

    def test_bump_with_impossible_date_fails(self) -> None:
        self.write_manifest("1.1.0")
        self.write_changelog("1.1.0", date="2026-13-45")
        result = self.gate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("not a real date", result.stderr)

    def test_non_payload_change_passes_without_bump(self) -> None:
        (self.repo / "README.md").write_text("updated\n", encoding="utf-8")
        result = self.gate()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_committed_branch_measured_against_base(self) -> None:
        git(self.repo, "checkout", "-b", "feature")
        (self.repo / "templates" / "skill.md").write_text("v2\n", encoding="utf-8")
        git(self.repo, "commit", "-am", "payload change, no bump")
        result = self.gate(base="main")
        self.assertEqual(result.returncode, 1)
        self.assertIn("without a version bump", result.stderr)

    def test_unknown_base_fails_cleanly(self) -> None:
        result = self.gate(base="does-not-exist")
        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot resolve base revision", result.stderr)

    def test_real_pack_gate_passes(self) -> None:
        result = run_script(GATE_SCRIPT)
        self.assertEqual(result.returncode, 0, result.stderr)


class ReleaseTagTest(TempDirTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.repo = self.base / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-b", "main")
        git(self.repo, "config", "user.email", "test@example.com")
        git(self.repo, "config", "user.name", "Test")
        (self.repo / "manifest.json").write_text(
            json.dumps({"name": "se-ai-command-pack", "version": "1.0.0"}) + "\n",
            encoding="utf-8",
        )
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-m", "initial")

    def tags(self) -> set[str]:
        result = subprocess.run(
            ["git", "-C", str(self.repo), "tag"],
            check=True,
            capture_output=True,
            text=True,
        )
        return set(result.stdout.split())

    def test_creates_tag_once(self) -> None:
        result = run_script(TAG_SCRIPT, "--repo", str(self.repo))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.tags(), {"v1.0.0"})
        again = run_script(TAG_SCRIPT, "--repo", str(self.repo))
        self.assertEqual(again.returncode, 0)
        self.assertIn("already exists", again.stdout)

    def test_dry_run_creates_nothing(self) -> None:
        result = run_script(TAG_SCRIPT, "--repo", str(self.repo), "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.tags(), set())


if __name__ == "__main__":
    unittest.main()

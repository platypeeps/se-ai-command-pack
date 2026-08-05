"""Release payload gate tests against synthetic git repositories."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from install_test_support import PACK_ROOT, TempDirTestCase

GATE_SCRIPT = PACK_ROOT / ".github" / "scripts" / "check-release-payload.py"
TAG_SCRIPT = PACK_ROOT / ".github" / "scripts" / "create-release-tag.py"
WORKFLOW = PACK_ROOT / ".github" / "workflows" / "tests.yml"


def load_tag_module():
    """Import create-release-tag.py as a module so its subprocess.run is
    patchable in-process; run_script's external subprocess cannot be reached
    by patch()."""
    spec = importlib.util.spec_from_file_location("create_release_tag", TAG_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


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
        (self.repo / "generated").mkdir()
        (self.repo / "generated" / "skill.md").write_text("v1\n", encoding="utf-8")
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

    def test_generated_payload_change_without_bump_fails(self) -> None:
        (self.repo / "generated" / "skill.md").write_text("v2\n", encoding="utf-8")
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

    def rev_parse(self, ref: str) -> str:
        proc = subprocess.run(
            ["git", "-C", str(self.repo), "rev-parse", ref],
            check=True,
            capture_output=True,
            text=True,
        )
        return proc.stdout.strip()

    def test_installer_dir_change_without_bump_fails(self) -> None:
        installer = self.repo / "installer"
        installer.mkdir()
        (installer / "registry.py").write_text("x = 1\n", encoding="utf-8")
        result = self.gate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("without a version bump", result.stderr)

    def test_install_py_change_without_bump_fails(self) -> None:
        (self.repo / "install.py").write_text("print('x')\n", encoding="utf-8")
        result = self.gate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("without a version bump", result.stderr)

    def test_install_py_change_with_bump_passes(self) -> None:
        (self.repo / "install.py").write_text("print('x')\n", encoding="utf-8")
        self.write_manifest("1.1.0")
        self.write_changelog("1.1.0")
        result = self.gate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1.0.0 -> 1.1.0", result.stdout)

    def test_installer_change_with_bump_passes(self) -> None:
        installer = self.repo / "installer"
        installer.mkdir()
        (installer / "registry.py").write_text("x = 1\n", encoding="utf-8")
        self.write_manifest("1.1.0")
        self.write_changelog("1.1.0")
        result = self.gate()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_nested_install_py_is_not_gated(self) -> None:
        # `install.py` is an exact top-level match, not a prefix: a nested
        # `sub/install.py` is not shipped payload and needs no bump.
        nested = self.repo / "sub"
        nested.mkdir()
        (nested / "install.py").write_text("print('x')\n", encoding="utf-8")
        result = self.gate()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_installer_prefix_sibling_is_not_gated(self) -> None:
        # The `installer/` prefix must not match a sibling like `installerX.py`
        # (startswith on a slash-terminated prefix, not a bare name).
        (self.repo / "installerX.py").write_text("x = 1\n", encoding="utf-8")
        result = self.gate()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_no_payload_diff_passes_without_bump(self) -> None:
        # Widened surface present and committed; a non-payload edit alongside a
        # byte-identical payload tree must still pass without a bump (carve-out).
        (self.repo / "install.py").write_text("print('x')\n", encoding="utf-8")
        installer = self.repo / "installer"
        installer.mkdir()
        (installer / "registry.py").write_text("x = 1\n", encoding="utf-8")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-m", "add installer payload")
        (self.repo / "README.md").write_text("changed prose\n", encoding="utf-8")
        result = self.gate()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_base_auto_falls_back_to_head_without_origin(self) -> None:
        # No origin/main ref exists, so auto degrades to HEAD (uncommitted only).
        git(self.repo, "checkout", "-b", "feature")
        (self.repo / "templates" / "skill.md").write_text("v2\n", encoding="utf-8")
        git(self.repo, "commit", "-am", "payload change, no bump")
        committed = self.gate(base="auto")
        self.assertEqual(committed.returncode, 0, committed.stderr)
        # An uncommitted payload change is still caught under the HEAD fallback.
        (self.repo / "templates" / "skill.md").write_text("v3\n", encoding="utf-8")
        uncommitted = self.gate(base="auto")
        self.assertEqual(uncommitted.returncode, 1)
        self.assertIn("without a version bump", uncommitted.stderr)

    def test_base_auto_uses_origin_main_when_present(self) -> None:
        # Synthesize the remote-tracking ref without any network, then commit a
        # payload change on a branch: auto must measure the branch range.
        main_sha = self.rev_parse("main")
        git(self.repo, "update-ref", "refs/remotes/origin/main", main_sha)
        git(self.repo, "checkout", "-b", "feature")
        (self.repo / "templates" / "skill.md").write_text("v2\n", encoding="utf-8")
        git(self.repo, "commit", "-am", "payload change, no bump")
        result = self.gate(base="auto")
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

    def add_bare_origin(self) -> Path:
        origin = self.base / "origin.git"
        subprocess.run(
            ["git", "init", "--bare", str(origin)],
            check=True,
            capture_output=True,
            text=True,
        )
        git(self.repo, "remote", "add", "origin", str(origin))
        return origin

    def remote_tags(self, origin: Path) -> set[str]:
        result = subprocess.run(
            ["git", "-C", str(origin), "tag"],
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

    def test_push_creates_and_pushes(self) -> None:
        origin = self.add_bare_origin()
        result = run_script(TAG_SCRIPT, "--repo", str(self.repo), "--push")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.tags(), {"v1.0.0"})
        self.assertEqual(self.remote_tags(origin), {"v1.0.0"})

    def test_push_respects_remote_tag_missing_locally(self) -> None:
        # The CI situation: the release tag exists on origin, but the
        # runner's checkout has no tags. The script must not recreate it.
        origin = self.add_bare_origin()
        git(self.repo, "tag", "v1.0.0")
        git(self.repo, "push", "origin", "v1.0.0")
        git(self.repo, "tag", "-d", "v1.0.0")
        result = run_script(TAG_SCRIPT, "--repo", str(self.repo), "--push")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("already exists on origin", result.stdout)
        self.assertEqual(self.tags(), set())
        self.assertEqual(self.remote_tags(origin), {"v1.0.0"})

    def test_push_without_origin_fails_cleanly(self) -> None:
        result = run_script(TAG_SCRIPT, "--repo", str(self.repo), "--push")
        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot query origin", result.stderr)
        self.assertEqual(self.tags(), set())

    def test_git_timeout_fails_cleanly(self) -> None:
        # A hung git must map to a clean error: exit 1, no traceback. A --push
        # run reaches run_git at its first ls-remote call before any early exit.
        module = load_tag_module()
        stderr = io.StringIO()
        with patch.object(
            module.subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired(cmd="git", timeout=60),
        ), contextlib.redirect_stderr(stderr):
            code = module.main(["--repo", str(self.repo), "--push"])
        self.assertEqual(code, 1)
        captured = stderr.getvalue()
        self.assertIn("error:", captured)
        self.assertIn("timed out", captured)

    def test_git_missing_fails_cleanly(self) -> None:
        module = load_tag_module()
        stderr = io.StringIO()
        with patch.object(
            module.subprocess, "run", side_effect=FileNotFoundError()
        ), contextlib.redirect_stderr(stderr):
            code = module.main(["--repo", str(self.repo), "--push"])
        self.assertEqual(code, 1)
        captured = stderr.getvalue()
        self.assertIn("error:", captured)
        self.assertIn("git not found", captured)


class WorkflowHygieneTest(unittest.TestCase):
    """Lock the CI-workflow wiring so a future edit that drops any of the
    hygiene guarantees (A-038 cache, A-039 concurrency, A-037 push-lane gate)
    fails a test. pyyaml is not a dependency, so assert on the file text."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_pip_cache_on_three_setup_python_steps(self) -> None:
        self.assertEqual(self.text.count("cache: pip"), 3)

    def test_concurrency_with_pr_only_cancellation(self) -> None:
        self.assertIn("concurrency:", self.text)
        self.assertIn(
            "cancel-in-progress: ${{ github.event_name == 'pull_request' }}",
            self.text,
        )

    def test_auto_tag_depends_on_release_gate(self) -> None:
        self.assertIn("needs: [unittest, lint, release-payload-gate]", self.text)

    def test_release_gate_runs_on_push_to_main(self) -> None:
        self.assertIn(
            "github.event_name == 'push' && github.ref == 'refs/heads/main'",
            self.text,
        )


if __name__ == "__main__":
    unittest.main()

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

from install_test_support import (
    PACK_ROOT,
    TempDirTestCase,
    git_env,
)

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
        env=git_env(),
    )


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        text=True,
        capture_output=True,
        check=False,
        env=git_env(),
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

    def gate(
        self, base: str = "HEAD", step_base: str | None = None
    ) -> subprocess.CompletedProcess:
        extra = () if step_base is None else ("--step-base", step_base)
        return run_script(
            GATE_SCRIPT, "--repo", str(self.repo), "--base", base, *extra
        )

    def release(self, version: str, *older: tuple[str, str]) -> None:
        """Commit one release: payload edit, manifest bump, changelog heading."""
        (self.repo / "templates" / "skill.md").write_text(
            f"{version}\n", encoding="utf-8"
        )
        self.write_manifest(version)
        self.write_changelog_entries((version, "2026-07-18"), *older)
        git(self.repo, "commit", "-am", f"release {version}")

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
            env=git_env(),
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

    def write_changelog_entries(self, *entries: tuple[str, str]) -> None:
        body = "".join(
            f"## {version} - {date}\n\n- Notes.\n\n" for version, date in entries
        )
        (self.repo / "CHANGELOG.md").write_text(
            f"# Changelog\n\n{body}", encoding="utf-8"
        )

    def test_two_version_headings_in_one_branch_fails(self) -> None:
        # A-041: the 0.53.0 shape. Bumping twice on one branch means the
        # intermediate version is never a merge-base state, so the auto-tag
        # workflow never sees it and no v<version> tag is ever created.
        git(self.repo, "checkout", "-b", "feature")
        (self.repo / "templates" / "skill.md").write_text("v2\n", encoding="utf-8")
        self.write_manifest("1.1.0")
        self.write_changelog_entries(("1.1.0", "2026-07-17"), ("1.0.0", "2026-07-16"))
        git(self.repo, "commit", "-am", "first bump")
        (self.repo / "templates" / "skill.md").write_text("v3\n", encoding="utf-8")
        self.write_manifest("1.2.0")
        self.write_changelog_entries(
            ("1.2.0", "2026-07-18"),
            ("1.1.0", "2026-07-17"),
            ("1.0.0", "2026-07-16"),
        )
        git(self.repo, "commit", "-am", "second bump")
        result = self.gate(base="main")
        self.assertEqual(result.returncode, 1)
        self.assertIn("adds 2 version headings", result.stderr)
        self.assertIn("1.2.0, 1.1.0", result.stderr)

    def test_collapsed_intra_branch_bump_passes(self) -> None:
        # The documented escape from the failure above: rewrite the branch's
        # single heading rather than stacking a second one.
        git(self.repo, "checkout", "-b", "feature")
        (self.repo / "templates" / "skill.md").write_text("v2\n", encoding="utf-8")
        self.write_manifest("1.1.0")
        self.write_changelog_entries(("1.1.0", "2026-07-17"), ("1.0.0", "2026-07-16"))
        git(self.repo, "commit", "-am", "first bump")
        self.write_manifest("1.2.0")
        self.write_changelog_entries(("1.2.0", "2026-07-18"), ("1.0.0", "2026-07-16"))
        git(self.repo, "commit", "-am", "collapse into one release")
        result = self.gate(base="main")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("one version step", result.stdout)

    def test_missed_tag_deadlocks_the_push_gate_without_a_step_base(self) -> None:
        # Push-to-main resolves its base to the last release tag. If a release
        # ever fails to tag, that release stays inside the diff, so the next
        # push looks like a two-heading branch -- and the tagging job that
        # would create the missing tag waits on this gate, so nothing heals it.
        git(self.repo, "tag", "v1.0.0")
        self.release("1.1.0", ("1.0.0", "2026-07-16"))  # tagging failed here
        self.release("1.2.0", ("1.1.0", "2026-07-18"), ("1.0.0", "2026-07-16"))
        stuck = self.gate(base="v1.0.0")
        self.assertEqual(stuck.returncode, 1)
        self.assertIn("adds 2 version headings", stuck.stderr)

    def test_step_base_lets_the_push_gate_recover_a_missed_tag(self) -> None:
        # Same repository state, measured the way CI now measures it: payload
        # still gated from the last tag, one-heading rule from the previous
        # commit on main. This push released once, so it passes and the tagger
        # downstream gets to create both missing tags.
        git(self.repo, "tag", "v1.0.0")
        self.release("1.1.0", ("1.0.0", "2026-07-16"))
        self.release("1.2.0", ("1.1.0", "2026-07-18"), ("1.0.0", "2026-07-16"))
        result = self.gate(base="v1.0.0", step_base="HEAD^")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("one version step from HEAD^", result.stdout)

    def test_step_base_still_rejects_two_headings_in_one_push(self) -> None:
        # The rule itself is not relaxed: one commit that adds two headings is
        # exactly what the gate exists to stop, step base or not.
        git(self.repo, "tag", "v1.0.0")
        (self.repo / "templates" / "skill.md").write_text("v2\n", encoding="utf-8")
        self.write_manifest("1.2.0")
        self.write_changelog_entries(
            ("1.2.0", "2026-07-18"), ("1.1.0", "2026-07-17"), ("1.0.0", "2026-07-16")
        )
        git(self.repo, "commit", "-am", "two releases in one commit")
        result = self.gate(base="v1.0.0", step_base="HEAD^")
        self.assertEqual(result.returncode, 1)
        self.assertIn("adds 2 version headings", result.stderr)

    def test_unresolvable_step_base_fails_cleanly(self) -> None:
        (self.repo / "templates" / "skill.md").write_text("v2\n", encoding="utf-8")
        self.write_manifest("1.1.0")
        self.write_changelog_entries(("1.1.0", "2026-07-18"), ("1.0.0", "2026-07-16"))
        result = self.gate(step_base="refs/heads/nonexistent")
        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot resolve version-step base", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_bump_reusing_a_base_heading_fails(self) -> None:
        # The entry must be written on the branch that releases it. A heading
        # pre-written on the base and merely adopted by a later bump would slip
        # a release past the one-step rule with no new heading at all.
        self.write_changelog_entries(("1.1.0", "2026-07-17"), ("1.0.0", "2026-07-16"))
        git(self.repo, "commit", "-am", "pre-write the next entry")
        self.write_manifest("1.1.0")
        result = self.gate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("adds no new heading", result.stderr)

    def test_correcting_an_old_entry_date_is_not_a_new_version(self) -> None:
        # The one-step check compares version tokens, not whole heading lines,
        # so editing a shipped entry's date is not mistaken for a release.
        self.write_changelog_entries(("1.0.0", "2026-07-16"))
        git(self.repo, "commit", "-am", "baseline changelog")
        (self.repo / "templates" / "skill.md").write_text("v2\n", encoding="utf-8")
        self.write_manifest("1.1.0")
        self.write_changelog_entries(("1.1.0", "2026-07-18"), ("1.0.0", "2026-07-15"))
        result = self.gate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("one version step", result.stdout)

    def test_first_changelog_import_is_not_a_multi_step(self) -> None:
        # A repository adding CHANGELOG.md for the first time imports its whole
        # history at once; with no base changelog there is nothing to step from.
        (self.repo / "CHANGELOG.md").unlink()
        git(self.repo, "commit", "-am", "remove changelog")
        (self.repo / "templates" / "skill.md").write_text("v2\n", encoding="utf-8")
        self.write_manifest("1.1.0")
        self.write_changelog_entries(("1.1.0", "2026-07-18"), ("1.0.0", "2026-07-16"))
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
            env=git_env(),
        )
        return set(result.stdout.split())

    def add_bare_origin(self) -> Path:
        origin = self.base / "origin.git"
        subprocess.run(
            ["git", "init", "--bare", str(origin)],
            check=True,
            capture_output=True,
            text=True,
            env=git_env(),
        )
        git(self.repo, "remote", "add", "origin", str(origin))
        return origin

    def remote_tags(self, origin: Path) -> set[str]:
        result = subprocess.run(
            ["git", "-C", str(origin), "tag"],
            check=True,
            capture_output=True,
            text=True,
            env=git_env(),
        )
        return set(result.stdout.split())

    def test_creates_tag_once(self) -> None:
        result = run_script(TAG_SCRIPT, "--repo", str(self.repo))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.tags(), {"v1.0.0"})
        again = run_script(TAG_SCRIPT, "--repo", str(self.repo))
        self.assertEqual(again.returncode, 0)
        self.assertIn("already exists", again.stdout)

    def write_release(self, manifest_version: str, *changelog_versions: str) -> None:
        """Point the manifest at one version and the changelog at several.

        Changelog order is newest-first, as the real file is written.
        """
        (self.repo / "manifest.json").write_text(
            json.dumps({"name": "se-ai-command-pack", "version": manifest_version})
            + "\n",
            encoding="utf-8",
        )
        body = "".join(
            f"## {v} - 2026-08-16\n\n- Notes.\n\n" for v in changelog_versions
        )
        (self.repo / "CHANGELOG.md").write_text(
            "# Changelog\n\n" + body, encoding="utf-8"
        )
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-m", f"release {manifest_version}")

    def test_multi_version_merge_tags_every_released_version(self) -> None:
        # Audit A-041: one branch bumped twice, so the merge shipped two
        # changelog versions. Tagging only the manifest's final value is what
        # left v0.53.0 permanently missing.
        git(self.repo, "tag", "v1.0.0")
        self.write_release("1.1.1", "1.1.1", "1.1.0", "1.0.0")
        result = run_script(TAG_SCRIPT, "--repo", str(self.repo))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.tags(), {"v1.0.0", "v1.1.0", "v1.1.1"})
        # Both are announced, so the extra tag is visible in CI logs rather
        # than appearing silently.
        self.assertIn("v1.1.0", result.stdout)
        self.assertIn("v1.1.1", result.stdout)

    def test_older_untagged_version_is_not_backfilled(self) -> None:
        # The v0.53.0 shape itself: a historical hole below the highest tag.
        # Tagging it here would put it on today's HEAD, claiming a commit
        # shipped a release it did not. Leaving it missing is the honest state.
        git(self.repo, "tag", "v1.0.0")
        git(self.repo, "tag", "v1.1.0")
        self.write_release("1.1.0", "1.1.0", "1.0.1", "1.0.0")
        result = run_script(TAG_SCRIPT, "--repo", str(self.repo))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("v1.0.1", self.tags())
        self.assertEqual(self.tags(), {"v1.0.0", "v1.1.0"})

    def test_single_bump_still_tags_exactly_one(self) -> None:
        # The ordinary case must not gain tags from the changelog scan.
        git(self.repo, "tag", "v1.0.0")
        self.write_release("1.1.0", "1.1.0", "1.0.0")
        result = run_script(TAG_SCRIPT, "--repo", str(self.repo))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.tags(), {"v1.0.0", "v1.1.0"})
        self.assertNotIn("this push releases", result.stdout)

    def test_push_without_a_bump_reports_the_existing_tag(self) -> None:
        git(self.repo, "tag", "v1.0.0")
        self.write_release("1.0.0", "1.0.0")
        result = run_script(TAG_SCRIPT, "--repo", str(self.repo))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.tags(), {"v1.0.0"})
        self.assertIn("already exists", result.stdout)

    def test_untagged_repository_tags_only_the_manifest_version(self) -> None:
        # No tags at all: the changelog is pre-tagging history, so claiming all
        # of it at HEAD would invent releases.
        self.write_release("1.1.0", "1.1.0", "1.0.0", "0.9.0")
        result = run_script(TAG_SCRIPT, "--repo", str(self.repo))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.tags(), {"v1.1.0"})

    def test_non_semver_manifest_version_fails_cleanly(self) -> None:
        # Ordering versions needs numeric parts, so a pre-release string has to
        # be rejected with a message rather than a ValueError traceback out of
        # _version_key, which main() does not catch.
        self.write_release("1.1.0-rc1", "1.0.0")
        result = run_script(TAG_SCRIPT, "--repo", str(self.repo))
        self.assertEqual(result.returncode, 1)
        self.assertIn("is not X.Y.Z", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(self.tags(), set())

    def test_unreadable_changelog_fails_instead_of_falling_back(self) -> None:
        # A changelog that exists but cannot be read must not degrade to
        # manifest-only tagging: that silent fallback is the A-041 loss mode.
        self.write_release("1.1.0", "1.1.0", "1.0.9")
        git(self.repo, "tag", "v1.0.8")
        changelog = self.repo / "CHANGELOG.md"
        changelog.write_bytes(b"# Changelog\n\n## 1.1.0 - \xff\xfe not utf-8\n")
        result = run_script(TAG_SCRIPT, "--repo", str(self.repo))
        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot read", result.stderr)
        self.assertEqual(self.tags(), {"v1.0.8"})

    def test_missing_changelog_still_tags_the_manifest_version(self) -> None:
        # Absent is the benign case and keeps the pre-A-041 behaviour.
        (self.repo / "CHANGELOG.md").unlink(missing_ok=True)
        result = run_script(TAG_SCRIPT, "--repo", str(self.repo))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.tags(), {"v1.0.0"})

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

    def test_pip_cache_on_every_setup_python_step(self) -> None:
        """Every setup-python step caches pip (A-038). Enumerated rather than
        counted, so adding a lane cannot silently drop the cache."""
        self.assertEqual(
            self.text.count("cache: pip"), self.text.count("uses: actions/setup-python")
        )
        self.assertGreaterEqual(self.text.count("cache: pip"), 3)

    def test_concurrency_with_pr_only_cancellation(self) -> None:
        self.assertIn("concurrency:", self.text)
        self.assertIn(
            "cancel-in-progress: ${{ github.event_name == 'pull_request' }}",
            self.text,
        )

    def test_auto_tag_depends_on_release_gate(self) -> None:
        # Anchor to the auto-tag-release job body: the same needs string also
        # appears under ci-result, so a bare substring match is ambiguous and
        # would pass even if auto-tag-release dropped the gate dependency.
        _, _, tail = self.text.partition("auto-tag-release:")
        self.assertTrue(tail, "auto-tag-release job not found")
        self.assertIn("needs: [unittest, lint, release-payload-gate]", tail)

    def test_release_gate_runs_on_push_to_main(self) -> None:
        # The full PR-or-push expression is unique to release-payload-gate;
        # auto-tag-release uses a push-only if without the pull_request clause,
        # so matching the whole expression anchors the assertion to the gate.
        self.assertIn(
            "if: github.event_name == 'pull_request' || "
            "(github.event_name == 'push' && github.ref == 'refs/heads/main')",
            self.text,
        )


if __name__ == "__main__":
    unittest.main()

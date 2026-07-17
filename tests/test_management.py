"""Pack lifecycle command tests."""

from __future__ import annotations

import json
import subprocess
from unittest import mock

from install_test_support import (
    PACK_ROOT,
    TempDirTestCase,
    install_ok,
    make_home,
    run_installer,
)

from install import main
from installer.management import _run_git, update_pack


class StatusCommandTest(TempDirTestCase):
    def test_status_reports_install_checkout_and_platforms(self) -> None:
        home = make_home(self.base)
        install_ok("--root", str(home))
        expected_version = json.loads(
            (PACK_ROOT / "manifest.json").read_text(encoding="utf-8")
        )["version"]

        result = install_ok("status", "--root", str(home))

        self.assertIn(f"se-ai-command-pack {expected_version}", result.stdout)
        self.assertIn("platforms: agents, claude, codex", result.stdout)
        self.assertIn("installed version matches", result.stdout)

    def test_status_returns_one_when_not_installed(self) -> None:
        home = make_home(self.base)
        result = run_installer("status", "--root", str(home))
        self.assertEqual(result.returncode, 1)
        self.assertIn("not installed", result.stdout)

    @mock.patch("install.load_manifest", side_effect=AssertionError)
    def test_status_does_not_load_checkout_manifest(
        self, load_manifest: mock.Mock
    ) -> None:
        home = make_home(self.base)
        install_ok("--root", str(home))

        self.assertEqual(main(["status", "--root", str(home)]), 0)
        load_manifest.assert_not_called()


class LifecycleCompatibilityTest(TempDirTestCase):
    def test_refresh_command_uses_existing_install_path(self) -> None:
        home = make_home(self.base)
        install_ok("--root", str(home))
        result = install_ok("refresh", "--root", str(home), "--dry-run")
        self.assertIn("mode: dry-run", result.stdout)
        self.assertIn("unchanged", result.stdout)

    def test_remove_command_previews_removal(self) -> None:
        home = make_home(self.base)
        install_ok("--root", str(home))
        result = install_ok("remove", "--root", str(home), "--dry-run")
        self.assertIn("mode: remove", result.stdout)
        self.assertIn("would-remove", result.stdout)

    def test_legacy_remove_flag_is_rejected(self) -> None:
        result = run_installer("--remove", "--root", str(self.base))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unrecognized arguments: --remove", result.stderr)


class UpdateCommandTest(TempDirTestCase):
    def _installed_home(self):
        home = make_home(self.base)
        install_ok("--root", str(home))
        return home

    @mock.patch("install.update_pack", return_value=0)
    def test_cli_forwards_platform_selection(self, update: mock.Mock) -> None:
        home = self._installed_home()

        result = main(
            ["update", "--root", str(home), "--platform", "codex", "--all"]
        )

        self.assertEqual(result, 0)
        self.assertEqual(update.call_args.kwargs["platforms"], ["codex"])
        self.assertTrue(update.call_args.kwargs["install_all"])

    @mock.patch("installer.management.subprocess.run")
    def test_git_failure_includes_stderr(self, run_process: mock.Mock) -> None:
        run_process.return_value = subprocess.CompletedProcess(
            [], 1, stdout="", stderr="no upstream configured\n"
        )

        with self.assertRaisesRegex(SystemExit, "no upstream configured"):
            _run_git(self.base, "pull", "--ff-only")

    def test_update_dry_run_fetches_and_plans_only(self) -> None:
        home = self._installed_home()
        with (
            mock.patch("installer.management._run_git") as run_git,
            mock.patch("installer.management.subprocess.run") as run_process,
        ):
            run_git.side_effect = ["", "", "0\t1"]
            run_process.return_value = subprocess.CompletedProcess([], 0)

            result = update_pack(
                home,
                dry_run=True,
                force=False,
                backup=False,
                platforms=["codex"],
                install_all=False,
            )

        self.assertEqual(result, 0)
        self.assertEqual(run_git.call_args_list[0].args[1:], ("status", "--porcelain"))
        self.assertEqual(run_git.call_args_list[1].args[1:], ("fetch", "--quiet"))
        self.assertEqual(run_process.call_count, 1)
        self.assertIn("--dry-run", run_process.call_args.args[0])
        self.assertIn("--platform", run_process.call_args.args[0])
        self.assertIn("codex", run_process.call_args.args[0])

    def test_update_applies_with_fresh_process_after_ff_only_pull(self) -> None:
        home = self._installed_home()
        with (
            mock.patch("installer.management._run_git") as run_git,
            mock.patch("installer.management.subprocess.run") as run_process,
        ):
            run_git.return_value = ""
            run_process.side_effect = [
                subprocess.CompletedProcess([], 0),
                subprocess.CompletedProcess([], 0),
            ]

            result = update_pack(
                home,
                dry_run=False,
                force=False,
                backup=False,
                platforms=None,
                install_all=True,
            )

        self.assertEqual(result, 0)
        self.assertEqual(run_git.call_args_list[1].args[1:], ("pull", "--ff-only"))
        self.assertEqual(run_process.call_count, 2)
        self.assertIn("--dry-run", run_process.call_args_list[0].args[0])
        self.assertNotIn("--dry-run", run_process.call_args_list[1].args[0])
        self.assertIn("--all", run_process.call_args_list[0].args[0])
        self.assertIn("--all", run_process.call_args_list[1].args[0])

    @mock.patch("installer.management._run_git")
    def test_update_refuses_dirty_checkout(self, run_git: mock.Mock) -> None:
        home = self._installed_home()
        run_git.return_value = " M install.py"

        with self.assertRaisesRegex(SystemExit, "uncommitted changes"):
            update_pack(
                home,
                dry_run=False,
                force=False,
                backup=False,
                platforms=None,
                install_all=False,
            )


if __name__ == "__main__":
    import unittest

    unittest.main()

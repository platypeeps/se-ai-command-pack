"""Pack lifecycle command tests."""

from __future__ import annotations

import subprocess
from unittest import mock

from install_test_support import (
    TempDirTestCase,
    install_ok,
    make_home,
    run_installer,
)

from installer.management import update_pack


class StatusCommandTest(TempDirTestCase):
    def test_status_reports_install_checkout_and_platforms(self) -> None:
        home = make_home(self.base)
        install_ok("--root", str(home))

        result = install_ok("status", "--root", str(home))

        self.assertIn("se-ai-command-pack 0.2.0", result.stdout)
        self.assertIn("platforms: agents, claude, codex", result.stdout)
        self.assertIn("installed version matches", result.stdout)

    def test_status_returns_one_when_not_installed(self) -> None:
        home = make_home(self.base)
        result = run_installer("status", "--root", str(home))
        self.assertEqual(result.returncode, 1)
        self.assertIn("not installed", result.stdout)


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

    def test_update_dry_run_fetches_and_plans_only(self) -> None:
        home = self._installed_home()
        with (
            mock.patch("installer.management._run_git") as run_git,
            mock.patch("installer.management.subprocess.run") as run_process,
        ):
            run_git.side_effect = ["", "", "0\t1"]
            run_process.return_value = subprocess.CompletedProcess([], 0)

            result = update_pack(
                home, dry_run=True, force=False, backup=False
            )

        self.assertEqual(result, 0)
        self.assertEqual(run_git.call_args_list[0].args[1:], ("status", "--porcelain"))
        self.assertEqual(run_git.call_args_list[1].args[1:], ("fetch", "--quiet"))
        self.assertEqual(run_process.call_count, 1)
        self.assertIn("--dry-run", run_process.call_args.args[0])

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
                home, dry_run=False, force=False, backup=False
            )

        self.assertEqual(result, 0)
        self.assertEqual(run_git.call_args_list[1].args[1:], ("pull", "--ff-only"))
        self.assertEqual(run_process.call_count, 2)
        self.assertIn("--dry-run", run_process.call_args_list[0].args[0])
        self.assertNotIn("--dry-run", run_process.call_args_list[1].args[0])

    @mock.patch("installer.management._run_git")
    def test_update_refuses_dirty_checkout(self, run_git: mock.Mock) -> None:
        home = self._installed_home()
        run_git.return_value = " M install.py"

        with self.assertRaisesRegex(SystemExit, "uncommitted changes"):
            update_pack(home, dry_run=False, force=False, backup=False)


if __name__ == "__main__":
    import unittest

    unittest.main()

"""Pack lifecycle command tests."""

from __future__ import annotations

import json
import os
import subprocess
import unittest
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
from installer.registry import PACK_NAME, PROVENANCE_FILE


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

    def test_early_commands_reject_missing_install_root(self) -> None:
        missing = self.base / "missing"
        for command in ("status", "update"):
            with self.subTest(command=command):
                result = run_installer(command, "--root", str(missing))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("install root not found", result.stderr)

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


class UpdateSourceTrustTest(TempDirTestCase):
    """Trust gate on the provenance-recorded source checkout (audit A-017)."""

    def _installed_home(self):
        home = make_home(self.base)
        install_ok("--root", str(home))
        return home

    def _make_foreign_checkout(self, *, git=True, git_as_file=False, name=PACK_NAME):
        """A valid-looking pack checkout that is NOT the running checkout."""
        src = self.base / "foreign-checkout"
        src.mkdir()
        (src / "install.py").write_text("# fake installer\n", encoding="utf-8")
        (src / "manifest.json").write_text(
            json.dumps({"name": name, "version": "0.0.0"}), encoding="utf-8"
        )
        if git_as_file:
            (src / ".git").write_text("gitdir: /elsewhere/.git\n", encoding="utf-8")
        elif git:
            (src / ".git").mkdir()
        return src.resolve()

    def _point_provenance(self, home, source_root) -> None:
        prov = home / PROVENANCE_FILE
        data = json.loads(prov.read_text(encoding="utf-8"))
        data["sourceRoot"] = str(source_root)
        prov.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def _fail_if_git_or_exec(self):
        """Patches that raise if any git or subprocess call is attempted."""
        return (
            mock.patch(
                "installer.management._run_git",
                side_effect=AssertionError("git must not run"),
            ),
            mock.patch(
                "installer.management.subprocess.run",
                side_effect=AssertionError("exec must not run"),
            ),
        )

    def test_refuses_relocated_current_user_checkout_without_confirmation(
        self,
    ) -> None:
        """PRINCIPAL CONTROL: a current-user-owned git checkout that differs
        from the running checkout must be refused (by the confirmation gate, not
        the .git gate) with zero git and zero exec calls."""
        home = self._installed_home()
        src = self._make_foreign_checkout(git=True)
        self._point_provenance(home, src)
        no_git, no_exec = self._fail_if_git_or_exec()
        with no_git, no_exec, mock.patch("installer.management.sys.stdin") as stdin:
            stdin.isatty.return_value = False
            with self.assertRaisesRegex(SystemExit, "--confirm-source"):
                update_pack(
                    home,
                    dry_run=False,
                    force=False,
                    backup=False,
                    platforms=None,
                    install_all=False,
                    confirm_source=False,
                )

    def test_refuses_non_git_foreign_source(self) -> None:
        home = self._installed_home()
        src = self._make_foreign_checkout(git=False)
        self._point_provenance(home, src)
        no_git, no_exec = self._fail_if_git_or_exec()
        with no_git, no_exec:
            with self.assertRaisesRegex(SystemExit, "not a git repository"):
                update_pack(
                    home,
                    dry_run=False,
                    force=False,
                    backup=False,
                    platforms=None,
                    install_all=False,
                )

    @unittest.skipUnless(hasattr(os, "geteuid"), "requires POSIX geteuid")
    def test_refuses_foreign_owned_source(self) -> None:
        home = self._installed_home()
        src = self._make_foreign_checkout(git=True)
        self._point_provenance(home, src)
        no_git, no_exec = self._fail_if_git_or_exec()
        with (
            no_git,
            no_exec,
            mock.patch(
                "installer.management.os.geteuid", return_value=os.geteuid() + 1
            ),
        ):
            with self.assertRaisesRegex(SystemExit, "not owned by the current user"):
                update_pack(
                    home,
                    dry_run=False,
                    force=False,
                    backup=False,
                    platforms=None,
                    install_all=False,
                    confirm_source=True,
                )

    def test_same_checkout_needs_no_confirmation(self) -> None:
        """AC2: the normal same-checkout path (sourceRoot == running checkout)
        proceeds without confirmation."""
        home = self._installed_home()  # provenance sourceRoot == running checkout
        with (
            mock.patch("installer.management._run_git", return_value=""),
            mock.patch("installer.management.subprocess.run") as run_process,
        ):
            run_process.return_value = subprocess.CompletedProcess([], 0)
            result = update_pack(
                home,
                dry_run=False,
                force=False,
                backup=False,
                platforms=None,
                install_all=True,
                confirm_source=False,
            )
        self.assertEqual(result, 0)

    def test_relocated_source_confirmed_with_flag_proceeds(self) -> None:
        home = self._installed_home()
        src = self._make_foreign_checkout(git=True)
        self._point_provenance(home, src)
        with (
            mock.patch("installer.management._run_git", return_value="") as run_git,
            mock.patch("installer.management.subprocess.run") as run_process,
        ):
            run_process.return_value = subprocess.CompletedProcess([], 0)
            result = update_pack(
                home,
                dry_run=False,
                force=False,
                backup=False,
                platforms=None,
                install_all=True,
                confirm_source=True,
            )
        self.assertEqual(result, 0)
        self.assertEqual(run_git.call_args_list[1].args[1:], ("pull", "--ff-only"))

    def test_relocated_source_interactive_yes_proceeds(self) -> None:
        home = self._installed_home()
        src = self._make_foreign_checkout(git=True)
        self._point_provenance(home, src)
        with (
            mock.patch("installer.management._run_git", return_value=""),
            mock.patch("installer.management.subprocess.run") as run_process,
            mock.patch("installer.management.sys.stdin") as stdin,
            mock.patch("builtins.input", return_value="y"),
        ):
            stdin.isatty.return_value = True
            run_process.return_value = subprocess.CompletedProcess([], 0)
            result = update_pack(
                home,
                dry_run=False,
                force=False,
                backup=False,
                platforms=None,
                install_all=True,
                confirm_source=False,
            )
        self.assertEqual(result, 0)

    def test_relocated_source_interactive_no_refuses(self) -> None:
        home = self._installed_home()
        src = self._make_foreign_checkout(git=True)
        self._point_provenance(home, src)
        no_git, no_exec = self._fail_if_git_or_exec()
        with (
            no_git,
            no_exec,
            mock.patch("installer.management.sys.stdin") as stdin,
            mock.patch("builtins.input", return_value="n"),
        ):
            stdin.isatty.return_value = True
            with self.assertRaisesRegex(SystemExit, "not confirmed"):
                update_pack(
                    home,
                    dry_run=False,
                    force=False,
                    backup=False,
                    platforms=None,
                    install_all=False,
                    confirm_source=False,
                )

    def test_accepts_git_file_worktree(self) -> None:
        home = self._installed_home()
        src = self._make_foreign_checkout(git=False, git_as_file=True)
        self._point_provenance(home, src)
        with (
            mock.patch("installer.management._run_git", return_value=""),
            mock.patch("installer.management.subprocess.run") as run_process,
        ):
            run_process.return_value = subprocess.CompletedProcess([], 0)
            result = update_pack(
                home,
                dry_run=False,
                force=False,
                backup=False,
                platforms=None,
                install_all=True,
                confirm_source=True,
            )
        self.assertEqual(result, 0)

    def test_ownership_check_skipped_without_geteuid(self) -> None:
        """Without an effective-uid primitive, the ownership branch is skipped
        while the git-repo and confirmation gates still apply."""
        home = self._installed_home()
        src = self._make_foreign_checkout(git=True)
        self._point_provenance(home, src)
        with (
            mock.patch("installer.management._run_git", return_value=""),
            mock.patch("installer.management.subprocess.run") as run_process,
            mock.patch.object(os, "geteuid", None, create=True),
        ):
            run_process.return_value = subprocess.CompletedProcess([], 0)
            result = update_pack(
                home,
                dry_run=False,
                force=False,
                backup=False,
                platforms=None,
                install_all=True,
                confirm_source=True,
            )
        self.assertEqual(result, 0)

    @mock.patch("install.update_pack", return_value=0)
    def test_cli_forwards_confirm_source(self, update: mock.Mock) -> None:
        home = self._installed_home()
        result = main(["update", "--root", str(home), "--confirm-source"])
        self.assertEqual(result, 0)
        self.assertTrue(update.call_args.kwargs["confirm_source"])

    @mock.patch("install.update_pack", return_value=0)
    def test_cli_confirm_source_defaults_false(self, update: mock.Mock) -> None:
        home = self._installed_home()
        main(["update", "--root", str(home)])
        self.assertFalse(update.call_args.kwargs["confirm_source"])


if __name__ == "__main__":
    unittest.main()

"""Pack lifecycle command tests."""

from __future__ import annotations

import contextlib
import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

from install_test_support import (
    PACK_ROOT,
    TempDirTestCase,
    git_env,
    install_ok,
    make_home,
    run_installer,
)

from install import main
from installer.management import (
    _fd_pinning_tier,
    _pinned_child_kwargs,
    _run_git,
    _source_checkout,
    update_pack,
)
from installer.registry import PACK_NAME, PROVENANCE_FILE


class UpdateFixtureMixin:
    """Installed root and provenance helpers shared by the update tests."""

    def _installed_home(self):
        home = make_home(self.base)
        install_ok("--root", str(home))
        return home

    def _point_provenance(self, home, source_root) -> None:
        prov = home / PROVENANCE_FILE
        data = json.loads(prov.read_text(encoding="utf-8"))
        data["sourceRoot"] = str(source_root)
        prov.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


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


class UpdateCommandTest(UpdateFixtureMixin, TempDirTestCase):
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

    @mock.patch(
        "installer.management.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="git", timeout=60),
    )
    def test_git_timeout_fails_cleanly(self, run_process: mock.Mock) -> None:
        # A-013: a hung git maps to a clean SystemExit, not a raw traceback.
        with self.assertRaisesRegex(SystemExit, "timed out"):
            _run_git(self.base, "pull", "--ff-only")

    @mock.patch(
        "installer.management.subprocess.run", side_effect=FileNotFoundError()
    )
    def test_git_missing_fails_cleanly(self, run_process: mock.Mock) -> None:
        with self.assertRaisesRegex(SystemExit, "git not found"):
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
        self.assertNotIn("--verbose", run_process.call_args_list[1].args[0])

    def test_update_forwards_verbose_to_refresh_process(self) -> None:
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
                verbose=True,
            )

        self.assertEqual(result, 0)
        self.assertIn("--verbose", run_process.call_args_list[0].args[0])
        self.assertIn("--verbose", run_process.call_args_list[1].args[0])

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


class UpdateSourceTrustTest(UpdateFixtureMixin, TempDirTestCase):
    """Trust gate on the provenance-recorded source checkout (audit A-017)."""

    def _make_foreign_checkout(
        self,
        *,
        git=True,
        git_as_file=False,
        gitdir=None,
        name=PACK_NAME,
        where="foreign-checkout",
    ):
        """A valid-looking pack checkout that is NOT the running checkout."""
        src = self.base / where
        src.mkdir()
        (src / "install.py").write_text("# fake installer\n", encoding="utf-8")
        (src / "manifest.json").write_text(
            json.dumps({"name": name, "version": "0.0.0"}), encoding="utf-8"
        )
        if git_as_file:
            target = self._real_gitdir(where) if gitdir is None else gitdir
            (src / ".git").write_text(f"gitdir: {target}\n", encoding="utf-8")
        elif git:
            (src / ".git").mkdir()
        return src.resolve()

    def _real_gitdir(self, where="foreign-checkout") -> Path:
        """A real, same-user gitdir a worktree pointer may legitimately name."""
        target = self.base / "worktrees" / where
        target.mkdir(parents=True)
        return target

    def _make_symlinked_git_checkout(self, where="symlinked-git") -> Path:
        real = self.base / f"{where}-real"
        (real / ".git").mkdir(parents=True)
        src = self._make_foreign_checkout(git=False, where=where)
        (src / ".git").symlink_to(real / ".git")
        return src

    @contextlib.contextmanager
    def _fd_spy(self, opened: list[int], closed: list[int]):
        """Record every os.open result and os.close argument in scope.

        Patching ``os.open`` replaces the function object, so
        ``os.open in os.supports_dir_fd`` turns false and
        ``_fd_pinning_tier()`` reports tier 2 inside this scope: the entry
        checks take their path fallback and the only spied descriptor is the
        pinned directory fd. That is exactly the descriptor whose closure the
        refusal tests assert, and the ``handle.close()``-on-refusal path under
        test is tier-independent; tier 1's transient ``dir_fd`` reads are
        closed by their ``os.fdopen`` context managers and are not covered
        here.
        """
        real_open, real_close = os.open, os.close

        def spy_open(*args, **kwargs):
            handle = real_open(*args, **kwargs)
            opened.append(handle)
            return handle

        def spy_close(handle):
            closed.append(handle)
            return real_close(handle)

        with (
            mock.patch.object(os, "open", spy_open),
            mock.patch.object(os, "close", spy_close),
        ):
            yield

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
        """A .git pointer file is accepted once its gitdir target is verified."""
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

    def test_refuses_symlinked_git_entry(self) -> None:
        """A symlinked .git re-points the repository outside the checked
        directory and is refused before any git or exec."""
        home = self._installed_home()
        src = self._make_symlinked_git_checkout()
        self._point_provenance(home, src)
        no_git, no_exec = self._fail_if_git_or_exec()
        with no_git, no_exec:
            with self.assertRaisesRegex(SystemExit, "symlinked .git"):
                update_pack(
                    home,
                    dry_run=False,
                    force=False,
                    backup=False,
                    platforms=None,
                    install_all=False,
                    confirm_source=True,
                )

    def test_refuses_symlinked_installer(self) -> None:
        """A symlinked install.py would let the relative exec escape the pinned
        directory, so the checkout counts as unavailable."""
        home = self._installed_home()
        src = self._make_foreign_checkout()
        elsewhere = self.base / "elsewhere-install.py"
        elsewhere.write_text("# other installer\n", encoding="utf-8")
        (src / "install.py").unlink()
        (src / "install.py").symlink_to(elsewhere)
        self._point_provenance(home, src)
        no_git, no_exec = self._fail_if_git_or_exec()
        with no_git, no_exec:
            with self.assertRaisesRegex(SystemExit, "unavailable"):
                update_pack(
                    home,
                    dry_run=False,
                    force=False,
                    backup=False,
                    platforms=None,
                    install_all=False,
                    confirm_source=True,
                )

    def test_refuses_dangling_gitdir_pointer(self) -> None:
        home = self._installed_home()
        src = self._make_foreign_checkout(
            git=False, git_as_file=True, gitdir=self.base / "missing" / ".git"
        )
        self._point_provenance(home, src)
        no_git, no_exec = self._fail_if_git_or_exec()
        with no_git, no_exec:
            with self.assertRaisesRegex(SystemExit, "unverified gitdir"):
                update_pack(
                    home,
                    dry_run=False,
                    force=False,
                    backup=False,
                    platforms=None,
                    install_all=False,
                    confirm_source=True,
                )

    def test_refuses_non_directory_gitdir_target(self) -> None:
        """A gitdir target that exists but is not a directory is refused."""
        home = self._installed_home()
        plain = self.base / "plain-file-target"
        plain.write_text("not a git directory\n", encoding="utf-8")
        src = self._make_foreign_checkout(git=False, git_as_file=True, gitdir=plain)
        self._point_provenance(home, src)
        no_git, no_exec = self._fail_if_git_or_exec()
        with no_git, no_exec:
            with self.assertRaisesRegex(SystemExit, "unverified gitdir"):
                update_pack(
                    home,
                    dry_run=False,
                    force=False,
                    backup=False,
                    platforms=None,
                    install_all=False,
                    confirm_source=True,
                )

    def test_refuses_malformed_gitdir_pointer(self) -> None:
        home = self._installed_home()
        src = self._make_foreign_checkout(git=False)
        (src / ".git").write_text("not a pointer\n", encoding="utf-8")
        self._point_provenance(home, src)
        no_git, no_exec = self._fail_if_git_or_exec()
        with no_git, no_exec:
            with self.assertRaisesRegex(SystemExit, "unverified gitdir"):
                update_pack(
                    home,
                    dry_run=False,
                    force=False,
                    backup=False,
                    platforms=None,
                    install_all=False,
                    confirm_source=True,
                )

    @unittest.skipUnless(hasattr(os, "geteuid"), "requires POSIX geteuid")
    def test_refuses_foreign_owned_gitdir_target(self) -> None:
        """The gitdir target is validated before the directory ownership gate,
        so a foreign-owned redirection is named as such."""
        home = self._installed_home()
        src = self._make_foreign_checkout(git=False, git_as_file=True)
        self._point_provenance(home, src)
        no_git, no_exec = self._fail_if_git_or_exec()
        with (
            no_git,
            no_exec,
            mock.patch(
                "installer.management.os.geteuid", return_value=os.geteuid() + 1
            ),
        ):
            with self.assertRaisesRegex(SystemExit, "unverified gitdir"):
                update_pack(
                    home,
                    dry_run=False,
                    force=False,
                    backup=False,
                    platforms=None,
                    install_all=False,
                    confirm_source=True,
                )

    def test_source_checkout_closes_fd_on_every_refusal(self) -> None:
        """No refusal path leaks the pinned directory descriptor."""
        home = self._installed_home()
        scenarios = [
            ("unavailable", self.base / "missing-checkout", "unavailable", True),
            (
                "wrong-pack",
                self._make_foreign_checkout(name="other-pack", where="wrong-pack"),
                f"is not {PACK_NAME}",
                True,
            ),
            (
                "non-repo",
                self._make_foreign_checkout(git=False, where="non-repo"),
                "not a git repository",
                True,
            ),
            (
                "symlinked-git",
                self._make_symlinked_git_checkout(),
                "symlinked .git",
                True,
            ),
            (
                "dangling-gitdir",
                self._make_foreign_checkout(
                    git=False,
                    git_as_file=True,
                    gitdir="/nonexistent/.git",
                    where="dangling-gitdir",
                ),
                "unverified gitdir",
                True,
            ),
            (
                "unconfirmed",
                self._make_foreign_checkout(where="unconfirmed"),
                "--confirm-source",
                False,
            ),
        ]
        for label, source_root, fragment, confirm_source in scenarios:
            with self.subTest(refusal=label):
                self._point_provenance(home, source_root)
                opened: list[int] = []
                closed: list[int] = []
                no_git, no_exec = self._fail_if_git_or_exec()
                with (
                    no_git,
                    no_exec,
                    mock.patch("installer.management.sys.stdin") as stdin,
                    self._fd_spy(opened, closed),
                ):
                    stdin.isatty.return_value = False
                    with self.assertRaisesRegex(SystemExit, fragment):
                        update_pack(
                            home,
                            dry_run=False,
                            force=False,
                            backup=False,
                            platforms=None,
                            install_all=False,
                            confirm_source=confirm_source,
                        )
                if label != "unavailable" and _fd_pinning_tier() < 3:
                    self.assertTrue(opened, "expected a pinned directory fd")
                self.assertLessEqual(set(opened), set(closed))

    @unittest.skipUnless(hasattr(os, "geteuid"), "requires POSIX geteuid")
    def test_foreign_owned_refusal_closes_fd(self) -> None:
        home = self._installed_home()
        src = self._make_foreign_checkout()
        self._point_provenance(home, src)
        opened: list[int] = []
        closed: list[int] = []
        no_git, no_exec = self._fail_if_git_or_exec()
        with (
            no_git,
            no_exec,
            mock.patch(
                "installer.management.os.geteuid", return_value=os.geteuid() + 1
            ),
            self._fd_spy(opened, closed),
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
        if _fd_pinning_tier() < 3:
            self.assertTrue(opened, "expected a pinned directory fd")
        self.assertLessEqual(set(opened), set(closed))

    def _record_handle_fds(self, fds: list[int | None]):
        def record(source, *args: str) -> str:
            fds.append(source.fd)
            return ""

        return mock.patch("installer.management._run_git", side_effect=record)

    def test_tier_two_fallback_still_pins_execution(self) -> None:
        """Without the dir_fd capability sets the entry checks fall back to
        paths, but git and the installer still run inside the held fd."""
        home = self._installed_home()
        src = self._make_foreign_checkout()
        self._point_provenance(home, src)
        fds: list[int | None] = []
        with (
            mock.patch.object(os, "supports_dir_fd", set()),
            mock.patch.object(os, "supports_follow_symlinks", set()),
            self._record_handle_fds(fds),
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
        self.assertIsNotNone(fds[0])
        self.assertEqual(run_process.call_args.kwargs["pass_fds"], (fds[0],))
        self.assertEqual(run_process.call_args.args[0][1], "install.py")

    def test_tier_three_without_geteuid_uses_path_flow(self) -> None:
        """Without an effective-uid primitive there is no descriptor to pin, so
        the installer keeps its absolute path."""
        home = self._installed_home()
        src = self._make_foreign_checkout()
        self._point_provenance(home, src)
        fds: list[int | None] = []
        with (
            mock.patch.object(os, "geteuid", None, create=True),
            self._record_handle_fds(fds),
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
        self.assertIsNone(fds[0])
        self.assertNotIn("pass_fds", run_process.call_args.kwargs)
        self.assertEqual(
            run_process.call_args.args[0][1], str(src / "install.py")
        )

    @unittest.skipUnless(hasattr(os, "geteuid"), "requires POSIX geteuid")
    def test_tier_three_without_directory_fd_still_checks_ownership(self) -> None:
        """geteuid without O_DIRECTORY/fchdir is the path tier, and its
        ownership refusal still applies."""
        home = self._installed_home()
        src = self._make_foreign_checkout()
        self._point_provenance(home, src)
        no_git, no_exec = self._fail_if_git_or_exec()
        with (
            no_git,
            no_exec,
            mock.patch.object(os, "O_DIRECTORY", None, create=True),
            mock.patch.object(os, "fchdir", None, create=True),
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


@unittest.skipIf(_fd_pinning_tier() == 3, "requires directory-fd pinning")
class SourcePinningTest(UpdateFixtureMixin, TempDirTestCase):
    """The checked directory is the used directory (audit A-017 follow-up).

    Every proof here swaps a decoy in at the recorded path after the trust
    checks pass; a run that re-resolved sourceRoot by name would reach it.
    """

    def setUp(self) -> None:
        super().setUp()
        # Two tests here call the real `_run_git`, and production code passes
        # no `env=` (installer/management.py), so the scrub has to be ambient.
        patcher = mock.patch.dict(os.environ, git_env(), clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _git(self, *args: str, cwd) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            env=git_env(),
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(f"git {' '.join(args)} failed: {result.stderr}")
        return result.stdout

    def _make_checkout(self, where: str, installer_body: str) -> Path:
        src = self.base / where
        src.mkdir()
        (src / "install.py").write_text(installer_body, encoding="utf-8")
        (src / "manifest.json").write_text(
            json.dumps({"name": PACK_NAME, "version": "0.0.0"}), encoding="utf-8"
        )
        (src / ".git").mkdir()
        return src.resolve()

    def _make_git_checkout(
        self, where: str, installer_body: str, *, upstream: bool = False
    ) -> Path:
        src = self.base / where
        src.mkdir()
        (src / "install.py").write_text(installer_body, encoding="utf-8")
        (src / "manifest.json").write_text(
            json.dumps({"name": PACK_NAME, "version": "0.0.0"}), encoding="utf-8"
        )
        self._git("init", "-q", cwd=src)
        self._git("checkout", "-q", "-b", "main", cwd=src)
        self._git("add", "-A", cwd=src)
        self._git("commit", "-q", "-m", "initial", cwd=src)
        if upstream:
            bare = self.base / f"{where}-origin.git"
            self._git("init", "-q", "--bare", str(bare), cwd=self.base)
            self._git("remote", "add", "origin", str(bare), cwd=src)
            self._git("push", "-q", "-u", "origin", "main", cwd=src)
        return src.resolve()

    def _sentinel_installer(self, sentinel: Path, marker: str) -> str:
        return (
            "import os\n"
            "from pathlib import Path\n"
            f"with open({str(sentinel)!r}, 'a', encoding='utf-8') as handle:\n"
            f"    handle.write("
            f"f'{marker}|{{os.getcwd()}}|{{Path(__file__).resolve()}}\\n')\n"
        )

    def test_handle_reads_through_pinned_fd_after_decoy_swap(self) -> None:
        home = self._installed_home()
        src = self._make_checkout("pinned", "# stub installer\n")
        (src / "sentinel.txt").write_text("original\n", encoding="utf-8")
        self._point_provenance(home, src)

        handle = _source_checkout(home, confirm_source=True)
        self.addCleanup(handle.close)
        moved = self.base / "pinned-moved"
        src.rename(moved)
        decoy = self._make_checkout("pinned", "# decoy installer\n")
        (decoy / "sentinel.txt").write_text("decoy\n", encoding="utf-8")

        self.assertEqual(os.fstat(handle.fd).st_ino, moved.stat().st_ino)
        self.assertNotEqual(moved.stat().st_ino, decoy.stat().st_ino)
        raw = os.open("sentinel.txt", os.O_RDONLY, dir_fd=handle.fd)
        with os.fdopen(raw, encoding="utf-8") as stream:
            self.assertEqual(stream.read().strip(), "original")

    def test_pinned_child_runs_inside_pinned_directory(self) -> None:
        """pass_fds keeps the descriptor alive through default close_fds, so
        the preexec_fn fchdir lands before exec."""
        pinned = self.base / "child-cwd"
        pinned.mkdir()
        fd = os.open(pinned, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, fd)

        result = subprocess.run(
            [sys.executable, "-c", "import os; print(os.getcwd())"],
            text=True,
            capture_output=True,
            check=False,
            **_pinned_child_kwargs(fd),
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), os.path.realpath(pinned))

    @unittest.skipUnless(shutil.which("git"), "requires git")
    def test_git_runs_in_pinned_directory_after_decoy_swap(self) -> None:
        """Unmocked: real git resolves the pinned directory, not the path."""
        home = self._installed_home()
        src = self._make_git_checkout("live", "# stub installer\n")
        self._point_provenance(home, src)

        handle = _source_checkout(home, confirm_source=True)
        self.addCleanup(handle.close)
        moved = self.base / "live-moved"
        src.rename(moved)
        decoy = self._make_git_checkout("live", "# decoy installer\n")

        toplevel = _run_git(handle, "rev-parse", "--show-toplevel")

        self.assertEqual(os.path.realpath(toplevel), os.path.realpath(moved))
        self.assertNotEqual(os.path.realpath(toplevel), os.path.realpath(decoy))

    @unittest.skipUnless(shutil.which("git"), "requires git")
    def test_update_execs_installer_inside_pinned_directory(self) -> None:
        """Unmocked update_pack: git and both installer processes stay inside
        the pinned checkout after the recorded path is swapped mid-run."""
        home = self._installed_home()
        sentinel = self.base / "sentinel.txt"
        src = self._make_git_checkout(
            "shipped", self._sentinel_installer(sentinel, "pinned"), upstream=True
        )
        self._point_provenance(home, src)
        moved = self.base / "shipped-moved"
        handle_fds: list[int | None] = []

        def swap_after_first_git(source, *args: str) -> str:
            output = _run_git(source, *args)
            if not handle_fds:
                handle_fds.append(source.fd)
                src.rename(moved)
                decoy = self.base / "shipped"
                decoy.mkdir()
                (decoy / "install.py").write_text(
                    self._sentinel_installer(sentinel, "decoy"), encoding="utf-8"
                )
            return output

        with (
            mock.patch(
                "installer.management._run_git", side_effect=swap_after_first_git
            ),
            mock.patch(
                "installer.management.subprocess.run", wraps=subprocess.run
            ) as spy,
        ):
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
        lines = sentinel.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 2, lines)  # plan process, then apply process
        for line in lines:
            marker, cwd, resolved = line.split("|")
            self.assertEqual(marker, "pinned")
            self.assertEqual(os.path.realpath(cwd), os.path.realpath(moved))
            self.assertEqual(
                os.path.realpath(resolved), os.path.realpath(moved / "install.py")
            )

        pinned_fd = handle_fds[0]
        git_calls = [c for c in spy.call_args_list if c.args[0][0] == "git"]
        installer_calls = [
            c for c in spy.call_args_list if c.args[0][0] == sys.executable
        ]
        self.assertTrue(git_calls)
        self.assertEqual(len(installer_calls), 2)
        for call in git_calls:
            self.assertEqual(call.args[0][:3], ["git", "-C", "."])
        for call in installer_calls:
            self.assertEqual(call.args[0][1], "install.py")
        for call in git_calls + installer_calls:
            self.assertEqual(call.kwargs["pass_fds"], (pinned_fd,))
            self.assertTrue(callable(call.kwargs["preexec_fn"]))


if __name__ == "__main__":
    unittest.main()

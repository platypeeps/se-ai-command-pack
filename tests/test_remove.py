"""End-to-end removal tests: vouching, drift preservation, refusals."""

from __future__ import annotations

import unittest

from install_test_support import (
    TempDirTestCase,
    install_ok,
    make_home,
    run_installer,
    tree_paths,
)

RECEIPT_FILE = ".se-ai-command-pack/installed-targets.txt"


class RemoveTest(TempDirTestCase):
    def installed_home(self, *args: str):
        home = make_home(self.base)
        install_ok("--root", str(home), *args)
        return home

    def test_full_remove_restores_empty_root(self) -> None:
        home = self.installed_home()
        result = install_ok("--root", str(home), "--remove")
        self.assertIn("removed", result.stdout)
        self.assertEqual(tree_paths(home), set())
        # Anchor dirs that only ever held pack files are pruned too.
        self.assertFalse((home / ".claude").exists())

    def test_drifted_file_preserved_without_force(self) -> None:
        home = self.installed_home()
        drifted = home / ".claude/skills/se-brief/SKILL.md"
        drifted.write_text("edited by user\n", encoding="utf-8")
        result = install_ok("--root", str(home), "--remove")
        self.assertIn("content differs from installed pack version", result.stdout)
        self.assertTrue(drifted.is_file())
        self.assertEqual(
            tree_paths(home), {".claude/skills/se-brief/SKILL.md"}
        )

    def test_force_removes_drifted_file(self) -> None:
        home = self.installed_home()
        drifted = home / ".claude/skills/se-brief/SKILL.md"
        drifted.write_text("edited by user\n", encoding="utf-8")
        install_ok("--root", str(home), "--remove", "--force")
        self.assertEqual(tree_paths(home), set())

    def test_dry_run_deletes_nothing(self) -> None:
        home = self.installed_home()
        before = tree_paths(home)
        result = install_ok("--root", str(home), "--remove", "--dry-run")
        self.assertIn("would-remove", result.stdout)
        self.assertEqual(tree_paths(home), before)

    def test_unrecognized_receipt_entry_ignored(self) -> None:
        home = self.installed_home()
        receipt = home / RECEIPT_FILE
        stray = home / "Documents/keep-me.txt"
        stray.parent.mkdir(parents=True)
        stray.write_text("precious\n", encoding="utf-8")
        receipt.write_text(
            receipt.read_text(encoding="utf-8") + "Documents/keep-me.txt\n",
            encoding="utf-8",
        )
        result = install_ok("--root", str(home), "--remove")
        self.assertIn("not a recognized se-ai-command-pack target", result.stdout)
        self.assertTrue(stray.is_file())

    def test_git_internals_refused_even_when_listed(self) -> None:
        home = self.installed_home()
        git_file = home / ".git/config"
        git_file.parent.mkdir(parents=True)
        git_file.write_text("[core]\n", encoding="utf-8")
        receipt = home / RECEIPT_FILE
        receipt.write_text(
            receipt.read_text(encoding="utf-8") + ".git/config\n",
            encoding="utf-8",
        )
        result = install_ok("--root", str(home), "--remove", "--force")
        self.assertIn("refusing to remove .git internals", result.stdout)
        self.assertTrue(git_file.is_file())

    def test_remove_works_from_provenance_when_receipt_missing(self) -> None:
        home = self.installed_home()
        (home / RECEIPT_FILE).unlink()
        install_ok("--root", str(home), "--remove")
        self.assertEqual(tree_paths(home), set())

    def test_remove_after_partial_install(self) -> None:
        home = make_home(self.base, anchors=("codex",))
        install_ok("--root", str(home))
        install_ok("--root", str(home), "--remove")
        self.assertEqual(tree_paths(home), set())

    def test_backup_on_remove_keeps_bak_copies(self) -> None:
        home = self.installed_home()
        result = install_ok("--root", str(home), "--remove", "--backup")
        self.assertIn("removed", result.stdout)
        remaining = tree_paths(home)
        self.assertTrue(remaining)
        self.assertTrue(
            all(".bak" in path for path in remaining), sorted(remaining)[:5]
        )

    def test_remove_missing_install_reports_missing(self) -> None:
        home = make_home(self.base)
        result = install_ok("--root", str(home), "--remove")
        self.assertIn("missing", result.stdout)
        self.assertEqual(tree_paths(home), set())

    def test_symlinked_target_preserved_without_force(self) -> None:
        home = self.installed_home()
        target = home / ".claude/skills/se-brief/SKILL.md"
        real = home / "real.md"
        real.write_bytes(target.read_bytes())
        target.unlink()
        target.symlink_to(real)
        result = run_installer("--root", str(home), "--remove")
        self.assertEqual(result.returncode, 0)
        self.assertIn("target is a symlink", result.stdout)
        self.assertTrue(target.is_symlink())


if __name__ == "__main__":
    unittest.main()

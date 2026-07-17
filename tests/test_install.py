"""End-to-end installer tests: subprocess runs against temporary roots."""

from __future__ import annotations

import json
import unittest

from install_test_support import (
    PACK_ROOT,
    TempDirTestCase,
    install_ok,
    make_home,
    read_provenance,
    read_receipt_targets,
    run_installer,
    tree_paths,
)

from installer.registry import PLATFORM_REGISTRY, SKILL_NAMES

MANIFEST = json.loads((PACK_ROOT / "manifest.json").read_text(encoding="utf-8"))
ALL_TARGETS = {row["target"] for row in MANIFEST["files"]}
RECEIPTS = {
    ".se-ai-command-pack/manifest.json",
    ".se-ai-command-pack/provenance.json",
    ".se-ai-command-pack/installed-targets.txt",
}


class FreshInstallTest(TempDirTestCase):
    def test_all_anchors_full_install(self) -> None:
        home = make_home(self.base)
        result = install_ok("--root", str(home))
        self.assertIn("created", result.stdout)
        self.assertEqual(tree_paths(home), ALL_TARGETS | RECEIPTS)
        self.assertEqual(read_receipt_targets(home), ALL_TARGETS | RECEIPTS)
        provenance = read_provenance(home)
        self.assertEqual(provenance["version"], MANIFEST["version"])
        self.assertEqual(provenance["sourceRoot"], str(PACK_ROOT))
        self.assertEqual(set(provenance["files"]), ALL_TARGETS)

    def test_refresh_is_idempotent(self) -> None:
        home = make_home(self.base)
        install_ok("--root", str(home))
        before = tree_paths(home)
        result = install_ok("--root", str(home))
        self.assertNotIn("created", result.stdout)
        self.assertNotIn("overwritten", result.stdout)
        self.assertIn("unchanged", result.stdout)
        self.assertEqual(tree_paths(home), before)

    def test_missing_anchor_skips_with_hint(self) -> None:
        home = make_home(self.base, anchors=("claude",))
        result = install_ok("--root", str(home))
        self.assertIn("anchor .codex not present", result.stdout)
        self.assertIn("hint: .codex/ not found", result.stdout)
        installed = tree_paths(home)
        self.assertFalse(
            {path for path in installed if path.startswith(".codex/")}
        )
        self.assertTrue(
            {path for path in installed if path.startswith(".claude/")}
        )

    def test_platform_filter_installs_one_platform(self) -> None:
        home = make_home(self.base, anchors=())
        install_ok("--root", str(home), "--platform", "codex")
        installed = tree_paths(home) - RECEIPTS
        self.assertTrue(installed)
        self.assertTrue(
            all(path.startswith(".codex/") for path in installed),
            sorted(installed),
        )

    def test_all_flag_creates_missing_anchors(self) -> None:
        home = make_home(self.base, anchors=())
        install_ok("--root", str(home), "--all")
        self.assertEqual(tree_paths(home), ALL_TARGETS | RECEIPTS)

    def test_every_skill_lands_on_every_platform(self) -> None:
        home = make_home(self.base)
        install_ok("--root", str(home))
        for name in SKILL_NAMES:
            for info in PLATFORM_REGISTRY.values():
                self.assertTrue(
                    (home / info.skills_dir / name / "SKILL.md").is_file(),
                    f"{info.skills_dir}/{name}",
                )


class ConflictTest(TempDirTestCase):
    def test_conflict_exits_2_and_writes_nothing(self) -> None:
        home = make_home(self.base)
        conflicting = home / ".claude/skills/se-research/SKILL.md"
        conflicting.parent.mkdir(parents=True)
        conflicting.write_text("mine\n", encoding="utf-8")
        result = run_installer("--root", str(home))
        self.assertEqual(result.returncode, 2)
        self.assertIn("Conflicts:", result.stdout)
        self.assertIn("--force", result.stdout)
        # Plan-before-apply: nothing else was written either.
        self.assertEqual(tree_paths(home), {".claude/skills/se-research/SKILL.md"})
        self.assertEqual(conflicting.read_text(encoding="utf-8"), "mine\n")

    def test_force_overwrites_and_backup_keeps_copy(self) -> None:
        home = make_home(self.base)
        conflicting = home / ".claude/skills/se-research/SKILL.md"
        conflicting.parent.mkdir(parents=True)
        conflicting.write_text("mine\n", encoding="utf-8")
        result = install_ok("--root", str(home), "--force", "--backup")
        self.assertIn("overwritten", result.stdout)
        backup = home / ".claude/skills/se-research/SKILL.md.bak"
        self.assertEqual(backup.read_text(encoding="utf-8"), "mine\n")
        template = PACK_ROOT / "templates/skills/se-research/SKILL.md"
        self.assertEqual(conflicting.read_bytes(), template.read_bytes())


class ModesAndFlagsTest(TempDirTestCase):
    def test_dry_run_writes_nothing(self) -> None:
        home = make_home(self.base)
        result = install_ok("--root", str(home), "--dry-run")
        self.assertIn("mode: dry-run", result.stdout)
        self.assertIn("created", result.stdout)
        self.assertEqual(tree_paths(home), set())

    def test_version_prints_identity(self) -> None:
        result = install_ok("--version")
        self.assertEqual(
            result.stdout.strip(),
            f"se-ai-command-pack {MANIFEST['version']}",
        )

    def test_missing_root_errors(self) -> None:
        result = run_installer("--root", str(self.base / "nope"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("install root not found", result.stderr)

    def test_pack_checkout_root_refused(self) -> None:
        result = run_installer("--root", str(PACK_ROOT))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pack source checkout", result.stderr)

    def test_backup_requires_force_or_remove(self) -> None:
        result = run_installer("--root", str(self.base), "--backup")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--backup requires --force", result.stderr)

    def test_root_and_user_are_exclusive(self) -> None:
        result = run_installer("--root", str(self.base), "--user")
        self.assertNotEqual(result.returncode, 0)


class FilteredRefreshReceiptTest(TempDirTestCase):
    def test_platform_filtered_refresh_keeps_other_entries(self) -> None:
        home = make_home(self.base)
        install_ok("--root", str(home))
        result = install_ok("--root", str(home), "--platform", "claude")
        self.assertIn("kept-in-receipt", result.stdout)
        targets = read_receipt_targets(home)
        codex_entries = {t for t in targets if t.startswith(".codex/")}
        self.assertTrue(codex_entries, "codex entries dropped from receipt")
        provenance = read_provenance(home)
        self.assertTrue(
            {t for t in provenance["files"] if t.startswith(".codex/")},
            "codex entries dropped from provenance",
        )


if __name__ == "__main__":
    unittest.main()

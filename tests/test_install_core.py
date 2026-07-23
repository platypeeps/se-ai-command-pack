"""Unit tests for manifest loading/validation and core file operations."""

from __future__ import annotations

import argparse
import json
import os
import unittest
from pathlib import Path
from unittest import mock

from install_test_support import PACK_ROOT, TempDirTestCase

import install as install_module
from installer import fileops, manifest
from installer.fileops import (
    InstallResult,
    install_file,
    next_backup_path,
    path_is_occupied,
    planned_result_matches_destination,
    prune_empty_parent_dirs,
    selected_files,
    source_digest,
)
from installer.manifest import (
    PackFile,
    load_manifest,
    validate_manifest,
    validate_relative_manifest_path,
)
from installer.registry import (
    ALWAYS_INSTALL,
    IF_ANCHOR_EXISTS,
    IF_NOT_EXISTS,
    ROOT,
    USER_SCOPE,
)
from installer.status import InstallStatus

REAL_TEMPLATE = ROOT / "templates/skills/se-research/SKILL.md"


def pack_file(
    *,
    platform: str = "claude",
    kind: str = "skill",
    scope: str = USER_SCOPE,
    source: Path | None = REAL_TEMPLATE,
    target: str = ".claude/skills/se-research/SKILL.md",
    anchor: str | None = ".claude",
    install: str = IF_ANCHOR_EXISTS,
) -> PackFile:
    return PackFile(
        platform=platform,
        kind=kind,
        scope=scope,
        source=source,
        target=Path(target),
        anchor=Path(anchor) if anchor else None,
        install=install,
    )


class LoadManifestTest(TempDirTestCase):
    def load_with_content(self, content: str):
        path = self.base / "manifest.json"
        path.write_text(content, encoding="utf-8")
        with mock.patch.object(manifest, "MANIFEST_PATH", path):
            return load_manifest()

    def assert_load_error(self, content: str, fragment: str) -> None:
        with self.assertRaises(SystemExit) as caught:
            self.load_with_content(content)
        self.assertIn(fragment, str(caught.exception))

    def test_invalid_json(self) -> None:
        self.assert_load_error("{not json", "not valid JSON")

    def test_non_object_manifest(self) -> None:
        self.assert_load_error("[]", "must be a JSON object")

    def test_boolean_schema_version(self) -> None:
        self.assert_load_error(
            json.dumps({"schemaVersion": True}), "must be an integer"
        )

    def test_newer_schema_version(self) -> None:
        self.assert_load_error(
            json.dumps({"schemaVersion": 99}), "newer than this installer supports"
        )

    def test_files_not_array(self) -> None:
        self.assert_load_error(json.dumps({"files": {}}), "must be an array")

    def test_missing_required_field(self) -> None:
        self.assert_load_error(
            json.dumps({"files": [{"platform": "claude"}]}),
            "missing required field",
        )

    def test_non_object_file_entry(self) -> None:
        self.assert_load_error(
            json.dumps({"files": ["nope"]}),
            "must be an object",
        )

    def test_defaults_applied(self) -> None:
        raw, files = self.load_with_content(
            json.dumps(
                {
                    "files": [
                        {
                            "platform": "claude",
                            "kind": "skill",
                            "source": "templates/skills/se-research/SKILL.md",
                            "target": ".claude/skills/se-research/SKILL.md",
                        }
                    ]
                }
            )
        )
        self.assertEqual(files[0].scope, USER_SCOPE)
        self.assertEqual(files[0].install, IF_ANCHOR_EXISTS)
        self.assertIsNone(files[0].anchor)

    def test_real_manifest_loads_and_validates(self) -> None:
        raw, files = load_manifest()
        self.assertEqual(raw["name"], "se-ai-command-pack")
        self.assertGreater(len(files), 0)
        validate_manifest(files)


class ValidateManifestTest(unittest.TestCase):
    def assert_invalid(self, file: PackFile, fragment: str) -> None:
        with self.assertRaises(SystemExit) as caught:
            validate_manifest([file])
        self.assertIn(fragment, str(caught.exception))

    def test_unknown_platform(self) -> None:
        self.assert_invalid(pack_file(platform="nope"), "unknown platform")

    def test_unknown_kind(self) -> None:
        self.assert_invalid(pack_file(kind="nope"), "unknown kind")

    def test_unknown_scope(self) -> None:
        self.assert_invalid(pack_file(scope="galactic"), "unknown scope")

    def test_unknown_install_mode(self) -> None:
        self.assert_invalid(pack_file(install="sometimes"), "unknown install mode")

    def test_missing_source(self) -> None:
        self.assert_invalid(pack_file(source=None), "has no source")

    def test_source_outside_pack(self) -> None:
        self.assert_invalid(
            pack_file(source=ROOT.parent / "outside.md"), "unsafe source path"
        )

    def test_missing_template(self) -> None:
        self.assert_invalid(
            pack_file(source=ROOT / "templates/skills/nope/SKILL.md"),
            "missing pack template",
        )

    def test_absolute_target(self) -> None:
        self.assert_invalid(pack_file(target="/etc/passwd"), "unsafe target path")

    def test_parent_traversal_target(self) -> None:
        self.assert_invalid(
            pack_file(target="../escape.md"), "unsafe target path"
        )

    def test_windows_drive_target(self) -> None:
        self.assert_invalid(
            pack_file(target="C:/windows/escape.md"), "unsafe target path"
        )

    def test_unsafe_anchor(self) -> None:
        self.assert_invalid(pack_file(anchor="../up"), "unsafe anchor path")

    def test_duplicate_target(self) -> None:
        with self.assertRaises(SystemExit) as caught:
            validate_manifest([pack_file(), pack_file()])
        self.assertIn("duplicate target", str(caught.exception))

    def test_valid_entry_passes(self) -> None:
        validate_manifest([pack_file()])


class RelativePathValidationTest(unittest.TestCase):
    def test_accepts_plain_relative(self) -> None:
        validate_relative_manifest_path("target", Path(".claude/skills/x.md"))

    def test_rejects_windows_root(self) -> None:
        with self.assertRaises(SystemExit):
            validate_relative_manifest_path("target", Path("\\windows\\path"))

    def test_rejects_embedded_parent_parts(self) -> None:
        with self.assertRaises(SystemExit):
            validate_relative_manifest_path("target", Path("a/../../b"))


class SelectedFilesTest(TempDirTestCase):
    def test_anchor_gating(self) -> None:
        (self.base / ".claude").mkdir()
        claude = pack_file()
        codex = pack_file(
            platform="codex",
            target=".codex/skills/se-research/SKILL.md",
            anchor=".codex",
        )
        selected, skipped = selected_files([claude, codex], self.base, None, False)
        self.assertEqual(selected, [claude])
        self.assertEqual(len(skipped), 1)
        self.assertIn("anchor .codex not present", skipped[0][1])

    def test_platform_filter_overrides_anchor(self) -> None:
        codex = pack_file(
            platform="codex",
            target=".codex/skills/se-research/SKILL.md",
            anchor=".codex",
        )
        selected, skipped = selected_files([codex], self.base, ["codex"], False)
        self.assertEqual(selected, [codex])
        self.assertEqual(skipped, [])

    def test_platform_filter_skips_others(self) -> None:
        (self.base / ".claude").mkdir()
        claude = pack_file()
        selected, skipped = selected_files([claude], self.base, ["codex"], False)
        self.assertEqual(selected, [])
        self.assertEqual(skipped[0][1], "platform not selected")

    def test_install_all_overrides_anchor(self) -> None:
        codex = pack_file(
            platform="codex",
            target=".codex/skills/se-research/SKILL.md",
            anchor=".codex",
        )
        selected, skipped = selected_files([codex], self.base, None, True)
        self.assertEqual(selected, [codex])

    def test_always_and_if_not_exists_are_selected(self) -> None:
        always = pack_file(install=ALWAYS_INSTALL, anchor=None)
        preserve = pack_file(
            install=IF_NOT_EXISTS,
            target=".claude/other.md",
            anchor=None,
        )
        selected, skipped = selected_files(
            [always, preserve], self.base, None, False
        )
        self.assertEqual(selected, [always, preserve])

    def test_unknown_mode_raises(self) -> None:
        broken = pack_file(install="sometimes")
        with self.assertRaises(SystemExit):
            selected_files([broken], self.base, None, False)


class InstallFileTest(TempDirTestCase):
    def install(self, file: PackFile, **kwargs) -> InstallResult:
        defaults = {"force": False, "dry_run": False, "backup": False}
        defaults.update(kwargs)
        return install_file(file, self.base, **defaults)

    def destination(self, file: PackFile) -> Path:
        return self.base / file.target

    def test_created(self) -> None:
        file = pack_file()
        result = self.install(file)
        self.assertIs(result.status, InstallStatus.CREATED)
        self.assertEqual(
            self.destination(file).read_bytes(), REAL_TEMPLATE.read_bytes()
        )

    def test_unchanged(self) -> None:
        file = pack_file()
        self.install(file)
        result = self.install(file)
        self.assertIs(result.status, InstallStatus.UNCHANGED)

    def test_conflict_leaves_content(self) -> None:
        file = pack_file()
        destination = self.destination(file)
        destination.parent.mkdir(parents=True)
        destination.write_text("user content\n", encoding="utf-8")
        result = self.install(file)
        self.assertIs(result.status, InstallStatus.CONFLICT)
        self.assertEqual(destination.read_text(encoding="utf-8"), "user content\n")

    def test_vouched_prior_payload_updates_without_force(self) -> None:
        file = pack_file()
        destination = self.destination(file)
        destination.parent.mkdir(parents=True)
        prior_content = b"prior installer content\n"
        destination.write_bytes(prior_content)

        result = self.install(
            file,
            vouched_digest=f"sha256:{source_digest(prior_content)}",
        )

        self.assertIs(result.status, InstallStatus.UPDATED)
        self.assertEqual(destination.read_bytes(), REAL_TEMPLATE.read_bytes())
        self.assertEqual(result.destination_digest, source_digest(prior_content))

    def test_if_not_exists_remains_preserved_when_vouched(self) -> None:
        file = pack_file(install=IF_NOT_EXISTS)
        destination = self.destination(file)
        destination.parent.mkdir(parents=True)
        prior_content = b"prior installer content\n"
        destination.write_bytes(prior_content)

        result = self.install(
            file,
            vouched_digest=f"sha256:{source_digest(prior_content)}",
        )

        self.assertIs(result.status, InstallStatus.PRESERVED)
        self.assertEqual(destination.read_bytes(), prior_content)

    def test_force_overwrites_with_backup(self) -> None:
        file = pack_file()
        destination = self.destination(file)
        destination.parent.mkdir(parents=True)
        destination.write_text("user content\n", encoding="utf-8")
        result = self.install(file, force=True, backup=True)
        self.assertIs(result.status, InstallStatus.OVERWRITTEN)
        assert result.backup is not None
        self.assertEqual(
            result.backup.read_text(encoding="utf-8"), "user content\n"
        )
        self.assertEqual(destination.read_bytes(), REAL_TEMPLATE.read_bytes())

    def test_symlink_conflict(self) -> None:
        file = pack_file()
        destination = self.destination(file)
        destination.parent.mkdir(parents=True)
        linked = self.base / "elsewhere.md"
        linked.write_bytes(REAL_TEMPLATE.read_bytes())
        destination.symlink_to(linked)
        result = self.install(file)
        self.assertIs(result.status, InstallStatus.SYMLINK_CONFLICT)

    def test_if_not_exists_preserves(self) -> None:
        file = pack_file(install=IF_NOT_EXISTS)
        destination = self.destination(file)
        destination.parent.mkdir(parents=True)
        destination.write_text("user content\n", encoding="utf-8")
        result = self.install(file, force=True)
        self.assertIs(result.status, InstallStatus.PRESERVED)
        self.assertEqual(destination.read_text(encoding="utf-8"), "user content\n")

    def test_dry_run_writes_nothing(self) -> None:
        file = pack_file()
        result = self.install(file, dry_run=True)
        self.assertIs(result.status, InstallStatus.CREATED)
        self.assertFalse(path_is_occupied(self.destination(file)))

    def test_directory_at_target_fails_cleanly(self) -> None:
        file = pack_file()
        self.destination(file).mkdir(parents=True)
        with self.assertRaises(SystemExit) as caught:
            self.install(file)
        self.assertIn("not a file", str(caught.exception))

    def test_executable_bit_propagates(self) -> None:
        source = self.base / "tool.sh"
        source.write_text("#!/bin/sh\n", encoding="utf-8")
        source.chmod(0o755)
        file = pack_file(source=source, target=".claude/tool.sh")
        self.install(file)
        mode = (self.base / file.target).stat().st_mode
        self.assertTrue(mode & 0o111)

    def test_planned_created_reused_without_source_read(self) -> None:
        file = pack_file()
        planned = InstallResult(
            file,
            InstallStatus.CREATED,
            source_digest="0" * 64,
            source_content=b"planned content\n",
            source_executable=False,
        )
        result = self.install(file, planned_result=planned)
        self.assertIs(result.status, InstallStatus.CREATED)
        self.assertEqual(
            self.destination(file).read_bytes(), b"planned content\n"
        )

    def test_stale_planned_result_recomputes(self) -> None:
        file = pack_file()
        destination = self.destination(file)
        destination.parent.mkdir(parents=True)
        destination.write_text("appeared meanwhile\n", encoding="utf-8")
        planned = InstallResult(
            file,
            InstallStatus.CREATED,
            source_digest="0" * 64,
            source_content=b"planned content\n",
            source_executable=False,
        )
        result = self.install(file, planned_result=planned)
        self.assertIs(result.status, InstallStatus.CONFLICT)
        self.assertEqual(
            destination.read_text(encoding="utf-8"), "appeared meanwhile\n"
        )

    def test_stale_planned_update_preserves_concurrent_edit(self) -> None:
        file = pack_file()
        destination = self.destination(file)
        destination.parent.mkdir(parents=True)
        prior_content = b"prior installer content\n"
        destination.write_bytes(prior_content)
        vouched_digest = f"sha256:{source_digest(prior_content)}"
        planned = self.install(
            file,
            dry_run=True,
            vouched_digest=vouched_digest,
        )
        self.assertIs(planned.status, InstallStatus.UPDATED)

        destination.write_text("user edit after preflight\n", encoding="utf-8")
        result = self.install(
            file,
            planned_result=planned,
            vouched_digest=vouched_digest,
        )

        self.assertIs(result.status, InstallStatus.CONFLICT)
        self.assertEqual(
            destination.read_text(encoding="utf-8"),
            "user edit after preflight\n",
        )


class FileopsHelpersTest(TempDirTestCase):
    def test_next_backup_path_increments(self) -> None:
        destination = self.base / "file.md"
        destination.write_text("x", encoding="utf-8")
        first = next_backup_path(self.base, destination)
        self.assertEqual(first.name, "file.md.bak")
        first.write_text("x", encoding="utf-8")
        second = next_backup_path(self.base, destination)
        self.assertEqual(second.name, "file.md.bak1")

    def test_planned_result_matcher(self) -> None:
        destination = self.base / "file.md"
        self.assertTrue(
            planned_result_matches_destination(
                destination, InstallStatus.CREATED, b"x"
            )
        )
        destination.write_bytes(b"x")
        self.assertFalse(
            planned_result_matches_destination(
                destination, InstallStatus.CREATED, b"x"
            )
        )
        self.assertTrue(
            planned_result_matches_destination(
                destination, InstallStatus.UNCHANGED, b"x"
            )
        )
        self.assertFalse(
            planned_result_matches_destination(
                destination, InstallStatus.UNCHANGED, b"y"
            )
        )
        current_digest = source_digest(b"x")
        self.assertTrue(
            planned_result_matches_destination(
                destination,
                InstallStatus.UPDATED,
                b"new",
                current_digest,
            )
        )
        self.assertFalse(
            planned_result_matches_destination(
                destination,
                InstallStatus.UPDATED,
                b"new",
                source_digest(b"other"),
            )
        )

    def test_prune_stops_at_occupied_dir(self) -> None:
        keeper = self.base / "keep" / "note.txt"
        keeper.parent.mkdir(parents=True)
        keeper.write_text("x", encoding="utf-8")
        removed = self.base / "keep" / "deep" / "deeper" / "file.md"
        removed.parent.mkdir(parents=True)
        removed.write_text("x", encoding="utf-8")
        removed.unlink()
        prune_empty_parent_dirs(self.base, removed)
        self.assertFalse((self.base / "keep" / "deep").exists())
        self.assertTrue(keeper.exists())

    def test_atomic_write_sets_mode(self) -> None:
        destination = self.base / "plain.txt"
        fileops.atomic_write_bytes(destination, b"content")
        self.assertEqual(destination.read_bytes(), b"content")
        umask = os.umask(0)
        os.umask(umask)
        self.assertEqual(
            destination.stat().st_mode & 0o777, 0o666 & ~umask
        )


class ResolveInstallRootTest(unittest.TestCase):
    def namespace(self, **kwargs) -> argparse.Namespace:
        defaults = {"root": None, "user": False}
        defaults.update(kwargs)
        return argparse.Namespace(**defaults)

    def test_defaults_to_home(self) -> None:
        root = install_module.resolve_install_root(self.namespace())
        self.assertEqual(root, Path.home().resolve())

    def test_user_flag_is_home(self) -> None:
        root = install_module.resolve_install_root(self.namespace(user=True))
        self.assertEqual(root, Path.home().resolve())

    def test_refuses_pack_checkout(self) -> None:
        with self.assertRaises(SystemExit) as caught:
            install_module.resolve_install_root(
                self.namespace(root=str(PACK_ROOT))
            )
        self.assertIn("pack source checkout", str(caught.exception))

    def test_refuses_paths_inside_checkout(self) -> None:
        with self.assertRaises(SystemExit):
            install_module.resolve_install_root(
                self.namespace(root=str(PACK_ROOT / "templates"))
            )


if __name__ == "__main__":
    unittest.main()

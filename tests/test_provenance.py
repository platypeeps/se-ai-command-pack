"""Unit tests for install receipts: provenance content and coverage."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from install_test_support import TempDirTestCase
from test_install_core import pack_file

from installer.fileops import InstallResult
from installer.provenance import (
    installed_targets_content,
    installed_targets_set,
    never_vouched_targets,
    preserved_receipt_targets,
    provenance_content,
    read_existing_installed_targets,
    read_existing_provenance_files,
)
from installer.registry import (
    INSTALLED_TARGETS_FILE,
    PACK_MANIFEST_FILE,
    PROVENANCE_FILE,
    ROOT,
)
from installer.status import InstallStatus

MANIFEST_HEADER = {"name": "se-ai-command-pack", "version": "9.9.9"}


def result(file, status: InstallStatus) -> InstallResult:
    content = b"content\n"
    return InstallResult(
        file,
        status,
        source_digest=hashlib.sha256(content).hexdigest(),
        source_content=content,
        source_executable=False,
    )


class InstalledTargetsTest(unittest.TestCase):
    def test_set_includes_receipt_and_extras(self) -> None:
        file = pack_file()
        targets = installed_targets_set([file], extra_targets=[PROVENANCE_FILE])
        self.assertIn(file.target.as_posix(), targets)
        self.assertIn(PROVENANCE_FILE.as_posix(), targets)
        self.assertIn(INSTALLED_TARGETS_FILE.as_posix(), targets)

    def test_content_is_sorted_with_trailing_newline(self) -> None:
        file = pack_file()
        content = installed_targets_content([file])
        lines = content.splitlines()
        self.assertEqual(lines, sorted(lines))
        self.assertTrue(content.endswith("\n"))


class NeverVouchedTest(unittest.TestCase):
    def test_receipts_are_never_vouched(self) -> None:
        never = never_vouched_targets()
        self.assertIn(INSTALLED_TARGETS_FILE.as_posix(), never)
        self.assertIn(PACK_MANIFEST_FILE.as_posix(), never)
        self.assertIn(PROVENANCE_FILE.as_posix(), never)


class ProvenanceContentTest(unittest.TestCase):
    def parse(self, results, existing=None, receipt_targets=None):
        receipt = receipt_targets
        if receipt is None:
            receipt = {result.file.target.as_posix() for result in results}
        return json.loads(
            provenance_content(
                MANIFEST_HEADER,
                results,
                existing_files=existing or {},
                receipt_targets=receipt,
                never_vouched=never_vouched_targets(),
            )
        )

    def test_vouchable_statuses_recorded(self) -> None:
        file = pack_file()
        payload = self.parse([result(file, InstallStatus.CREATED)])
        digest = "sha256:" + hashlib.sha256(b"content\n").hexdigest()
        self.assertEqual(payload["files"][file.target.as_posix()], digest)
        self.assertEqual(payload["pack"], "se-ai-command-pack")
        self.assertEqual(payload["version"], "9.9.9")

    def test_source_root_recorded(self) -> None:
        payload = self.parse([result(pack_file(), InstallStatus.UNCHANGED)])
        self.assertEqual(payload["sourceRoot"], str(ROOT))

    def test_preserved_and_conflict_not_vouched(self) -> None:
        file = pack_file()
        payload = self.parse(
            [
                result(file, InstallStatus.PRESERVED),
                result(file, InstallStatus.CONFLICT),
            ]
        )
        self.assertEqual(payload["files"], {})

    def test_merge_keeps_receipt_covered_entries(self) -> None:
        file = pack_file()
        existing = {
            file.target.as_posix(): "sha256:old",
            ".codex/skills/gone/SKILL.md": "sha256:dropped",
        }
        payload = self.parse(
            [],
            existing=existing,
            receipt_targets={file.target.as_posix()},
        )
        self.assertEqual(
            payload["files"], {file.target.as_posix(): "sha256:old"}
        )

    def test_hand_edited_receipt_vouch_is_scrubbed(self) -> None:
        existing = {PROVENANCE_FILE.as_posix(): "sha256:forged"}
        payload = self.parse(
            [],
            existing=existing,
            receipt_targets={PROVENANCE_FILE.as_posix()},
        )
        self.assertEqual(payload["files"], {})

    def test_digest_fallback_reads_source(self) -> None:
        file = pack_file()
        bare = InstallResult(file, InstallStatus.UNCHANGED)
        payload = self.parse([bare])
        assert file.source is not None
        expected = "sha256:" + hashlib.sha256(file.source.read_bytes()).hexdigest()
        self.assertEqual(payload["files"][file.target.as_posix()], expected)


class ReadReceiptsTest(TempDirTestCase):
    def test_missing_provenance_is_empty(self) -> None:
        self.assertEqual(read_existing_provenance_files(self.base), {})

    def test_invalid_provenance_is_empty(self) -> None:
        path = self.base / PROVENANCE_FILE
        path.parent.mkdir(parents=True)
        path.write_text("{broken", encoding="utf-8")
        self.assertEqual(read_existing_provenance_files(self.base), {})

    def test_non_string_entries_filtered(self) -> None:
        path = self.base / PROVENANCE_FILE
        path.parent.mkdir(parents=True)
        path.write_text(
            json.dumps({"files": {"a": "sha256:x", "b": 7}}), encoding="utf-8"
        )
        self.assertEqual(
            read_existing_provenance_files(self.base), {"a": "sha256:x"}
        )

    def test_symlinked_provenance_untrusted(self) -> None:
        real = self.base / "real.json"
        real.write_text(json.dumps({"files": {"a": "sha256:x"}}), encoding="utf-8")
        path = self.base / PROVENANCE_FILE
        path.parent.mkdir(parents=True)
        path.symlink_to(real)
        self.assertEqual(read_existing_provenance_files(self.base), {})

    def test_installed_targets_skips_comments_and_blanks(self) -> None:
        path = self.base / INSTALLED_TARGETS_FILE
        path.parent.mkdir(parents=True)
        path.write_text("# note\n\n.claude/skills/x.md\n", encoding="utf-8")
        self.assertEqual(
            read_existing_installed_targets(self.base), {".claude/skills/x.md"}
        )

    def test_missing_installed_targets_is_empty(self) -> None:
        self.assertEqual(read_existing_installed_targets(self.base), set())


class PreservedReceiptTargetsTest(unittest.TestCase):
    def test_keeps_only_previously_receipted_skips(self) -> None:
        skipped_known = pack_file(
            platform="codex",
            target=".codex/skills/se-research/SKILL.md",
            anchor=".codex",
        )
        skipped_unknown = pack_file(
            platform="agents",
            target=".config/agents/skills/se-research/SKILL.md",
            anchor=".config/agents",
        )
        existing = {skipped_known.target.as_posix()}
        kept = preserved_receipt_targets(
            existing,
            [
                (skipped_known, "platform not selected"),
                (skipped_unknown, "anchor .config/agents not present"),
            ],
        )
        self.assertEqual(kept, [(Path(skipped_known.target), "codex")])


if __name__ == "__main__":
    unittest.main()

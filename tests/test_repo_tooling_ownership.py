"""Repo-own versus vendored ownership contracts for tooling paths.

These tests encode the CONTRIBUTING section "Repo-own source vs vendored
installs". Ownership is decided by the two registries described in
`.trellis/spec/backend/quality-guidelines.md` ("Which registry owns this
file?"), never by directory or filename, so the helpers below implement that
lookup rather than pattern-matching paths.
"""

from __future__ import annotations

import json
import subprocess
import unittest

from install_test_support import PACK_ROOT

SD_MANIFEST = PACK_ROOT / ".sd-ai-command-pack" / "manifest.json"
SD_PROVENANCE = PACK_ROOT / ".sd-ai-command-pack" / "provenance.json"
SD_TARGETS = PACK_ROOT / ".sd-ai-command-pack" / "installed-targets.txt"
TRELLIS_HASHES = PACK_ROOT / ".trellis" / ".template-hashes.json"
TRELLIS_PROVENANCE = PACK_ROOT / ".github" / "trellis-provenance.json"

# The documented home for repo-own tooling. `scripts/` is wholly vendored.
REPO_OWN_HOME = ".github/scripts/"

# Removed as dead code; asserted absent so it cannot return via a receipt.
DELETED_WRAPPER = "scripts/se-ai-command-pack-skill-review.py"

# Written by the installer rather than shipped as payload, so they carry no
# manifest entry and the two-registry lookup cannot classify them.
INSTALLER_RECEIPTS = frozenset(
    {
        ".sd-ai-command-pack/installed-targets.txt",
        ".sd-ai-command-pack/manifest.json",
        ".sd-ai-command-pack/provenance.json",
    }
)


def tracked_files(*paths: str) -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files", "--", *paths] if paths else ["git", "ls-files"],
        cwd=PACK_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in proc.stdout.split("\n") if line]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class OwnershipLookup:
    """The two-registry lookup from the backend quality guidelines."""

    def __init__(self) -> None:
        self.registry_b = {entry["target"]: entry for entry in load_json(SD_MANIFEST)["files"]}
        trellis = load_json(TRELLIS_PROVENANCE)
        self.registry_a = (
            set(load_json(TRELLIS_HASHES)["hashes"])
            | set(trellis["files"])
            | set(trellis["templateReceipted"])
        )

    def classify(self, path: str) -> str:
        in_a = path in self.registry_a
        entry = self.registry_b.get(path)
        if entry is None:
            return "vendored-trellis" if in_a else "repo-own"
        if entry.get("kind") == "managed-block":
            return "dual-owned"
        # An absent `install` key means `if-anchor-exists`, which a refresh
        # overwrites exactly like `always`. Only `if-not-exists` is preserved.
        if entry.get("install", "if-anchor-exists") == "if-not-exists":
            return "repo-own-seeded"
        return "vendored-pack"

    def is_repo_own(self, path: str) -> bool:
        return self.classify(path) in {"repo-own", "repo-own-seeded"}


class ScriptsDirectoryIsWhollyVendoredTest(unittest.TestCase):
    """`scripts/` holds installed pack files only, so no exception is needed."""

    def setUp(self) -> None:
        self.lookup = OwnershipLookup()
        self.tracked = tracked_files("scripts/")

    def test_every_tracked_script_is_pack_vendored(self) -> None:
        self.assertTrue(self.tracked, "expected tracked files under scripts/")
        offenders = {
            path: self.lookup.classify(path)
            for path in self.tracked
            if self.lookup.classify(path) != "vendored-pack"
        }
        self.assertEqual(
            offenders,
            {},
            "repo-own files belong in .github/scripts/, not scripts/ "
            "(see CONTRIBUTING, 'Repo-own source vs vendored installs')",
        )

    def test_receipts_agree_about_the_scripts_directory(self) -> None:
        # The manifest decides ownership; provenance and installed-targets are
        # the content and destination receipts beside it. If they disagree, one
        # of the three is stale and the ownership answer is no longer trustworthy.
        provenance = {p for p in load_json(SD_PROVENANCE)["files"] if p.startswith("scripts/")}
        targets = {
            line.strip()
            for line in SD_TARGETS.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#") and line.strip().startswith("scripts/")
        }
        self.assertEqual(provenance, targets)
        self.assertEqual(provenance, set(self.tracked))

    def test_dead_wrapper_stays_deleted(self) -> None:
        self.assertNotIn(DELETED_WRAPPER, self.tracked)


class RepoOwnHomeIsUniformlyEditableTest(unittest.TestCase):
    """Acceptance criterion 4: every file in the home edits without drift.

    A passing provenance run only shows the current bytes are consistent. What
    makes a path drift-sensitive is membership in the manifest's `files` map,
    which is hash-pinned; `repoOwn` entries are hand-curated and free to change.
    Asserting the classification is therefore stronger than running the gate.
    """

    def setUp(self) -> None:
        self.manifest = load_json(TRELLIS_PROVENANCE)
        self.tracked = tracked_files(REPO_OWN_HOME)

    def test_home_is_populated(self) -> None:
        self.assertTrue(self.tracked, f"expected tracked files under {REPO_OWN_HOME}")

    def test_every_file_is_curated_repo_own_and_not_hash_pinned(self) -> None:
        repo_own = set(self.manifest["repoOwn"])
        hash_pinned = set(self.manifest["files"])
        for path in self.tracked:
            with self.subTest(path=path):
                self.assertIn(
                    path,
                    repo_own,
                    "a new .github file is an `uncovered:` provenance finding "
                    "until it is curated into repoOwn",
                )
                self.assertNotIn(
                    path,
                    hash_pinned,
                    "hash-pinned files report `drifted:` when edited, which "
                    "makes the repo-own home only partly editable",
                )


class DocumentedOwnershipExceptionsTest(unittest.TestCase):
    """The exceptions CONTRIBUTING calls out, pinned so they cannot rot."""

    def setUp(self) -> None:
        self.lookup = OwnershipLookup()

    def test_sd_check_registration_is_repo_own(self) -> None:
        # Guards against a blanket `.sd-ai-command-pack/**` do-not-edit rule:
        # the registration file sits beside the receipts but is authored here.
        self.assertTrue(self.lookup.is_repo_own(".sd-ai-command-pack/check.json"))
        self.assertNotIn(".sd-ai-command-pack/check.json", INSTALLER_RECEIPTS)

    def test_installer_receipts_are_generated_not_authored(self) -> None:
        # The two-registry lookup classifies payload. Installer receipts are a
        # third category: they are listed as installed targets but carry no
        # manifest entry, because the installer writes them rather than
        # shipping them. They are not hand-editable, and the lookup alone
        # cannot say so — hence this explicit assertion.
        targets = {
            line.strip()
            for line in SD_TARGETS.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        }
        for receipt in sorted(INSTALLER_RECEIPTS):
            with self.subTest(receipt=receipt):
                self.assertIn(receipt, targets)
                self.assertNotIn(receipt, self.lookup.registry_b)

    def test_seeded_targets_are_repo_own_after_install(self) -> None:
        seeded = sorted(
            path
            for path, entry in self.lookup.registry_b.items()
            if entry.get("install") == "if-not-exists"
        )
        self.assertEqual(seeded, [".gito/config.toml", ".prism/rules.json"])
        for path in seeded:
            with self.subTest(path=path):
                self.assertEqual(self.lookup.classify(path), "repo-own-seeded")

    def test_copilot_instructions_is_dual_owned(self) -> None:
        self.assertEqual(
            self.lookup.classify(".github/copilot-instructions.md"), "dual-owned"
        )

    def test_repository_specs_and_tasks_are_repo_own(self) -> None:
        for path in (
            ".trellis/spec/backend/quality-guidelines.md",
            "CONTRIBUTING.md",
            "Makefile",
        ):
            with self.subTest(path=path):
                self.assertTrue(self.lookup.is_repo_own(path))


if __name__ == "__main__":
    unittest.main()

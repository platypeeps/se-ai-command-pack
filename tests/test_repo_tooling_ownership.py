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

# Registry A's receipt (`.trellis/.template-hashes.json`) is gitignored, so it
# exists in a working checkout and never on CI. Everything it contributes that
# `.github/trellis-provenance.json` does not already cover falls under these
# four Trellis-runtime paths, which are vendored whether or not the receipt is
# readable. Naming them keeps the lookup's answer identical in both
# environments instead of silently degrading to "repo-own" on CI.
TRELLIS_RUNTIME_PREFIXES = (".trellis/scripts/", ".trellis/agents/")
TRELLIS_RUNTIME_FILES = frozenset({".trellis/config.yaml", ".trellis/workflow.md"})


def is_trellis_runtime(path: str) -> bool:
    return path in TRELLIS_RUNTIME_FILES or path.startswith(TRELLIS_RUNTIME_PREFIXES)


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
        self.registry_a = set(trellis["files"]) | set(trellis["templateReceipted"])
        # The receipt is gitignored; merge it when the checkout has one so a
        # local run exercises the real data, and fall back to the named
        # runtime paths otherwise.
        self.registry_a_receipt_present = TRELLIS_HASHES.exists()
        if self.registry_a_receipt_present:
            self.registry_a |= set(load_json(TRELLIS_HASHES)["hashes"])

    def classify(self, path: str) -> str:
        in_a = path in self.registry_a or is_trellis_runtime(path)
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


class RegistryAIsReadableWithoutItsReceiptTest(unittest.TestCase):
    """The lookup must answer the same way on CI, where the receipt is absent.

    `.trellis/.template-hashes.json` is gitignored, so a checkout has one and a
    runner never does. Without a substitute the vendored Trellis runtime would
    classify as `repo-own` on CI only — the lookup would not crash, it would
    quietly invert its answer for 32 paths.
    """

    def setUp(self) -> None:
        self.lookup = OwnershipLookup()

    def test_receipt_is_not_tracked(self) -> None:
        # If this ever starts failing, the fallback below is dead weight and
        # the receipt can be read directly.
        self.assertEqual(tracked_files(".trellis/.template-hashes.json"), [])

    def test_trellis_runtime_classifies_vendored_without_the_receipt(self) -> None:
        for path in (
            ".trellis/scripts/task.py",
            ".trellis/agents/check.md",
            ".trellis/config.yaml",
            ".trellis/workflow.md",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.lookup.classify(path), "vendored-trellis")

    def test_repo_authored_trellis_paths_are_not_swept_into_the_fallback(self) -> None:
        # The fallback names runtime paths only. Specs and tasks live under the
        # same `.trellis/` root and are authored here.
        for path in (
            ".trellis/spec/backend/quality-guidelines.md",
            ".trellis/tasks/07-25-audit-repo-tooling-ownership/prd.md",
        ):
            with self.subTest(path=path):
                self.assertFalse(is_trellis_runtime(path))
                self.assertTrue(self.lookup.is_repo_own(path))

    def test_fallback_still_covers_the_whole_receipt(self) -> None:
        # Anti-rot, and the only assertion that needs the receipt: a new
        # vendored Trellis runtime file outside the named paths would make the
        # fallback incomplete, and CI alone could not notice.
        if not self.lookup.registry_a_receipt_present:
            self.skipTest("Registry A receipt is gitignored and absent in this checkout")
        tracked_registry_a = set(load_json(TRELLIS_PROVENANCE)["files"]) | set(
            load_json(TRELLIS_PROVENANCE)["templateReceipted"]
        )
        uncovered = sorted(
            path
            for path in load_json(TRELLIS_HASHES)["hashes"]
            if path not in tracked_registry_a
            and path not in self.lookup.registry_b
            and not is_trellis_runtime(path)
        )
        self.assertEqual(
            uncovered,
            [],
            "extend TRELLIS_RUNTIME_PREFIXES/TRELLIS_RUNTIME_FILES: these "
            "vendored paths would classify as repo-own on CI",
        )


if __name__ == "__main__":
    unittest.main()

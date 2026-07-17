"""Install receipts: provenance hashes for vouching and the installed-targets record."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path

from installer.fileops import (
    VOUCHABLE_STATUSES,
    InstallResult,
    InstallStatus,
    atomic_write_text,
    generated_pack_file,
    generated_text_file_status,
)
from installer.manifest import (
    PackFile,
    read_text_strict,
    target_destination,
)
from installer.registry import (
    FORCE_PRESERVED_TARGETS,
    INSTALLED_TARGETS_FILE,
    PACK_MANIFEST_FILE,
    PROVENANCE_FILE,
    ROOT,
)


def installed_targets_set(
    selected: list[PackFile],
    extra_targets: Iterable[Path] = (),
) -> set[str]:
    """Return the set of POSIX target paths the install records as installed.

    Shared by the receipt content and provenance coverage so the "provenance
    coverage == receipt contents" invariant is structural, not coincidental.
    """
    targets = {file.target.as_posix() for file in selected}
    targets.update(target.as_posix() for target in extra_targets)
    targets.add(INSTALLED_TARGETS_FILE.as_posix())
    return targets


def installed_targets_content(
    selected: list[PackFile],
    *,
    extra_targets: Iterable[Path] = (),
) -> str:
    targets = installed_targets_set(selected, extra_targets)
    return "\n".join(sorted(targets)) + "\n"


def read_existing_provenance_files(root: Path) -> dict[str, str]:
    provenance = target_destination(root, PROVENANCE_FILE)
    # A symlinked provenance is never trusted; generated-file installation
    # reports a symlink conflict instead of following or replacing the link.
    if provenance.is_symlink() or not provenance.is_file():
        return {}
    try:
        payload = json.loads(provenance.read_text(encoding="utf-8", errors="strict"))
    except (OSError, UnicodeError, ValueError):
        return {}
    files = payload.get("files") if isinstance(payload, dict) else None
    if not isinstance(files, dict):
        return {}
    return {
        key: value
        for key, value in files.items()
        if isinstance(key, str) and isinstance(value, str)
    }


def read_existing_provenance_files_for_remove(root: Path) -> dict[str, str]:
    try:
        return read_existing_provenance_files(root)
    except SystemExit:
        return {}


def never_vouched_targets() -> set[str]:
    """Targets provenance must never vouch, whatever a prior file claims.

    Force-preserved targets are user-tunable and generated files describe
    the install itself; a hand-edited provenance entry for any of them would
    turn legitimate local content into a false drift failure.
    """
    return {
        *(path.as_posix() for path in FORCE_PRESERVED_TARGETS),
        INSTALLED_TARGETS_FILE.as_posix(),
        PACK_MANIFEST_FILE.as_posix(),
        PROVENANCE_FILE.as_posix(),
    }


def provenance_content(
    manifest: dict,
    results: list[InstallResult],
    *,
    existing_files: dict[str, str],
    receipt_targets: set[str],
    never_vouched: set[str],
) -> str:
    # Entries survive for targets still recorded in the receipt so a
    # filtered or partially-skipped run does not shrink coverage; this
    # run's vouched installs overwrite their entries. Never-vouched
    # targets are dropped from prior content too, so a hand-edited
    # provenance file cannot vouch them in through the merge.
    files = {
        key: value
        for key, value in existing_files.items()
        if key in receipt_targets and key not in never_vouched
    }
    # Prefer the source digest captured during planning/apply. The fallback
    # keeps provenance_content usable in narrow unit tests that construct
    # legacy-style InstallResult objects without source metadata.
    source_digests: dict[Path, str] = {}
    for result in results:
        file = result.file
        # Every status that ends with the target byte-equal to the template
        # is vouchable — including "overwritten" (--force over drifted
        # content). Excluded: "preserved" (user content) and "conflict"
        # (target left untouched).
        if result.status not in VOUCHABLE_STATUSES:
            continue
        if file.target.as_posix() in never_vouched:
            continue
        if result.source_digest is not None:
            files[file.target.as_posix()] = f"sha256:{result.source_digest}"
            continue
        if file.source is None:
            continue
        digest = source_digests.get(file.source)
        if digest is None:
            digest = hashlib.sha256(file.source.read_bytes()).hexdigest()
            source_digests[file.source] = digest
        files[file.target.as_posix()] = f"sha256:{digest}"
    payload = {
        "pack": manifest["name"],
        "version": manifest["version"],
        # Where the pack checkout lives, so the se-pack skill can find it
        # to run updates. Refreshes from a different checkout overwrite it.
        "sourceRoot": str(ROOT),
        "files": dict(sorted(files.items())),
    }
    return json.dumps(payload, indent=2) + "\n"


def _install_generated_text_file(
    file: PackFile,
    root: Path,
    content: str,
    *,
    dry_run: bool,
) -> InstallResult:
    """Write a generated pack file: unchanged / updated / created (dry-run safe)."""
    destination = target_destination(root, file.target)
    status = generated_text_file_status(destination)
    if status is not None:
        return InstallResult(file, status)
    if destination.exists():
        current = read_text_strict(destination, str(file.target))
        if current == content:
            return InstallResult(file, InstallStatus.UNCHANGED)
        if not dry_run:
            atomic_write_text(destination, content)
        return InstallResult(file, InstallStatus.UPDATED)

    if not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(destination, content)
    return InstallResult(file, InstallStatus.CREATED)


def install_provenance_file(
    manifest: dict,
    results: list[InstallResult],
    root: Path,
    *,
    receipt_targets: set[str],
    never_vouched: set[str],
    dry_run: bool,
) -> InstallResult:
    file = generated_pack_file("generated-provenance", PROVENANCE_FILE)
    content = provenance_content(
        manifest,
        results,
        existing_files=read_existing_provenance_files(root),
        receipt_targets=receipt_targets,
        never_vouched=never_vouched,
    )
    return _install_generated_text_file(file, root, content, dry_run=dry_run)


def installed_pack_manifest_content(manifest: dict) -> str:
    return json.dumps(manifest, indent=2) + "\n"


def install_pack_manifest_file(
    manifest: dict,
    root: Path,
    *,
    dry_run: bool,
) -> InstallResult:
    file = generated_pack_file("generated-pack-manifest", PACK_MANIFEST_FILE)
    content = installed_pack_manifest_content(manifest)
    return _install_generated_text_file(file, root, content, dry_run=dry_run)


def read_existing_installed_targets(root: Path) -> set[str]:
    receipt = target_destination(root, INSTALLED_TARGETS_FILE)
    if not receipt.is_file():
        return set()
    try:
        content = receipt.read_text(encoding="utf-8", errors="replace")
    except OSError as error:
        raise SystemExit(
            f"error: cannot read installed-targets receipt {receipt}: {error}"
        ) from None
    entries: set[str] = set()
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#"):
            entries.add(line)
    return entries


def read_existing_installed_targets_for_remove(root: Path) -> set[str]:
    try:
        return read_existing_installed_targets(root)
    except (OSError, SystemExit):
        return set()


def preserved_receipt_targets(
    existing: set[str],
    skipped: list[tuple[PackFile, str]],
) -> list[tuple[Path, str]]:
    """Receipt entries to keep for platforms skipped in this run only.

    A refresh filtered with --platform, or one that skips a platform whose
    anchor is gone, must not drop receipt entries an earlier run installed:
    a later --remove still needs to know about those files.
    """
    preserved: list[tuple[Path, str]] = []
    for file, _reason in skipped:
        if file.target.as_posix() not in existing:
            continue
        preserved.append((file.target, file.platform))
    return preserved


def install_installed_targets_file(
    selected: list[PackFile],
    root: Path,
    *,
    dry_run: bool,
    extra_targets: Iterable[Path] = (),
) -> InstallResult:
    file = generated_pack_file("generated-manifest", INSTALLED_TARGETS_FILE)
    content = installed_targets_content(selected, extra_targets=extra_targets)
    return _install_generated_text_file(file, root, content, dry_run=dry_run)


__all__ = [
    "install_installed_targets_file",
    "install_pack_manifest_file",
    "install_provenance_file",
    "installed_pack_manifest_content",
    "installed_targets_content",
    "installed_targets_set",
    "never_vouched_targets",
    "preserved_receipt_targets",
    "provenance_content",
    "read_existing_installed_targets",
    "read_existing_installed_targets_for_remove",
    "read_existing_provenance_files",
    "read_existing_provenance_files_for_remove",
]

"""Payload file operations: selection, atomic writes, backups, removal helpers."""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from installer.manifest import (
    PackFile,
    target_destination,
    validate_resolved_target_path,
)
from installer.registry import (
    ALWAYS_INSTALL,
    FORCE_PRESERVED_TARGETS,
    IF_ANCHOR_EXISTS,
    IF_NOT_EXISTS,
    USER_SCOPE,
)
from installer.status import (
    CONFLICT_STATUSES,
    VOUCHABLE_STATUSES,
    InstallStatus,
    RemoveStatus,
)


@dataclass(frozen=True)
class InstallResult:
    file: PackFile
    status: InstallStatus
    backup: Path | None = None
    source_digest: str | None = None
    source_content: bytes | None = None
    source_executable: bool | None = None


@dataclass(frozen=True)
class RemoveResult:
    target: Path
    status: RemoveStatus
    backup: Path | None = None
    detail: str | None = None


def generated_pack_file(kind: str, target: Path) -> PackFile:
    """PackFile for an installer-generated file (receipts/manifest/provenance).

    The platform value is inert bookkeeping: generated files never pass
    through manifest validation or platform selection.
    """
    return PackFile(
        platform="pack",
        kind=kind,
        scope=USER_SCOPE,
        source=None,
        target=target,
        anchor=None,
        install=ALWAYS_INSTALL,
    )


def default_file_mode(*, executable: bool = False) -> int:
    current_umask = os.umask(0)
    try:
        base_mode = 0o777 if executable else 0o666
        return base_mode & ~current_umask
    finally:
        os.umask(current_umask)


def source_is_executable(source: Path) -> bool:
    return bool(source.stat().st_mode & 0o111)


def source_digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def atomic_write_bytes(
    destination: Path,
    content: bytes,
    *,
    executable: bool = False,
) -> None:
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
        # NamedTemporaryFile creates 0600 files; installed files should get
        # normal umask-derived modes, executable when the caller requests it
        # (install_file passes the pack source's executable state).
        os.chmod(temporary_path, default_file_mode(executable=executable))
        os.replace(temporary_path, destination)
        temporary_path = None
    except OSError as error:
        raise SystemExit(f"error: cannot write {destination}: {error}") from None
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass


def atomic_write_text(destination: Path, content: str) -> None:
    atomic_write_bytes(destination, content.encode("utf-8"))


def selected_files(
    files: list[PackFile],
    root: Path,
    platforms: list[str] | None,
    install_all: bool,
) -> tuple[list[PackFile], list[tuple[PackFile, str]]]:
    """Split manifest files into (selected, skipped-with-reason) for one run,
    honoring always/if-not-exists policies, the platform filter or --all
    override, and anchor-directory detection."""
    selected: list[PackFile] = []
    skipped: list[tuple[PackFile, str]] = []
    platform_filter = set(platforms or [])

    for file in files:
        if file.install in {ALWAYS_INSTALL, IF_NOT_EXISTS}:
            selected.append(file)
            continue
        if file.install != IF_ANCHOR_EXISTS:
            raise SystemExit(
                f"error: unknown install mode {file.install!r} for {file.target}"
            )
        if platform_filter and file.platform not in platform_filter:
            skipped.append((file, "platform not selected"))
            continue
        if install_all or platform_filter:
            selected.append(file)
            continue
        if file.anchor and not (root / file.anchor).exists():
            skipped.append((file, f"anchor {file.anchor} not present"))
            continue
        selected.append(file)

    return selected, skipped


def path_is_occupied(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def _require_file_destination(destination: Path, relative_target: Path) -> None:
    """Fail cleanly when the target path is occupied by a non-file node."""
    if path_is_occupied(destination) and not destination.is_file():
        raise SystemExit(
            f"error: target exists and is not a file: {relative_target}"
        )


def generated_text_file_status(destination: Path) -> InstallStatus | None:
    """Return the non-writing status for a generated text destination, if any."""
    if destination.is_symlink():
        return InstallStatus.SYMLINK_CONFLICT
    if destination.exists() and not destination.is_file():
        return InstallStatus.CONFLICT
    return None


def next_backup_path(root: Path, destination: Path) -> Path:
    candidate = destination.with_name(f"{destination.name}.bak")
    if not path_is_occupied(candidate):
        validate_resolved_target_path(root, candidate, "backup path")
        return candidate

    index = 1
    while True:
        candidate = destination.with_name(f"{destination.name}.bak{index}")
        if not path_is_occupied(candidate):
            validate_resolved_target_path(root, candidate, "backup path")
            return candidate
        index += 1


def planned_result_matches_destination(
    destination: Path,
    status: InstallStatus,
    new_content: bytes,
) -> bool:
    """Return whether a preflight result is still safe to reuse at apply time."""
    if status is InstallStatus.CREATED:
        return not path_is_occupied(destination)
    if destination.is_symlink():
        return False
    if status is InstallStatus.UNCHANGED:
        return destination.exists() and destination.read_bytes() == new_content
    if status is InstallStatus.PRESERVED:
        return destination.exists()
    return False


def install_file(
    file: PackFile,
    root: Path,
    *,
    force: bool,
    dry_run: bool,
    backup: bool,
    planned_result: InstallResult | None = None,
) -> InstallResult:
    source = file.source
    if source is None:
        raise SystemExit(
            f"error: generated file cannot be installed as a template: {file.target}"
        )
    destination = target_destination(root, file.target)
    _require_file_destination(destination, file.target)
    if (
        planned_result is not None
        and planned_result.file == file
        and planned_result.source_content is not None
        and planned_result.source_executable is not None
        and planned_result.status
        in {
            InstallStatus.CREATED,
            InstallStatus.UNCHANGED,
            InstallStatus.PRESERVED,
        }
    ):
        new_content = planned_result.source_content
        digest = planned_result.source_digest or source_digest(new_content)
        executable = planned_result.source_executable
        if planned_result_matches_destination(
            destination,
            planned_result.status,
            new_content,
        ):
            if planned_result.status is InstallStatus.CREATED:
                if not dry_run:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    atomic_write_bytes(
                        destination,
                        new_content,
                        executable=executable,
                    )
                return InstallResult(
                    file,
                    InstallStatus.CREATED,
                    source_digest=digest,
                    source_content=new_content,
                    source_executable=executable,
                )
            return InstallResult(
                file,
                planned_result.status,
                source_digest=digest,
                source_content=new_content,
                source_executable=executable,
            )

    new_content = source.read_bytes()
    digest = source_digest(new_content)
    executable = source_is_executable(source)
    if destination.is_symlink():
        # Provenance vouches plain regular files only (lstat-based), so a
        # symlinked target must never report "unchanged"/vouchable even when
        # the linked content is identical.
        if file.install == IF_NOT_EXISTS or file.target in FORCE_PRESERVED_TARGETS:
            return InstallResult(
                file,
                InstallStatus.PRESERVED,
                source_digest=digest,
                source_content=new_content,
                source_executable=executable,
            )
        if not force:
            return InstallResult(
                file,
                InstallStatus.SYMLINK_CONFLICT,
                source_digest=digest,
                source_content=new_content,
                source_executable=executable,
            )
        backup_path = None
        if not dry_run:
            backup_path = backup_existing_file(
                root,
                destination,
                backup=backup,
                dry_run=dry_run,
            )
            atomic_write_bytes(destination, new_content, executable=executable)
        return InstallResult(
            file,
            InstallStatus.OVERWRITTEN,
            backup_path,
            source_digest=digest,
            source_content=new_content,
            source_executable=executable,
        )
    if destination.exists():
        current = destination.read_bytes()
        if current == new_content:
            return InstallResult(
                file,
                InstallStatus.UNCHANGED,
                source_digest=digest,
                source_content=new_content,
                source_executable=executable,
            )
        if file.install == IF_NOT_EXISTS or file.target in FORCE_PRESERVED_TARGETS:
            return InstallResult(
                file,
                InstallStatus.PRESERVED,
                source_digest=digest,
                source_content=new_content,
                source_executable=executable,
            )
        if not force:
            return InstallResult(
                file,
                InstallStatus.CONFLICT,
                source_digest=digest,
                source_content=new_content,
                source_executable=executable,
            )
        backup_path = None
        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            backup_path = backup_existing_file(
                root,
                destination,
                backup=backup,
                dry_run=dry_run,
            )
            atomic_write_bytes(destination, new_content, executable=executable)
        return InstallResult(
            file,
            InstallStatus.OVERWRITTEN,
            backup_path,
            source_digest=digest,
            source_content=new_content,
            source_executable=executable,
        )

    if not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_bytes(destination, new_content, executable=executable)
    return InstallResult(
        file,
        InstallStatus.CREATED,
        source_digest=digest,
        source_content=new_content,
        source_executable=executable,
    )


def backup_existing_file(
    root: Path,
    destination: Path,
    *,
    backup: bool,
    dry_run: bool,
) -> Path | None:
    if not backup or dry_run:
        return None
    backup_path = next_backup_path(root, destination)
    try:
        shutil.copyfile(destination, backup_path)
    except OSError as error:
        raise SystemExit(
            f"error: cannot create backup for {display_path(root, destination)}: "
            f"{display_path(root, backup_path)} ({error})"
        ) from None
    return backup_path


def unlink_target_file(root: Path, destination: Path) -> None:
    try:
        destination.unlink()
    except OSError as error:
        raise SystemExit(
            f"error: cannot remove {display_path(root, destination)}: {error}"
        ) from None


def prune_empty_parent_dirs(root: Path, destination: Path) -> None:
    current = destination.parent
    while current != root and current != current.parent:
        try:
            current.rmdir()
        except OSError:
            return
        current = current.parent


def read_bytes_for_remove(path: Path, label: str) -> tuple[bytes | None, str | None]:
    try:
        return path.read_bytes(), None
    except OSError as error:
        return None, f"{label} cannot be read: {error}"


def sha256_file(path: Path) -> tuple[str | None, str | None]:
    content, detail = read_bytes_for_remove(path, "target")
    if detail is not None:
        return None, detail
    assert content is not None
    return "sha256:" + hashlib.sha256(content).hexdigest(), None


def display_path(root: Path, path: Path) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return path


__all__ = [
    "CONFLICT_STATUSES",
    "InstallResult",
    "InstallStatus",
    "RemoveResult",
    "RemoveStatus",
    "VOUCHABLE_STATUSES",
    "atomic_write_bytes",
    "atomic_write_text",
    "backup_existing_file",
    "default_file_mode",
    "display_path",
    "generated_pack_file",
    "generated_text_file_status",
    "install_file",
    "next_backup_path",
    "path_is_occupied",
    "planned_result_matches_destination",
    "prune_empty_parent_dirs",
    "read_bytes_for_remove",
    "selected_files",
    "sha256_file",
    "source_digest",
    "source_is_executable",
    "unlink_target_file",
]

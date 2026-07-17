"""Pack removal: vouch-gated deletion and retired-target cleanup."""

from __future__ import annotations

from pathlib import Path

from installer.fileops import (
    RemoveResult,
    backup_existing_file,
    display_path,
    path_is_occupied,
    prune_empty_parent_dirs,
    read_bytes_for_remove,
    selected_files,
    sha256_file,
    unlink_target_file,
)
from installer.manifest import (
    PackFile,
    removal_target_destination,
    require_install_root,
    system_exit_detail,
)
from installer.provenance import (
    read_existing_installed_targets_for_remove,
    read_existing_provenance_files_for_remove,
)
from installer.registry import (
    INSTALLED_TARGETS_FILE,
    PACK_MANIFEST_FILE,
    PACK_NAME,
    PROVENANCE_FILE,
)
from installer.status import RemoveStatus

GENERATED_REMOVAL_TARGETS = frozenset(
    {
        INSTALLED_TARGETS_FILE.as_posix(),
        PACK_MANIFEST_FILE.as_posix(),
        PROVENANCE_FILE.as_posix(),
    }
)

# Installed target paths of skills retired from the manifest. A normal
# install/refresh deletes vouched leftovers (retire_stale_targets) so user
# scopes do not accumulate orphaned pack files. Retiring a skill means:
# remove it from registry SKILL_NAMES, regenerate the manifest, and add the
# paths the last shipping manifest listed for it here.
RETIRED_TARGETS: tuple[str, ...] = (
    ".config/agents/skills/se-pack/SKILL.md",
    ".claude/skills/se-pack/SKILL.md",
    ".codex/skills/se-pack/SKILL.md",
)

# remove_pack_file statuses renamed so the install summary reads as
# retirement, not pack removal ("missing" is excluded on purpose: absent
# retired targets are skipped without a result).
_RETIRED_STATUSES = {
    RemoveStatus.REMOVED: RemoveStatus.RETIRED,
    RemoveStatus.PRESERVED: RemoveStatus.RETIRED_PRESERVED,
    RemoveStatus.WOULD_REMOVE: RemoveStatus.WOULD_RETIRE,
}


def normalize_removal_candidate(candidate: str) -> str:
    normalized = candidate.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def is_git_internal_candidate(candidate: str) -> bool:
    return candidate == ".git" or candidate.startswith(".git/")


def recognized_removal_targets(files: list[PackFile]) -> set[str]:
    # Retired targets stay recognized so a full --remove on a root whose
    # receipts still list them deletes the leftovers instead of reporting
    # them as unrecognized.
    return {
        *(file.target.as_posix() for file in files),
        *GENERATED_REMOVAL_TARGETS,
        *RETIRED_TARGETS,
    }


def removal_candidate_rejection(
    candidate: str,
    recognized_targets: set[str],
) -> str | None:
    if is_git_internal_candidate(candidate):
        return "refusing to remove .git internals"
    if candidate not in recognized_targets:
        return f"not a recognized {PACK_NAME} target"
    return None


def installed_target_candidates(
    files: list[PackFile],
    root: Path,
    *,
    platforms: list[str] | None,
    install_all: bool,
    provenance_files: dict[str, str] | None = None,
) -> set[str]:
    receipt_targets = {
        normalize_removal_candidate(path)
        for path in read_existing_installed_targets_for_remove(root)
    }
    # remove_installed_pack parses provenance.json once and threads the
    # normalized dict in; standalone callers pass nothing and we read it here.
    if provenance_files is None:
        provenance_files = {
            normalize_removal_candidate(path): digest
            for path, digest in read_existing_provenance_files_for_remove(
                root
            ).items()
        }
    provenance_targets = set(provenance_files)
    if receipt_targets or provenance_targets:
        candidates = {*receipt_targets, *provenance_targets}
    else:
        selected, _ = selected_files(files, root, platforms, install_all)
        candidates = {file.target.as_posix() for file in selected}

    candidates.update(GENERATED_REMOVAL_TARGETS)
    return candidates


def may_remove_pack_file(
    destination: Path,
    *,
    file: PackFile | None,
    recorded_hash: str | None,
    force: bool,
) -> tuple[bool, str | None]:
    if force:
        return True, None
    if recorded_hash:
        digest, detail = sha256_file(destination)
        if detail is not None:
            return False, detail
        if recorded_hash == digest:
            return True, None
    if file and file.source is not None:
        destination_content, detail = read_bytes_for_remove(destination, "target")
        if detail is not None:
            return False, detail
        source_content, source_detail = read_bytes_for_remove(
            file.source,
            "pack template",
        )
        if source_detail is not None:
            raise SystemExit(f"error: {source_detail}") from None
        if destination_content == source_content:
            return True, None
    return False, "content differs from installed pack version"


def remove_pack_file(
    root: Path,
    relative_path: Path,
    *,
    file: PackFile | None,
    recorded_hash: str | None,
    force: bool,
    dry_run: bool,
    backup: bool,
) -> RemoveResult:
    try:
        destination = removal_target_destination(root, relative_path)
    except SystemExit as error:
        return RemoveResult(
            relative_path,
            RemoveStatus.PRESERVED,
            detail=system_exit_detail(error),
        )
    if not path_is_occupied(destination):
        return RemoveResult(relative_path, RemoveStatus.MISSING)
    if destination.is_symlink():
        if not force:
            return RemoveResult(
                relative_path,
                RemoveStatus.PRESERVED,
                detail="target is a symlink",
            )
    elif not destination.is_file():
        return RemoveResult(
            relative_path,
            RemoveStatus.PRESERVED,
            detail="target is not a regular file",
        )

    generated_state = relative_path in {
        INSTALLED_TARGETS_FILE,
        PACK_MANIFEST_FILE,
        PROVENANCE_FILE,
    }
    if generated_state and not destination.is_symlink():
        removable = True
        detail = None
    else:
        removable, detail = may_remove_pack_file(
            destination,
            file=file,
            recorded_hash=recorded_hash,
            force=force,
        )
    if not removable:
        return RemoveResult(relative_path, RemoveStatus.PRESERVED, detail=detail)
    if dry_run:
        return RemoveResult(relative_path, RemoveStatus.WOULD_REMOVE)

    backup_path = None
    if not destination.is_symlink():
        backup_path = backup_existing_file(
            root,
            destination,
            backup=backup,
            dry_run=dry_run,
        )
    unlink_target_file(root, destination)
    prune_empty_parent_dirs(root, destination)
    return RemoveResult(relative_path, RemoveStatus.REMOVED, backup_path)


def retire_stale_targets(
    root: Path,
    *,
    force: bool,
    dry_run: bool,
    backup: bool,
) -> list[RemoveResult]:
    """Delete retired-skill leftovers during a normal install/refresh.

    Must run before the receipt files are rewritten: vouching reads the
    prior install's provenance records, and the provenance rewrite drops
    retired entries (their targets left the manifest). Hash-vouched files
    are deleted with empty parent dirs pruned, drifted or unvouched files
    are preserved and reported unless ``force`` (which honors ``backup``),
    and absent targets produce no result.
    """
    if not RETIRED_TARGETS:
        return []
    provenance_files = {
        normalize_removal_candidate(path): digest
        for path, digest in read_existing_provenance_files_for_remove(root).items()
    }
    results: list[RemoveResult] = []
    for candidate in RETIRED_TARGETS:
        result = remove_pack_file(
            root,
            Path(candidate),
            file=None,
            recorded_hash=provenance_files.get(candidate),
            force=force,
            dry_run=dry_run,
            backup=backup,
        )
        if result.status is RemoveStatus.MISSING:
            continue
        results.append(
            RemoveResult(
                result.target,
                _RETIRED_STATUSES[result.status],
                backup=result.backup,
                detail=result.detail,
            )
        )
    return results


def remove_installed_pack(
    manifest: dict,
    files: list[PackFile],
    root: Path,
    *,
    platforms: list[str] | None,
    install_all: bool,
    force: bool,
    dry_run: bool,
    backup: bool,
) -> int:
    """Run the remove entry point: delete vouched pack files (honoring
    force/dry-run/backup) and report per-file results."""
    require_install_root(root)
    files_by_target = {file.target.as_posix(): file for file in files}
    provenance_files = {
        normalize_removal_candidate(path): digest
        for path, digest in read_existing_provenance_files_for_remove(root).items()
    }
    recognized_targets = recognized_removal_targets(files)

    print(f"{manifest['name']} {manifest['version']}")
    print(f"root: {root}")
    print("mode: remove")
    if dry_run:
        print("mode: dry-run")

    results: list[RemoveResult] = []
    for candidate in sorted(
        installed_target_candidates(
            files,
            root,
            platforms=platforms,
            install_all=install_all,
            provenance_files=provenance_files,
        )
    ):
        rejection = removal_candidate_rejection(candidate, recognized_targets)
        if rejection is not None:
            results.append(
                RemoveResult(Path(candidate), RemoveStatus.IGNORED, detail=rejection)
            )
            continue
        relative_path = Path(candidate)
        file = files_by_target.get(relative_path.as_posix())
        results.append(
            remove_pack_file(
                root,
                relative_path,
                file=file,
                recorded_hash=provenance_files.get(relative_path.as_posix()),
                force=force,
                dry_run=dry_run,
                backup=backup,
            )
        )

    for result in results:
        suffix = f" ({result.detail})" if result.detail else ""
        print(f"{result.status:14} {display_path(root, result.target)}{suffix}")
        if result.backup:
            print(f"{'backup':14} {display_path(root, result.backup)}")

    return 0


__all__ = [
    "GENERATED_REMOVAL_TARGETS",
    "RETIRED_TARGETS",
    "RemoveStatus",
    "installed_target_candidates",
    "is_git_internal_candidate",
    "may_remove_pack_file",
    "normalize_removal_candidate",
    "recognized_removal_targets",
    "removal_candidate_rejection",
    "remove_installed_pack",
    "remove_pack_file",
    "retire_stale_targets",
]

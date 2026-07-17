#!/usr/bin/env python3
"""Install the SE AI command pack into user-level agent skill directories."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from installer.fileops import (
    CONFLICT_STATUSES,
    InstallResult,
    InstallStatus,
    RemoveResult,
    display_path,
    install_file,
    selected_files,
)
from installer.management import pack_status, update_pack
from installer.manifest import (
    PackFile,
    load_manifest,
    manifest_cli_identity,
    require_install_root,
    validate_manifest,
)
from installer.provenance import (
    install_installed_targets_file,
    install_pack_manifest_file,
    install_provenance_file,
    installed_targets_set,
    never_vouched_targets,
    preserved_receipt_targets,
    read_existing_installed_targets,
)
from installer.registry import (
    PACK_MANIFEST_FILE,
    PLATFORM_REGISTRY,
    PLATFORMS,
    PROVENANCE_FILE,
    ROOT,
)
from installer.removal import remove_installed_pack, retire_stale_targets

__all__ = [
    "ManifestVersionAction",
    "main",
    "parse_args",
    "preflight_checks",
    "resolve_install_root",
]


class ManifestVersionAction(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        print(manifest_cli_identity())
        parser.exit()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Install SE AI command pack skills into user-level agent scopes "
            "(Claude Code/Cowork, OpenAI Codex, shared agents dir)."
        )
    )
    parser.add_argument(
        "--version",
        action=ManifestVersionAction,
        help="Print the se-ai-command-pack version and exit.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=("install", "status", "refresh", "update", "remove"),
        default="install",
        help=(
            "Lifecycle command. Bare invocation remains an install/refresh "
            "for backward compatibility."
        ),
    )
    root_group = parser.add_mutually_exclusive_group()
    root_group.add_argument(
        "--user",
        action="store_true",
        help="Install into the current user's home directory (the default).",
    )
    root_group.add_argument(
        "--root",
        help=(
            "Install root to use instead of the home directory. Mainly for "
            "tests; also the seam for future per-folder installs."
        ),
    )
    parser.add_argument(
        "--platform",
        action="append",
        choices=PLATFORMS,
        help=(
            "Install only this platform's skills, even if its anchor "
            "directory is missing. Repeat to select several."
        ),
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help=(
            "Install every platform's skills even when anchor directories "
            "are not present."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Overwrite existing files that differ from the pack templates. "
            "Add --backup to save .bak copies before overwriting."
        ),
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help=(
            "With --force or the remove command, save a .bak copy next to each "
            "overwritten or deleted file before changing it."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned changes without writing files.",
    )
    return parser.parse_args(argv)


def resolve_install_root(args: argparse.Namespace) -> Path:
    if args.root:
        root = Path(args.root).expanduser().resolve()
    else:
        root = Path.home().resolve()
    try:
        root.relative_to(ROOT)
    except ValueError:
        return root
    raise SystemExit(
        "error: refusing to use the pack source checkout as the install root; "
        "pass --root pointing elsewhere"
    )


def preflight_checks(root: Path, manifest_data: dict) -> None:
    """Pack prerequisite checks before any write.

    The seam for future backends: v0.1 only requires the install root to
    exist. Keep new prerequisites here so install and remove share them.
    """
    del manifest_data
    require_install_root(root)


def _install_payload(
    selected: list[PackFile],
    root: Path,
    *,
    force: bool,
    dry_run: bool,
    backup: bool,
    planned_results: dict[Path, InstallResult] | None = None,
) -> list[InstallResult]:
    results: list[InstallResult] = []
    for file in selected:
        results.append(
            install_file(
                file,
                root,
                force=force,
                dry_run=dry_run,
                backup=backup,
                planned_result=(
                    planned_results.get(file.target) if planned_results else None
                ),
            )
        )
    return results


def _conflict_results(results: list[InstallResult]) -> list[InstallResult]:
    return [result for result in results if result.status in CONFLICT_STATUSES]


def _print_conflicts(conflicts: list[InstallResult]) -> None:
    print("")
    print("Conflicts:")
    for result in conflicts:
        if result.status is InstallStatus.SYMLINK_CONFLICT:
            print(
                f"- {result.file.target} "
                "(target is a symlink; the pack installs regular files only)"
            )
        else:
            print(f"- {result.file.target}")
    print("Re-run with --force to overwrite these files.")


def _install_receipt_files(
    manifest_data: dict,
    root: Path,
    *,
    selected: list[PackFile],
    skipped: list[tuple[PackFile, str]],
    results: list[InstallResult],
    dry_run: bool,
) -> list[tuple[Path, str]]:
    """Write the pack-manifest, provenance, and installed-targets receipts.

    Appends each receipt's result to ``results`` in order (provenance vouches
    for the results collected so far, so the ordering is load-bearing) and
    returns the receipt entries preserved for platforms skipped only in this
    run.
    """
    results.append(
        install_pack_manifest_file(
            manifest_data,
            root,
            dry_run=dry_run,
        )
    )
    kept_receipt_targets = preserved_receipt_targets(
        read_existing_installed_targets(root), skipped
    )
    receipt_extra_targets = [
        PACK_MANIFEST_FILE,
        PROVENANCE_FILE,
        *(kept_target for kept_target, _ in kept_receipt_targets),
    ]
    receipt_target_set = installed_targets_set(selected, receipt_extra_targets)
    results.append(
        install_provenance_file(
            manifest_data,
            results,
            root,
            receipt_targets=receipt_target_set,
            never_vouched=never_vouched_targets(),
            dry_run=dry_run,
        )
    )
    results.append(
        install_installed_targets_file(
            selected,
            root,
            dry_run=dry_run,
            extra_targets=receipt_extra_targets,
        )
    )
    return kept_receipt_targets


def _print_install_summary(
    root: Path,
    *,
    results: list[InstallResult],
    retired_results: list[RemoveResult],
    skipped: list[tuple[PackFile, str]],
    kept_receipt_targets: list[tuple[Path, str]],
) -> None:
    """Print install results, retired results, skips, hints, and notes."""
    for result in results:
        print(f"{result.status:11} {result.file.target}")
        if result.backup:
            print(f"{'backup':11} {display_path(root, result.backup)}")
    for retired in retired_results:
        suffix = f" ({retired.detail})" if retired.detail else ""
        print(f"{retired.status:17} {display_path(root, retired.target)}{suffix}")
        if retired.backup:
            print(f"{'backup':17} {display_path(root, retired.backup)}")
    for file, reason in skipped:
        print(f"skipped     {file.target} ({reason})")
    anchor_missed_platforms = sorted(
        {
            file.platform
            for file, reason in skipped
            if reason.startswith("anchor ")
        }
    )
    for platform in anchor_missed_platforms:
        info = PLATFORM_REGISTRY[platform]
        print(
            f"hint: {info.anchor}/ not found under {root}; "
            f"{info.display} does not appear to be set up here. Pass "
            f"--platform {platform} or --all to install anyway."
        )
    for kept_target, kept_platform in kept_receipt_targets:
        print(
            f"kept-in-receipt {kept_target} "
            f"({kept_platform} skills not selected in this run; "
            "a later remove still covers them)"
        )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    command = args.command
    if args.backup and not args.force and command != "remove":
        raise SystemExit(
            "error: --backup requires --force unless the remove command is used"
        )

    root = resolve_install_root(args)
    require_install_root(root)

    if command == "status":
        return pack_status(root)

    if command == "update":
        return update_pack(
            root,
            dry_run=args.dry_run,
            force=args.force,
            backup=args.backup,
            platforms=args.platform,
            install_all=args.all,
        )

    manifest_data, files = load_manifest()
    validate_manifest(files)
    preflight_checks(root, manifest_data)

    if command == "remove":
        return remove_installed_pack(
            manifest_data,
            files,
            root,
            platforms=args.platform,
            install_all=args.all,
            force=args.force,
            dry_run=args.dry_run,
            backup=args.backup,
        )

    selected, skipped = selected_files(files, root, args.platform, args.all)

    print(f"{manifest_data['name']} {manifest_data['version']}")
    print(f"root: {root}")
    if args.dry_run:
        print("mode: dry-run")

    # A normal refresh is plan-before-apply: detect every selected-file
    # conflict before the first pack-owned write.
    if not args.force and not args.dry_run:
        preflight_results = _install_payload(
            selected,
            root,
            force=False,
            dry_run=True,
            backup=False,
        )
        preflight_conflicts = _conflict_results(preflight_results)
        if preflight_conflicts:
            for conflict in preflight_conflicts:
                print(f"{conflict.status:11} {conflict.file.target}")
            _print_conflicts(preflight_conflicts)
            return 2
        planned_results = {
            result.file.target: result
            for result in preflight_results
            if result.source_content is not None
        }
    else:
        planned_results = None

    results = _install_payload(
        selected,
        root,
        force=args.force,
        dry_run=args.dry_run,
        backup=args.backup,
        planned_results=planned_results,
    )

    # Retired-target cleanup must run before the receipt files are rewritten:
    # it vouches stale files against the prior install's provenance, and the
    # provenance rewrite below drops retired entries (they left the manifest,
    # so receipts never list them again).
    retired_results = retire_stale_targets(
        root,
        force=args.force,
        dry_run=args.dry_run,
        backup=args.backup,
    )

    kept_receipt_targets = _install_receipt_files(
        manifest_data,
        root,
        selected=selected,
        skipped=skipped,
        results=results,
        dry_run=args.dry_run,
    )

    _print_install_summary(
        root,
        results=results,
        retired_results=retired_results,
        skipped=skipped,
        kept_receipt_targets=kept_receipt_targets,
    )

    conflict_results = _conflict_results(results)
    if conflict_results:
        _print_conflicts(conflict_results)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

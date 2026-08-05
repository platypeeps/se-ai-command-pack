"""Status and source-checkout update operations for the installed pack."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from installer.registry import (
    INSTALLED_TARGETS_FILE,
    PACK_MANIFEST_FILE,
    PACK_NAME,
    PLATFORM_REGISTRY,
    PROVENANCE_FILE,
    ROOT,
)


def _read_json_object(path: Path) -> dict[str, Any] | None:
    if path.is_symlink() or not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8", errors="strict"))
    except (OSError, UnicodeError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def _installed_platforms(root: Path) -> list[str]:
    receipt = root / INSTALLED_TARGETS_FILE
    if receipt.is_symlink() or not receipt.is_file():
        return []
    try:
        targets = receipt.read_text(encoding="utf-8", errors="strict").splitlines()
    except (OSError, UnicodeError):
        return []
    return [
        platform
        for platform, info in PLATFORM_REGISTRY.items()
        if any(
            target == info.skills_dir or target.startswith(info.skills_dir + "/")
            for target in targets
        )
    ]


def pack_status(root: Path) -> int:
    """Report receipt, checkout, version, and platform state."""
    installed = _read_json_object(root / PACK_MANIFEST_FILE)
    provenance = _read_json_object(root / PROVENANCE_FILE)
    if installed is None or installed.get("name") != PACK_NAME:
        print(f"{PACK_NAME}: not installed under {root}")
        return 1

    installed_version = installed.get("version", "unknown")
    source_value = provenance.get("sourceRoot") if provenance else None
    source_root = (
        Path(source_value).expanduser().resolve()
        if isinstance(source_value, str) and source_value
        else None
    )
    checkout = (
        _read_json_object(source_root / "manifest.json") if source_root else None
    )
    checkout_version = (
        checkout.get("version")
        if checkout is not None and checkout.get("name") == PACK_NAME
        else None
    )

    print(f"{PACK_NAME} {installed_version}")
    print(f"root: {root}")
    print(f"source: {source_root if source_root else 'unavailable'}")
    print(
        "platforms: "
        + (", ".join(_installed_platforms(root)) or "none recorded")
    )
    if checkout_version is None:
        print("checkout: unavailable")
    elif checkout_version == installed_version:
        print(f"checkout: {checkout_version} (installed version matches)")
    else:
        print(f"checkout: {checkout_version} (refresh available)")
    return 0


def _owned_by_current_user(path: Path) -> bool:
    """Whether ``path`` is owned by the current effective user.

    On platforms without an effective-uid primitive (e.g. Windows), ownership
    cannot be established, so this returns ``True`` and the same-checkout /
    explicit-confirmation gate in :func:`_source_checkout` remains the
    cross-platform trust guarantee. ``stat`` follows symlinks, so a symlinked
    ``.git`` is judged by its resolved target.

    An :class:`OSError` (missing path, permission denied, broken symlink) is
    treated as "not owned" and returns ``False`` so the trust gate fails closed
    rather than proceeding on an unverifiable path.
    """
    geteuid = getattr(os, "geteuid", None)
    if geteuid is None:
        return True
    try:
        return path.stat().st_uid == geteuid()
    except OSError:
        return False


def _source_checkout(root: Path, *, confirm_source: bool) -> Path:
    provenance = _read_json_object(root / PROVENANCE_FILE)
    source_value = provenance.get("sourceRoot") if provenance else None
    if not isinstance(source_value, str) or not source_value:
        raise SystemExit(
            "error: installed provenance does not record a source checkout; "
            "rerun install.py from the checkout"
        )
    source_root = Path(source_value).expanduser().resolve()
    manifest = _read_json_object(source_root / "manifest.json")
    if not (source_root / "install.py").is_file() or manifest is None:
        raise SystemExit(
            f"error: recorded source checkout is unavailable: {source_root}"
        )
    if manifest.get("name") != PACK_NAME:
        raise SystemExit(
            f"error: recorded source checkout is not {PACK_NAME}: {source_root}"
        )
    # Source-trust gate (audit A-017). The recorded sourceRoot comes from a
    # plain-JSON provenance receipt with no integrity protection, and update
    # runs git against it and executes its install.py. Refuse an unverified path
    # before any git or exec: it must be a git repository (current-user-owned on
    # POSIX), and must either be the running checkout or be explicitly confirmed.
    # The window between these checks and the later git/exec use is an accepted
    # residual TOCTOU risk, tracked as a separate hardening follow-up.
    git_entry = source_root / ".git"
    if not git_entry.exists():
        raise SystemExit(
            f"error: recorded source checkout is not a git repository: {source_root}"
        )
    if not (
        _owned_by_current_user(source_root) and _owned_by_current_user(git_entry)
    ):
        raise SystemExit(
            "error: recorded source checkout is not owned by the current user: "
            f"{source_root}"
        )
    if source_root != ROOT and not confirm_source:
        if sys.stdin.isatty():
            answer = input(
                f"Recorded source checkout {source_root} differs from the running "
                f"checkout {ROOT}. Update from it anyway? [y/N] "
            )
            if answer.strip().lower() not in ("y", "yes"):
                raise SystemExit(
                    "error: update from a relocated source checkout was not confirmed"
                )
        else:
            raise SystemExit(
                f"error: recorded source checkout {source_root} differs from the "
                f"running checkout {ROOT}; pass --confirm-source to update from a "
                "relocated checkout"
            )
    return source_root


def _run_git(source_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(source_root), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        suffix = f": {detail}" if detail else ""
        raise SystemExit(f"error: git {' '.join(args)} failed{suffix}")
    return result.stdout.strip()


def _installer_args(
    root: Path,
    *,
    dry_run: bool,
    force: bool,
    backup: bool,
    platforms: list[str] | None,
    install_all: bool,
) -> list[str]:
    args = ["refresh", "--root", str(root)]
    for platform in platforms or []:
        args.extend(("--platform", platform))
    if install_all:
        args.append("--all")
    if dry_run:
        args.append("--dry-run")
    if force:
        args.append("--force")
    if backup:
        args.append("--backup")
    return args


def update_pack(
    root: Path,
    *,
    dry_run: bool,
    force: bool,
    backup: bool,
    platforms: list[str] | None,
    install_all: bool,
    confirm_source: bool = False,
) -> int:
    """Fast-forward the recorded checkout and refresh with a new process."""
    source_root = _source_checkout(root, confirm_source=confirm_source)
    dirty = _run_git(source_root, "status", "--porcelain")
    if dirty:
        raise SystemExit(
            f"error: recorded source checkout has uncommitted changes: {source_root}"
        )

    if dry_run:
        _run_git(source_root, "fetch", "--quiet")
        relation = _run_git(
            source_root,
            "rev-list",
            "--left-right",
            "--count",
            "HEAD...@{upstream}",
        )
        print(f"update plan: checkout {source_root}")
        print(f"git divergence (local remote): {relation.replace(chr(9), ' ')}")
        return subprocess.run(
            [
                sys.executable,
                str(source_root / "install.py"),
                *_installer_args(
                    root,
                    dry_run=True,
                    force=force,
                    backup=backup,
                    platforms=platforms,
                    install_all=install_all,
                ),
            ],
            check=False,
        ).returncode

    _run_git(source_root, "pull", "--ff-only")
    installer = str(source_root / "install.py")
    plan = subprocess.run(
        [
            sys.executable,
            installer,
            *_installer_args(
                root,
                dry_run=True,
                force=force,
                backup=backup,
                platforms=platforms,
                install_all=install_all,
            ),
        ],
        check=False,
    )
    if plan.returncode != 0:
        return plan.returncode
    return subprocess.run(
        [
            sys.executable,
            installer,
            *_installer_args(
                root,
                dry_run=False,
                force=force,
                backup=backup,
                platforms=platforms,
                install_all=install_all,
            ),
        ],
        check=False,
    ).returncode


__all__ = ["pack_status", "update_pack"]

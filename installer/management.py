"""Status and source-checkout update operations for the installed pack."""

from __future__ import annotations

import json
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


def _source_checkout(root: Path) -> Path:
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
    return source_root


def _run_git(source_root: Path, *args: str, capture: bool = False) -> str:
    result = subprocess.run(
        ["git", "-C", str(source_root), *args],
        text=True,
        capture_output=capture,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() if capture else ""
        suffix = f": {detail}" if detail else ""
        raise SystemExit(f"error: git {' '.join(args)} failed{suffix}")
    return result.stdout.strip() if capture else ""


def _installer_args(root: Path, *, dry_run: bool, force: bool, backup: bool) -> list[str]:
    args = ["refresh", "--root", str(root)]
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
) -> int:
    """Fast-forward the recorded checkout and refresh with a new process."""
    source_root = _source_checkout(root)
    dirty = _run_git(source_root, "status", "--porcelain", capture=True)
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
            capture=True,
        )
        print(f"update plan: checkout {source_root}")
        print(f"git divergence (local remote): {relation.replace(chr(9), ' ')}")
        return subprocess.run(
            [
                sys.executable,
                str(source_root / "install.py"),
                *_installer_args(
                    root, dry_run=True, force=force, backup=backup
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
            *_installer_args(root, dry_run=True, force=force, backup=backup),
        ],
        check=False,
    )
    if plan.returncode != 0:
        return plan.returncode
    return subprocess.run(
        [
            sys.executable,
            installer,
            *_installer_args(root, dry_run=False, force=force, backup=backup),
        ],
        check=False,
    ).returncode


__all__ = ["pack_status", "update_pack"]

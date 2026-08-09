"""Status and source-checkout update operations for the installed pack."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from dataclasses import dataclass
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

# Bound git the same way every other subprocess wrapper in the repo does
# (check-release-payload.py, create-release-tag.py): a hung git during update
# must not block the installer forever.
GIT_TIMEOUT_SECONDS = 60

# A `.git` pointer file holds one short `gitdir: <path>` line; bound the read
# so a hostile checkout cannot force an unbounded read into an error message.
GITDIR_PREFIX = "gitdir: "
GITDIR_READ_LIMIT = 4096


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
    cross-platform trust guarantee.

    This is the tier-3 (no directory-fd primitives) ownership check only; tiers
    1 and 2 own the source directory through :func:`os.fstat` on the held
    descriptor, and every tier rejects a symlinked ``.git`` before ownership is
    considered, so no ownership decision is ever made about a symlink target.

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


def _uid_owned_by_current_user(uid: int) -> bool:
    geteuid = getattr(os, "geteuid", None)
    return True if geteuid is None else uid == geteuid()


@dataclass
class SourceHandle:
    """A source checkout pinned to an open directory descriptor.

    ``fd`` is the object the trust checks ran against and the object every
    later git/exec use runs inside, so the checked directory is the used
    directory. It is ``None`` on the tier-3 path fallback, where the
    same-checkout / ``--confirm-source`` gate remains the trust guarantee.
    """

    path: Path
    fd: int | None = None

    def close(self) -> None:
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None


def _fd_pinning_tier() -> int:
    """Which source-pinning tier this platform supports (see design A-017/1).

    1: full fd pinning — checks run relative to the held descriptor.
    2: the descriptor is held and used for git/exec, but the entry checks fall
       back to paths because a ``dir_fd``/``follow_symlinks`` capability set is
       incomplete.
    3: no descriptor at all (Windows, or a POSIX without ``O_DIRECTORY`` or
       ``fchdir``); the original path-based flow applies.
    """
    if (
        getattr(os, "geteuid", None) is None
        or getattr(os, "O_DIRECTORY", None) is None
        or getattr(os, "fchdir", None) is None
    ):
        return 3
    if (
        os.stat in os.supports_dir_fd
        and os.open in os.supports_dir_fd
        and os.stat in os.supports_follow_symlinks
    ):
        return 1
    return 2


def _read_bytes_at(
    source_root: Path, name: str, dir_fd: int | None, limit: int | None = None
) -> bytes | None:
    try:
        if dir_fd is None:
            with open(source_root / name, "rb") as stream:
                return stream.read() if limit is None else stream.read(limit)
        handle = os.open(name, os.O_RDONLY, dir_fd=dir_fd)
        try:
            stream = os.fdopen(handle, "rb")
        except Exception:
            os.close(handle)
            raise
        with stream:
            return stream.read() if limit is None else stream.read(limit)
    except OSError:
        return None


def _is_regular_file_at(source_root: Path, name: str, dir_fd: int | None) -> bool:
    """Whether ``name`` is a regular file, never following a final symlink.

    A symlinked ``install.py`` would let the relative exec escape the pinned
    directory, so link-following ``Path.is_file()`` is not usable here.
    """
    try:
        if dir_fd is None:
            info = (source_root / name).lstat()
        else:
            info = os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
    except OSError:
        return False
    return stat.S_ISREG(info.st_mode)


def _read_source_json(
    source_root: Path, name: str, dir_fd: int | None
) -> dict[str, Any] | None:
    if dir_fd is None:
        return _read_json_object(source_root / name)
    if not _is_regular_file_at(source_root, name, dir_fd):
        return None
    raw = _read_bytes_at(source_root, name, dir_fd)
    if raw is None:
        return None
    try:
        payload = json.loads(raw.decode("utf-8", errors="strict"))
    except (UnicodeError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def _verify_gitdir_pointer(source_root: Path, dir_fd: int | None) -> None:
    """Validate a ``.git`` file's ``gitdir:`` target, one hop, no recursion.

    A worktree/submodule pointer redirects the repository outside the checked
    directory, so the target must exist, be a directory, and be
    current-user-owned before any git runs. ``commondir`` and nested pointers
    are deliberately not followed.
    """
    raw = _read_bytes_at(source_root, ".git", dir_fd, GITDIR_READ_LIMIT) or b""
    lines = raw.decode("utf-8", errors="replace").splitlines()
    first = lines[0].strip() if lines else ""
    target = (
        first[len(GITDIR_PREFIX) :].strip() if first.startswith(GITDIR_PREFIX) else ""
    )
    # repr-quote the attacker-controlled pointer text so control and escape
    # bytes from the .git file cannot reach the terminal raw.
    unverified = (
        "error: recorded source checkout .git file points to an unverified "
        f"gitdir: {(target or first)!r}"
    )
    if not target:
        raise SystemExit(unverified)
    try:
        # An absolute target ignores dir_fd; a relative one resolves inside the
        # pinned directory.
        info = (
            os.stat(target, dir_fd=dir_fd)
            if dir_fd is not None
            else (source_root / target).stat()
        )
    except OSError:
        raise SystemExit(unverified) from None
    if not stat.S_ISDIR(info.st_mode) or not _uid_owned_by_current_user(info.st_uid):
        raise SystemExit(unverified)


def _git_entry_uid(source_root: Path, dir_fd: int | None) -> int:
    """Validate the ``.git`` entry shape and return its owner uid."""
    try:
        if dir_fd is None:
            info = (source_root / ".git").lstat()
        else:
            info = os.stat(".git", dir_fd=dir_fd, follow_symlinks=False)
    except OSError:
        raise SystemExit(
            f"error: recorded source checkout is not a git repository: {source_root}"
        ) from None
    if stat.S_ISLNK(info.st_mode):
        # A symlinked .git re-points the repository outside the checked
        # directory, which is exactly the redirection this gate refuses.
        raise SystemExit(
            f"error: recorded source checkout has a symlinked .git: {source_root}"
        )
    if stat.S_ISREG(info.st_mode):
        _verify_gitdir_pointer(source_root, dir_fd)
    elif not stat.S_ISDIR(info.st_mode):
        raise SystemExit(
            f"error: recorded source checkout is not a git repository: {source_root}"
        )
    return info.st_uid


def _verify_source_trust(
    handle: SourceHandle, *, check_fd: int | None, confirm_source: bool
) -> None:
    # Source-trust gate (audit A-017, hardened by A-017/1). The recorded
    # sourceRoot comes from a plain-JSON provenance receipt with no integrity
    # protection, and update runs git against it and executes its install.py.
    # Refuse an unverified checkout before any git or exec: it must be a git
    # repository (current-user-owned on POSIX), and must either be the running
    # checkout or be explicitly confirmed. On tiers 1 and 2 the directory that
    # is checked here is the descriptor that later git/exec runs inside;
    # entries *inside* the checkout are still re-resolved by git and by the
    # child interpreter, so a principal who can already write inside the owned
    # checkout remains in scope (documented residual).
    source_root = handle.path
    manifest = _read_source_json(source_root, "manifest.json", check_fd)
    if manifest is None or not _is_regular_file_at(source_root, "install.py", check_fd):
        raise SystemExit(
            f"error: recorded source checkout is unavailable: {source_root}"
        )
    if manifest.get("name") != PACK_NAME:
        raise SystemExit(
            f"error: recorded source checkout is not {PACK_NAME}: {source_root}"
        )
    git_uid = _git_entry_uid(source_root, check_fd)
    if handle.fd is None:
        directory_owned = _owned_by_current_user(source_root)
    else:
        try:
            directory_owned = _uid_owned_by_current_user(os.fstat(handle.fd).st_uid)
        except OSError:
            directory_owned = False
    if not (directory_owned and _uid_owned_by_current_user(git_uid)):
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


def _source_checkout(root: Path, *, confirm_source: bool) -> SourceHandle:
    provenance = _read_json_object(root / PROVENANCE_FILE)
    source_value = provenance.get("sourceRoot") if provenance else None
    if not isinstance(source_value, str) or not source_value:
        raise SystemExit(
            "error: installed provenance does not record a source checkout; "
            "rerun install.py from the checkout"
        )
    source_root = Path(source_value).expanduser().resolve()
    tier = _fd_pinning_tier()
    fd: int | None = None
    if tier <= 2:
        try:
            fd = os.open(source_root, os.O_RDONLY | os.O_DIRECTORY)
        except OSError:
            raise SystemExit(
                f"error: recorded source checkout is unavailable: {source_root}"
            ) from None
    handle = SourceHandle(source_root, fd)
    try:
        _verify_source_trust(
            handle,
            check_fd=fd if tier == 1 else None,
            confirm_source=confirm_source,
        )
    except BaseException:
        handle.close()
        raise
    return handle


def _pinned_child_kwargs(fd: int) -> dict[str, Any]:
    """subprocess keywords that run a child inside the pinned directory.

    ``preexec_fn`` runs in the forked child before exec; it is unsafe in a
    multi-threaded parent and unsupported in subinterpreters, and
    ``install.py update`` is a single-threaded CPython CLI entry point.
    ``pass_fds`` keeps the descriptor open past ``close_fds`` so the callback's
    ``fchdir`` is a documented contract rather than an implementation detail.
    """
    return {"pass_fds": (fd,), "preexec_fn": lambda: os.fchdir(fd)}


def _run_git(source: SourceHandle | Path, *args: str) -> str:
    fd = source.fd if isinstance(source, SourceHandle) else None
    path = source.path if isinstance(source, SourceHandle) else source
    argv = ["git", "-C", "." if fd is not None else str(path), *args]
    try:
        result = subprocess.run(
            argv,
            text=True,
            capture_output=True,
            check=False,
            timeout=GIT_TIMEOUT_SECONDS,
            **({} if fd is None else _pinned_child_kwargs(fd)),
        )
    except FileNotFoundError:
        raise SystemExit("error: git not found") from None
    except subprocess.TimeoutExpired:
        raise SystemExit(f"error: git {' '.join(args)} timed out") from None
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        suffix = f": {detail}" if detail else ""
        raise SystemExit(f"error: git {' '.join(args)} failed{suffix}")
    return result.stdout.strip()


def _run_installer(handle: SourceHandle, args: list[str]) -> int:
    """Run the checkout's install.py, resolved inside the pinned directory."""
    fd = handle.fd
    script = "install.py" if fd is not None else str(handle.path / "install.py")
    return subprocess.run(
        [sys.executable, script, *args],
        check=False,
        **({} if fd is None else _pinned_child_kwargs(fd)),
    ).returncode


def _installer_args(
    root: Path,
    *,
    dry_run: bool,
    force: bool,
    backup: bool,
    platforms: list[str] | None,
    install_all: bool,
    verbose: bool,
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
    if verbose:
        args.append("--verbose")
    return args


def update_pack(
    root: Path,
    *,
    dry_run: bool,
    force: bool,
    backup: bool,
    platforms: list[str] | None,
    install_all: bool,
    verbose: bool = False,
    confirm_source: bool = False,
) -> int:
    """Fast-forward the recorded checkout and refresh with a new process."""
    handle = _source_checkout(root, confirm_source=confirm_source)
    try:
        source_root = handle.path
        dirty = _run_git(handle, "status", "--porcelain")
        if dirty:
            raise SystemExit(
                "error: recorded source checkout has uncommitted changes: "
                f"{source_root}"
            )

        if dry_run:
            _run_git(handle, "fetch", "--quiet")
            relation = _run_git(
                handle,
                "rev-list",
                "--left-right",
                "--count",
                "HEAD...@{upstream}",
            )
            print(f"update plan: checkout {source_root}")
            print(f"git divergence (local remote): {relation.replace(chr(9), ' ')}")
            return _run_installer(
                handle,
                _installer_args(
                    root,
                    dry_run=True,
                    force=force,
                    backup=backup,
                    platforms=platforms,
                    install_all=install_all,
                    verbose=verbose,
                ),
            )

        _run_git(handle, "pull", "--ff-only")
        planned = _run_installer(
            handle,
            _installer_args(
                root,
                dry_run=True,
                force=force,
                backup=backup,
                platforms=platforms,
                install_all=install_all,
                verbose=verbose,
            ),
        )
        if planned != 0:
            return planned
        return _run_installer(
            handle,
            _installer_args(
                root,
                dry_run=False,
                force=force,
                backup=backup,
                platforms=platforms,
                install_all=install_all,
                verbose=verbose,
            ),
        )
    finally:
        handle.close()


__all__ = ["pack_status", "update_pack"]

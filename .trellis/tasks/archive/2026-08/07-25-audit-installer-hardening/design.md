# Design — Installer subprocess and file-handling hardening

Scope: `installer/management.py`, `installer/fileops.py`, `install.py`, plus
tests. Four audit findings: A-013, A-019, A-011, A-008. `installer/**` and
`install.py` are release-payload paths (`check-release-payload.py`
`PAYLOAD_PREFIXES`/`PAYLOAD_EXACT`), so this task carries a manifest **patch**
bump (0.66.13 → 0.66.14) and a matching `CHANGELOG.md` entry — the release gate
fails otherwise.

## A-013 — `_run_git` timeout (management.py:168)

`_run_git` runs `subprocess.run(["git", "-C", ...], check=False)` with no
`timeout`, so a hung git during `update_pack` blocks forever. Every other
subprocess wrapper in the repo bounds itself (`check-release-payload.py` and
`create-release-tag.py` both use `timeout=60` and map `TimeoutExpired`/
`FileNotFoundError` to a clean error). Mirror that here:

- Add `timeout=60` to the `subprocess.run` call (a module constant
  `GIT_TIMEOUT_SECONDS = 60` for parity with the other scripts).
- Wrap the call: `except subprocess.TimeoutExpired: raise SystemExit(f"error: git {' '.join(args)} timed out")`.
  Also map `except FileNotFoundError: raise SystemExit("error: git not found")`
  — git-absent parity, same as the sibling scripts, and cheap. `from None` on
  both to suppress the chained traceback, matching the existing
  `returncode != 0` branch style.

The existing `returncode != 0` handling is unchanged. `_run_git` already raises
`SystemExit` (not a custom exception), so the installer's existing top-level
handling is untouched.

## A-019 — symlink-safe, mode-preserving backup (fileops.py:398, :179)

`backup_existing_file` calls `next_backup_path` (which probes for a
non-occupied `.bak`/`.bakN` candidate) and then `shutil.copyfile(destination,
backup_path)`. Two defects:

1. **Check-then-use window.** `next_backup_path` decides the candidate is
   unoccupied, then `copyfile` opens it for write later. Between the two, the
   path can be created (symlink or regular file); `copyfile` opens the
   destination with plain `open(..., "wb")`, which **follows a symlink** and
   truncates its target. An attacker who wins the race redirects the backup
   write.
2. **Mode leak.** `copyfile` copies content but not mode; the new `.bak` gets
   the process umask default (typically 0644), even when the source file was
   0600. A backup of a secret-bearing file is world-readable.

Fix: create the backup with an atomic exclusive, no-follow open and copy into
that descriptor, preserving the source file's permission bits. Because
`O_EXCL` makes the create atomic, the candidate search and the create must be
one loop: the exclusive open is the source of truth, and `O_EXCL` raises
`FileExistsError` on an occupied candidate (including an existing symlink),
which advances to the next index.

**Ordering (concern C-1).** `validate_resolved_target_path` (manifest.py:217)
calls `path.resolve(strict=False)`, which *follows symlinks*; a `.bak`
candidate that is itself a symlink escaping the install root would make the
validator raise `SystemExit` ("resolves outside the install root") rather than
letting the loop skip past it. The original `next_backup_path` avoids this by
validating only a candidate that `path_is_occupied` already reported as free.
To preserve "skip an occupied/symlinked candidate, don't hard-fail on it," the
open must come **first**; validation runs only on the candidate we actually
created, which — being a fresh `O_EXCL | O_NOFOLLOW` regular file under the
already-trusted `destination.parent` — always resolves inside root:

```python
def _open_exclusive_backup(root: Path, destination: Path) -> tuple[int, Path]:
    # Try .bak, then .bak1, .bak2, ... O_EXCL closes the check-then-use window
    # and treats an existing symlink as occupied (FileExistsError -> advance),
    # so a hostile .bak symlink is skipped, never followed or hard-failed on.
    index = 0
    while True:
        suffix = ".bak" if index == 0 else f".bak{index}"
        candidate = destination.with_name(f"{destination.name}{suffix}")
        try:
            fd = os.open(
                candidate,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW,
                0o600,
            )
        except FileExistsError:
            index += 1
            continue
        # The path now exists as a brand-new regular file we just created;
        # resolve() can no longer be diverted by a symlink at `candidate`.
        validate_resolved_target_path(root, candidate, "backup path")
        return fd, candidate
```

`backup_existing_file` then:

- `source_mode = destination.stat().st_mode & 0o777` (the file being backed up;
  `stat` on the destination is fine — it is the file we are about to
  overwrite, already validated as a regular file by the caller path);
- open the exclusive fd, `os.fchmod(fd, source_mode)`, stream
  `destination`'s bytes into it (`shutil.copyfileobj` from an
  `open(destination, "rb")` into `os.fdopen(fd, "wb")`), then close;
- keep the existing `except OSError -> SystemExit("cannot create backup ...")`
  framing so the error contract is unchanged.

`next_backup_path` stays as a public helper (it is exported in `__all__` and
may be referenced elsewhere), but `backup_existing_file` no longer routes its
write through the check-then-copy path; it uses `_open_exclusive_backup`. This
keeps the exported surface stable while closing the window in the one place
that actually writes.

Tradeoff: reading the source mode with `destination.stat()` follows a symlink,
but the caller (`_require_file_destination` / install apply path) has already
established `destination.is_file()` and the backup is only taken before
overwriting a real file; a symlinked destination is a separate conflict status
handled upstream and never reaches `backup_existing_file`.

## A-011 — umask read once (fileops.py:68)

`default_file_mode` calls `os.umask(0)` and restores it on **every** installed
file. `os.umask` is process-global; the set-and-restore momentarily exposes a
0 umask to any concurrent thread. The installer is single-threaded, so this is
latent, but the per-write churn is needless. There is no portable `getumask`,
so the only way to read the umask is the set-and-restore dance — do it **once**
at import into a module constant:

```python
def _read_process_umask() -> int:
    current = os.umask(0)
    os.umask(current)
    return current


_PROCESS_UMASK = _read_process_umask()


def default_file_mode(*, executable: bool = False) -> int:
    base_mode = 0o777 if executable else 0o666
    return base_mode & ~_PROCESS_UMASK
```

The one set-and-restore runs at module import (single-threaded), documented in
a comment. Tradeoff: if a caller mutates the process umask after import, the
constant is stale — the installer never does, and capturing the ambient umask
at startup is the correct semantic for a CLI. This is the "read once into a
module constant" option the prd names, not the "document the mutation" fallback.

## A-008 — `--platform` help vs selection (fileops.py:123, install.py:100)

In `selected_files`, `ALWAYS_INSTALL`/`IF_NOT_EXISTS` files are appended before
the platform filter is consulted (lines 137–139), so `--platform` does **not**
restrict them. The `--platform` help says "Install only this platform's
skills," which reads as "nothing else." Today this is latent: all manifest
rows (currently 544, verified via `manifest.json`) are `IF_ANCHOR_EXISTS`; no
always/if-not-exists row carries a platform
distinction.

Decision: **amend the help**, do not move the filter. Always-install and
if-not-exists files are pack-wide infrastructure (toolchain scripts, journal
scaffolding) that must land regardless of the selected platform; filtering them
out under `--platform` would break every install that uses the flag. The honest
fix is to state the exception:

- `--platform` help → "Install this platform's anchored skills, even if its
  anchor directory is missing (repeat to select several). Pack-wide
  always-install and if-not-exists files are installed regardless of this
  filter."

Lock the contract with a test: `selected_files` given a `--platform` filter and
a synthetic `ALWAYS_INSTALL`/`IF_NOT_EXISTS` file still selects it, while an
`IF_ANCHOR_EXISTS` file of a non-selected platform is skipped. This documents
the intended behavior so a future "fix" that moves the filter fails a test.

## Testing

- **A-013:** import `management` and patch `management.subprocess.run` with
  `side_effect=subprocess.TimeoutExpired(cmd="git", timeout=60)`; assert
  `_run_git` raises `SystemExit` whose message contains `timed out`. A
  `FileNotFoundError` variant asserts `git not found`.
- **A-019:** in a temp dir, write a destination file with mode 0600 and
  distinctive content; call `backup_existing_file(..., backup=True,
  dry_run=False)`; assert the `.bak` exists, is **not** a symlink, has content
  equal to the source, and mode `0o600` (not 0644). Second: pre-create the
  `.bak` as a symlink to an outside sentinel file; assert the backup is written
  to `.bak1` (or a fresh non-symlink path) and the sentinel is untouched —
  proving `O_NOFOLLOW`/`O_EXCL` did not clobber the symlink target.
- **A-011:** with `patch.object(fileops, "_PROCESS_UMASK", 0o022)`,
  `default_file_mode()` returns `0o644` and `default_file_mode(executable=True)`
  returns `0o755`; assert no `os.umask` call happens during
  `default_file_mode` (`patch.object(fileops.os, "umask")` asserted not
  called).
- **A-008:** `selected_files` contract test above.

## Release discipline

- Bump `manifest.json` version 0.66.13 → 0.66.14.
- Prepend a `## 0.66.14 - 2026-08-05` section to `CHANGELOG.md` describing the
  four hardening fixes.
- The generator surfaces (`generate-skill-surfaces.py --check`) read the
  manifest version; run `--check` and regenerate if it flags drift.

## Out of scope

- No change to the source-trust gate or the TOCTOU follow-up already tracked
  as `followup/toctou-task-record`.
- No change to `next_backup_path`'s exported signature.
- No new install modes or platform registry changes.

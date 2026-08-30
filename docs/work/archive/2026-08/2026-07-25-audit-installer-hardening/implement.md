# Implement — Installer subprocess and file-handling hardening

Ordered steps. Validate after each code change; full `make check` before ship.

## Step 1 — A-013 `_run_git` timeout (installer/management.py)

- Add module constant `GIT_TIMEOUT_SECONDS = 60` near the other constants.
- In `_run_git`, pass `timeout=GIT_TIMEOUT_SECONDS` to `subprocess.run` and wrap:
  - `except subprocess.TimeoutExpired: raise SystemExit(f"error: git {' '.join(args)} timed out") from None`
  - `except FileNotFoundError: raise SystemExit("error: git not found") from None`
- Leave the `returncode != 0` branch unchanged.

## Step 2 — A-011 umask read once (installer/fileops.py)

- Add `_read_process_umask()` (set-and-restore once) and
  `_PROCESS_UMASK = _read_process_umask()` at module scope, with a comment that
  the one mutation runs at single-threaded import time.
- Rewrite `default_file_mode` to `base_mode & ~_PROCESS_UMASK` with no
  `os.umask` call.

## Step 3 — A-019 symlink-safe mode-preserving backup (installer/fileops.py)

- Add `_open_exclusive_backup(root, destination)` that loops `.bak`, `.bak1`,
  … attempting `os.open(candidate, O_CREAT|O_EXCL|O_WRONLY|O_NOFOLLOW, 0o600)`
  FIRST, advancing on `FileExistsError`; only after a successful create call
  `validate_resolved_target_path(root, candidate, "backup path")` (the fresh
  file can no longer be diverted by a symlink), then `return (fd, candidate)`.
  Validate-before-open is wrong here: the validator follows symlinks and would
  hard-fail on an escaping `.bak` symlink instead of skipping it (concern C-1).
- Rewrite `backup_existing_file`'s write path:
  - `source_mode = destination.stat().st_mode & 0o777`
  - `fd, backup_path = _open_exclusive_backup(root, destination)`
  - `os.fchmod(fd, source_mode)`; stream bytes with
    `with open(destination, "rb") as src, os.fdopen(fd, "wb") as dst: shutil.copyfileobj(src, dst)`
  - keep the `except OSError -> SystemExit("cannot create backup ...")` framing;
    ensure the fd is closed on the error path (fdopen owns it once wrapped, so
    do the fchmod before fdopen or guard with try/os.close).
- `next_backup_path` stays unchanged (still exported).

## Step 4 — A-008 `--platform` help (install.py) + contract test

- Amend the `--platform` help to state that pack-wide always-install and
  if-not-exists files are installed regardless of the filter (see design).
- No change to `selected_files` logic.

## Step 5 — Tests (tests/)

Locate the existing installer test module(s) (`tests/test_*install*`,
`tests/test_fileops*`, or similar) via grep; add cases there rather than a new
file unless none fits.

- A-013: import `management`, patch `management.subprocess.run` with
  `TimeoutExpired` and with `FileNotFoundError`; assert `SystemExit` containing
  `timed out` / `git not found`.
- A-019: mode-preservation test (dest 0600 → `.bak` 0600, not symlink, content
  matches) and symlink-safety test (pre-existing `.bak` symlink → write lands on
  a fresh non-symlink path, sentinel target untouched).
- A-011: `patch.object(fileops, "_PROCESS_UMASK", 0o022)` → `default_file_mode()`
  == 0o644, `default_file_mode(executable=True)` == 0o755; and
  `patch.object(fileops.os, "umask")` asserted not called during the call.
- A-008: `selected_files` with a platform filter keeps an ALWAYS_INSTALL and an
  IF_NOT_EXISTS synthetic file, skips a non-selected IF_ANCHOR_EXISTS file.

## Step 6 — Release discipline

- `manifest.json`: version 0.66.13 → 0.66.14.
- `CHANGELOG.md`: prepend `## 0.66.14 - 2026-08-05` with the four fixes.
- Run `python .github/scripts/generate-skill-surfaces.py --check`; if it flags
  drift from the version bump, regenerate and stage the generated surfaces.

## Step 7 — Validate + mark ACs

- `make check` exit 0 (unittest+coverage, ruff, mypy, generator `--check`,
  release gate — the gate now REQUIRES the version bump because installer paths
  changed; confirm it reports the bump as satisfied, not "no payload change").
- Mark the three prd ACs:
  - timeout + backup mode/symlink tests present (Steps 1, 3, 5).
  - no per-write `os.umask` remains (Step 2).
  - `--platform` help/selection consistent, locked by test (Step 4/5).

## Validation commands

- `make check`
- `python3 -c "import ast; ast.parse(open('installer/fileops.py').read()); ast.parse(open('installer/management.py').read()); print('syntax OK')"`
- `PYTHONPATH=tests .venv/bin/python -m unittest <installer test module> -v`

## Rollback

Each finding is an isolated hunk in one function; revert independently. The
version/changelog bump is the only cross-file coupling — reverting the code
also requires reverting the bump so the release gate stays consistent.

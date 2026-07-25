# Installer subprocess and file-handling hardening

## Goal

The installer's edge behavior matches the rest of the pack: bounded subprocesses, symlink-safe mode-preserving backups, no hidden umask mutation, and a --platform flag that does what its help says.

## Requirements

- installer/management.py `_run_git`: add timeout=60 and convert TimeoutExpired into the existing clean SystemExit error message (parity with every other subprocess wrapper in the repo). [A-013]
- Backups: create the .bak via O_CREAT|O_EXCL|O_NOFOLLOW and copy into the descriptor, preserving the source file's mode (closes the check-then-use window and the umask-default 0644 leak). [A-019]
- default_file_mode: read the umask once into a module constant instead of os.umask(0)-and-restore per installed file, or explicitly document the temporary mutation. [A-011]
- --platform: apply the platform filter before the ALWAYS_INSTALL/IF_NOT_EXISTS shortcut in selected_files, or amend the --platform help to state the exception (latent today; all 378 rows are if-anchor-exists). [A-008]
- Installer behavior is consumer contract: follow the release bump/changelog discipline.

## Acceptance Criteria

- [ ] Tests cover the timeout conversion and backup mode/symlink behavior.
- [ ] No per-write os.umask mutation remains (or the docstring documents it).
- [ ] --platform contract is consistent between help text and selection logic (test or amended help).

## Notes

- Audit findings: A-013, A-019, A-011, A-008 (P3/S) — .trellis/audit/report-2026-07-25.md.
- Evidence: installer/management.py:110, :164, :190; installer/fileops.py:409, :181, :309, :68, :137; install.py:100.

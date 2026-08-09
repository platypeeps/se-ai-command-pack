# Implement: fd-pinned source-trust gate

Execution checklist for the design in `design.md`. Work happens on one
feature branch; the sd-ship chain owns publish-to-merge.

## Ordered steps

1. [ ] `installer/management.py`: add `SourceHandle` (path, fd, close) and
   the tier predicate — tier 1 requires all of: `geteuid` callable,
   `O_DIRECTORY`, `os.fchdir`, `os.stat in os.supports_dir_fd`,
   `os.open in os.supports_dir_fd`,
   `os.stat in os.supports_follow_symlinks`; tier 2 requires `geteuid` +
   `O_DIRECTORY` + `fchdir` (missing only dir_fd/follow_symlinks
   members); everything else (no `geteuid`, or no `O_DIRECTORY`/`fchdir`)
   is tier 3 = today's path-based flow.
2. [ ] Rework `_source_checkout` to open the directory fd before the trust
   checks and run them fd-relative per the design tiers, **in the current
   refusal order** (manifest/name → `.git` shape → ownership → confirm):
   dir_fd-relative manifest read; `install.py` stat with
   `follow_symlinks=False` requiring a regular file (symlink → existing
   "unavailable" refusal); `dir_fd` + `follow_symlinks=False` `.git` stat
   with the new symlinked-`.git` refusal; `.git`-file `gitdir:` one-hop
   target validation (exists + current-user-owned, new refusal message per
   design); fstat ownership. Preserve every existing refusal message
   byte-for-byte; close the fd on every refusal path; return a
   `SourceHandle`. Tier 3 keeps today's path checks plus the
   `Path.lstat()` symlink rejections and path-based `gitdir` validation.
3. [ ] Rework `_run_git` to accept `SourceHandle | Path` (Path keeps
   today's `git -C <path>` shape — the three existing `_run_git` direct
   tests stay valid) and the three `subprocess.run` installer invocations
   in `update_pack` to run `install.py` relative with
   `pass_fds=(fd,)` + `preexec_fn=lambda: os.fchdir(fd)` (the callable —
   never the call's return value) on tier 1/2; tier 3 keeps absolute
   paths. Wrap the flow in `try/finally handle.close()`.
4. [ ] Update `_owned_by_current_user` docstring (no longer the `.git`
   authority on tier 1/2); keep the function for tier 3.
5. [ ] Tests in `tests/test_management.py` (extend `UpdateSourceTrustTest`):
   - symlinked `.git` refused, no git/exec (spy on `subprocess.run`);
   - symlinked `install.py` refused ("unavailable"), no git/exec;
   - `.git`-file `gitdir` validation: dangling and foreign-owned targets
     refused with the new message; `test_accepts_git_file_worktree`
     fixture updated to a real same-user `gitdir` target;
   - pinning proof: rename-aside + decoy, fd still reads original
     (`st_ino` compare + sentinel read through `dir_fd`);
   - fchdir ordering proof: a `sys.executable -c` child run through the
     handle-based subprocess helper prints a cwd inside the pinned
     directory with default `close_fds`;
   - unmocked wiring proofs per the design's validation plan: real
     `git rev-parse --show-toplevel` through `_run_git(handle)` after a
     decoy swap reports the original directory; full unmocked
     `update_pack` with a sentinel-writing stub `install.py` and a
     swap staged at the test seam shows the child resolved inside the
     pinned directory; a wrapping (non-replacing) `subprocess.run` spy
     asserts relative argv + `pass_fds` + `preexec_fn` on every handle
     call;
   - fd-closure assertions on every `_source_checkout` refusal path;
   - tier-2 fallback (capability-set members removed), tier-3 fallback
     (delete `geteuid`), and tier-3 with `geteuid` present but
     `O_DIRECTORY`/`fchdir` absent (ownership check still applied) behave
     per design;
   - all existing `UpdateSourceTrustTest` cases pass unchanged
     (refusal-order preservation makes this hold); `UpdateCommandTest`
     argv-shape assertions may be updated only where the handle path
     changes the git invocation to `-C .`.
6. [ ] `CHANGELOG.md` entry + `manifest.json` version bump (release payload
   gate enforces it).
7. [ ] Focused run: `make test` (or targeted
   `python -m unittest tests.test_management`), `ruff` on changed files,
   then full `make check`.

## Validation commands

- `.venv/bin/python -m unittest tests.test_management -v`
- `make check`

## Review gates

- Planning adversarial review before `task.py start` (this document's
  batch).
- sd-ship Stage 2 review loop on the PR.

## Rollback

Single self-contained commit series on the feature branch; revert the
branch or drop the PR. No data migration, no cross-repo effects.

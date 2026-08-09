# Design: fd-pinned source-trust gate for install.py update

Follow-up to A-017 (PR #143), which added the source-trust gate in
`installer/management.py:_source_checkout` and accepted the
time-of-check/time-of-use window as a residual. This design closes the
directory-identity half of that window on POSIX and documents the exact
residual that remains per platform tier.

## Threat model recap and the measured window

The recorded `sourceRoot` comes from a plain-JSON provenance receipt with no
integrity protection. `update_pack` runs `git -C <sourceRoot>` (status, and
fetch+rev-list or pull) and executes `<sourceRoot>/install.py` (plan and
apply, or dry-run plan). Today every one of those uses re-resolves the path
from scratch, so after `_source_checkout`'s checks pass, an attacker who
can replace `source_root` (or its `.git`) redirects every later
re-resolution to content that was never checked.

**Measurement (defined up front, per the PRD):** the metric is **external
`source_root` pathname resolutions between the trust check and the last use
in one `update` run** — it deliberately excludes lookups of entries *inside*
the checkout (`.git`, `install.py`), which git and Python re-resolve
relative to the pinned directory and which are covered by the residual
section below. Before: **4** in each mode (non-dry-run: `status`, `pull`,
plan exec, apply exec; dry-run: `status`, `fetch`, `rev-list`, plan exec).
After, on tier-1 platforms: **0** — every use goes through one directory
file descriptor opened once, before the checks run.

## Approach: check and use one held handle

`_source_checkout` opens the resolved `source_root` once with
`os.open(path, os.O_RDONLY | os.O_DIRECTORY)` and returns a handle object
that owns that fd for the rest of the update. All trust checks then run
against the fd (`os.fstat`), or dir_fd-relative to it, and all git/exec use
chdirs into the fd — so the object that was checked is the object that is
used, whatever happens to the path afterwards.

New module-level helper class in `installer/management.py`:

```python
class SourceHandle:
    """A source checkout pinned to an open directory fd (POSIX tiers)."""
    path: Path          # resolved path, for messages and Windows fallback
    fd: int | None      # None on the Windows/path fallback tier
    def close(self) -> None: ...
```

`update_pack` wraps the whole flow in `try/finally handle.close()`.

### Trust checks, fd-relative

Order inside `_source_checkout` (tier-1):

1. Resolve `source_root` from provenance exactly as today (unchanged
   messages for the provenance/manifest/name refusals).
2. `fd = os.open(source_root, os.O_RDONLY | os.O_DIRECTORY)` — an `OSError`
   here (not a directory, vanished, permission) refuses with the existing
   "recorded source checkout is unavailable" error. The final path component
   may be a symlink to a directory; that is fine — identity is pinned at
   open time, and ownership of the *opened* directory is what is checked
   next. Every refusal raised after this point closes the fd first
   (`try/except` around the check block), so a refused update leaks no
   descriptor.
3. `manifest.json` / `install.py` presence and pack-name checks run
   dir_fd-relative here, preserving today's refusal precedence (they
   precede the git checks in the current code). `install.py` is checked
   with `os.stat("install.py", dir_fd=fd, follow_symlinks=False)` and must
   be a **regular file**: today's `Path.is_file()` follows symlinks, and a
   symlinked `install.py` would let the later relative exec escape the
   pinned directory. A symlinked or missing `install.py` refuses with the
   existing "recorded source checkout is unavailable" message (no new
   message needed — the checkout is unusable either way).
4. `.git` entry: `os.stat(".git", dir_fd=fd, follow_symlinks=False)` — this
   stays **before** the ownership refusal, matching the current
   check order so `test_refuses_non_git_foreign_source` keeps seeing
   "not a git repository".
   - **Symlink decision (PRD): reject.** If `stat.S_ISLNK(st.st_mode)`,
     refuse with a new explicit error
     (`error: recorded source checkout has a symlinked .git: <path>`), and
     no git/exec runs. Legitimate checkouts have a `.git` directory
     (primary) or a regular `.git` file (worktree/submodule pointer); a
     symlinked `.git` re-points the repository outside the checked
     directory and is exactly the redirection this gate exists to refuse.
   - A `.git` **directory** is accepted (unchanged behavior), with
     ownership checked from the same `dir_fd` stat result
     (`st_uid == geteuid()`), replacing the old path-based
     `_owned_by_current_user(git_entry)` that followed symlinks.
   - A `.git` **regular file** (worktree/submodule pointer) is accepted
     only after its redirection target is validated — a deliberate
     tightening of A-017, which accepted any `.git` file without looking
     at the `gitdir` it points to (the existing fixture even uses a
     dangling `gitdir: /elsewhere/.git`). The file is read through
     `dir_fd`; it must match `gitdir: <path>` on its first line; the
     target (resolved against the pinned directory when relative) must
     exist and pass the same current-user-ownership check. A malformed,
     dangling, or foreign-owned `gitdir` target refuses with a new
     explicit error
     (`error: recorded source checkout .git file points to an unverified
     gitdir: <target>`), and no git/exec runs. No recursion into
     `commondir` or nested pointers — one hop, validated, is the bounded
     contract. The `test_accepts_git_file_worktree` fixture moves to a
     real same-user `gitdir` target, and a new refusal test covers the
     dangling/foreign case.
5. Directory ownership: `os.fstat(fd).st_uid == os.geteuid()` — the fd
   cannot be swapped, unlike the previous `Path.stat()` by path. Combined
   with the `.git` stat's uid, this preserves the current single
   "not owned by the current user" refusal.
6. Same-checkout / `--confirm-source` gate: unchanged semantics. The
   comparison stays on the resolved path (identity-by-path is what the
   prompt is about), and the A-017 refusal messages stay byte-identical.

### Use, fd-relative

- `_run_git(handle, *args)` accepts `SourceHandle | Path`. With a handle on
  tier 1/2 it runs `["git", "-C", ".", *args]` with
  `pass_fds=(handle.fd,)` plus `preexec_fn=lambda: os.fchdir(handle.fd)`;
  with a bare `Path` (tier 3 and the existing direct-call tests) it keeps
  today's `["git", "-C", str(path), *args]`. `pass_fds` makes the fd's
  survival into the callback a documented contract rather than a CPython
  implementation detail (the public `subprocess` docs only guarantee both
  `preexec_fn` and fd closing happen before exec, and recommend `pass_fds`
  for descriptors that must outlive `close_fds`); a dedicated test still
  proves the plumbing by running a `sys.executable -c` child that prints
  its cwd through the same helper with default `close_fds`. `preexec_fn`
  is unsafe in multi-threaded parents and unsupported in subinterpreters;
  `install.py update` is a single-threaded CPython CLI entry point, which
  the code comments state as the precondition.
- The installer execs become
  `subprocess.run([sys.executable, "install.py", ...], preexec_fn=...)` with
  the same fchdir — the script is resolved by the child inside the pinned
  directory, not by a fresh path walk.
- `--root` and every other installer argument still pass absolute paths for
  the *target* repository; only the source checkout's own resolution is
  pinned.

### Platform tiers and fallbacks

- **Tier 1 (POSIX with full fd primitives — Linux, macOS):** full
  fd-pinned checks and use as above. Gate (`_fd_pinning_supported()`), all
  of: `os.geteuid` callable, `os.O_DIRECTORY` present, `os.fchdir` present,
  `os.stat in os.supports_dir_fd`, `os.open in os.supports_dir_fd`, and
  `os.stat in os.supports_follow_symlinks` — each primitive the tier
  actually uses, since Python exposes these as independent capability sets.
- **Tier 2 (POSIX with `geteuid`, `O_DIRECTORY`, and `fchdir`, but missing
  a `supports_dir_fd`/`supports_follow_symlinks` member):** the directory
  fd is still opened and ownership still checked via `fstat`, and git/exec
  still fchdir into it; only the `.git`/manifest checks fall back to
  path-based access (with `Path.lstat()` for the symlink rejections and a
  path-based `gitdir` validation, preserving those decisions). Residual:
  the entry checks themselves can race, but the execution directory cannot
  be swapped.
- **Tier 3 (everything else — Windows, no `geteuid`, or a POSIX without
  `O_DIRECTORY`/`fchdir`):** the flow is today's path-based behavior:
  ownership is still checked by path whenever `geteuid` exists (exactly the
  current code), the same-checkout / `--confirm-source` gate remains the
  trust guarantee, and the symlink and `gitdir` rejections still apply via
  `Path.lstat()` and path reads (all portable). Residual: the original
  A-017 window, explicitly accepted for this tier.

Tier selection is one small predicate (`_fd_pinning_supported()`), decided
once per update run, and the chosen tier is not user-visible except through
the documented refusals.

### Residual after this change (stated explicitly)

- **Tier 1 — what is closed:** the *directory identity* is check-equals-use.
  Swapping `source_root` (or any parent path component) after the checks has
  no effect: git and the installer children run inside the fd-pinned
  directory, and zero external pathname re-resolutions remain.
- **Tier 1 — what remains open:** entries *inside* the pinned directory are
  not pinned. `git -C .` re-looks-up `.git`, and the child Python re-opens
  `install.py`, after the checks; an attacker with write access **inside**
  the checkout (the owner, or a group/ACL writer on an owner-writable tree)
  can still swap those entries between check and use. Ownership is the
  trust anchor A-017 chose, and it does not exclude group/ACL writers; this
  design narrows the attack surface from "anyone who can swap the path"
  to "principals who can already write inside the owned checkout", and
  states that plainly instead of claiming full closure. Pinning interior
  entries would require fd-relative re-implementation of git itself and is
  out of scope. The path string printed in messages may go stale if the
  directory is moved after open; execution is unaffected.
- **Tier 2:** execution is pinned to the fd opened before the checks, but
  the `.git`/manifest checks are path-based, so check and use can diverge
  in *both* directions: the checks may validate a decoy while execution
  uses the pinned original (whose only fd-verified property is ownership),
  or race on the `.git` entry. The tier-2 guarantee is therefore
  "execution confined to a current-user-owned directory chosen before the
  checks", not check-equals-use. Documented, and exercised by the
  tier-fallback tests.
- **Tier 3:** unchanged A-017 residual, per the PRD's no-regression
  requirement.

## Compatibility

- All existing A-017 refusal messages and exit behavior are preserved
  byte-for-byte; the new refusals are exactly two — the symlinked-`.git`
  error and the unverified-`gitdir` error — plus the reuse of the existing
  "unavailable" message for a symlinked `install.py`.
- `_owned_by_current_user` remains for the tier-3 path; its docstring drops
  the "follows symlinks" caveat for `.git` since tier-1/2 now lstat it.
- No new dependencies; stdlib `os`/`stat` only. No CLI surface change.

## Validation plan

Unit tests in `tests/test_install_update.py` (or the module that already
covers A-017; extend, do not fork):

- **Symlink rejection (AC2):** fixture checkout whose `.git` is a symlink to
  a real repo's `.git` — update refuses with the new message; a spy on
  `subprocess.run`/`_run_git` proves no git/exec ran.
- **A-017 regression (AC3):** existing refusal tests (missing provenance,
  missing checkout, name mismatch, non-repo, foreign ownership, relocated
  without confirm) pass unchanged; run the module's full suite.
- **Pinning proof (AC1's mechanism):** open the handle, then rename the
  original directory aside and put a decoy at the recorded path; a
  dir_fd-relative read through the handle still sees the original content
  (compare `os.fstat(handle.fd).st_ino` to the renamed directory's inode,
  and read a sentinel file through `dir_fd`). This demonstrates
  check-equals-use without needing a real race.
- **Production wiring proof (unmocked):** the mocked update tests could
  pass while one call site silently kept an absolute path, so two
  end-to-end tests run with **no** `_run_git`/`subprocess.run` mocks:
  1. real `git rev-parse --show-toplevel` through `_run_git(handle)` after
     the rename-aside + decoy swap must report the original (renamed)
     directory, not the decoy at the recorded path;
  2. a full `update_pack` run against a fixture git checkout whose stub
     `install.py` writes `os.getcwd()` and its own resolved `__file__` to a
     sentinel — after a decoy swap staged between `_source_checkout` and
     the exec (test seam: the swap runs inside a wrapped `_run_git`), the
     sentinel must show the child resolved inside the pinned directory.
  A spy that *wraps* (not replaces) `subprocess.run` additionally asserts
  every git/installer call in the handle path used relative argv,
  `pass_fds` containing the handle fd, and a `preexec_fn`.
- **Tier fallback:** monkeypatch the capability predicate's inputs to
  drive each ladder rung and assert the documented behavior (checks still
  run, path fallback used, no crash): emptied
  `os.supports_dir_fd`/`os.supports_follow_symlinks` → tier 2; deleted
  `geteuid` → tier 3; **`geteuid` present but `O_DIRECTORY`/`fchdir`
  absent → tier 3 with the ownership check still applied** (the
  previously undefined rung).
- **fd closure:** every refusal path of `_source_checkout` (unavailable,
  name mismatch, non-repo, symlinked `.git`, foreign-owned, unconfirmed
  relocation) closes the opened fd — asserted by tracking `os.open`
  results against `os.close` calls in each refusal test.
- Changelog + version bump (AC4): installer is a consumer contract — bump
  the pack version and add a changelog entry; the release payload gate
  enforces the bump.

# Harden install.py update source-trust TOCTOU window

## Goal

Close, or measurably shrink, the time-of-check/time-of-use gap in
`installer.management._source_checkout` between the source-trust checks
(git-repository existence, POSIX ownership, same-checkout/confirm) and the
subsequent `git` invocations and `install.py` execution against `source_root`.

## Background

A-017 (merged PR #143) added the source-trust gate but explicitly accepted the
TOCTOU window as a residual: an attacker who can swap `source_root` (or its
`.git`) between the ownership check and the git/exec use could still influence
what runs. The gate also follows a symlinked `.git` to its target via `stat`,
and treats any existing `.git` entry as proof of a git repository.

## Requirements

- Reduce reliance on re-resolving `source_root` by path after the trust check:
  prefer operating on a single stable handle (e.g. an opened directory fd via
  `os.open(..., O_DIRECTORY)` with `dir_fd`-relative git/exec, where the
  platform supports it) so the checked object is the used object.
- Decide and document the intended handling of a symlinked `.git` (reject via
  `lstat`, or validate the symlink's own ownership) rather than silently
  following it.
- Keep the same-checkout / `--confirm-source` guarantee and all existing
  A-017 refusal behavior intact; this is defense-in-depth, not a replacement.
- Preserve cross-platform behavior: no regression on platforms without an
  effective-uid primitive or without `dir_fd` support.

## Acceptance Criteria

- [x] Design records the chosen TOCTOU-narrowing approach and its platform
  fallbacks, with the residual (if any) stated explicitly — `design.md` tier
  ladder + per-tier residual section; metric: external `source_root`
  pathname re-resolutions 4 → 0 on tier 1.
- [x] Test: a `.git` symlink is handled per the documented decision (rejected
  or ownership-validated), with no git/exec on refusal — decision: rejected;
  `test_refuses_symlinked_git_entry` with `_fail_if_git_or_exec` spies.
- [x] Test: existing A-017 refusal and same-checkout/confirm paths still pass
  unchanged — pre-existing `UpdateSourceTrustTest` cases untouched;
  `unittest discover -p test_management.py`: 40 tests OK; full
  `make check`: 639 tests OK (skipped=1, pre-existing A-025 skip).
- [x] Changelog + version bump discipline applied (installer is consumer
  contract) — 0.67.2 → 0.68.0, dated CHANGELOG entry, release payload gate
  green.

## Notes

- Follow-up to A-017 (P2/S) — .trellis/audit/report-2026-07-25.md.
- Origin: PR #143 accepted-residual disposition (adversarial review C-2 and
  local review re-flags on installer/management.py:_source_checkout).
- Planning depth: **Complex — needs `design.md` and `implement.md` before `task.py start`.** A TOCTOU window is a concurrency contract: which handle is held, what is re-verified at use, and what the residual window is after the change. Security-sensitive, and 'measurably shrink' requires the measurement to be defined up front rather than asserted afterwards.
- Check-pass observations, accepted (theoretical, below fix threshold): a
  failing `os.fdopen` on the dir_fd-relative manifest read would leak the
  raw fd until the process-ending refusal (`management.py` ~:184); the
  unverified-gitdir refusal embeds the bounded, replace-decoded first line
  of the attacker-supplied `.git` file (terminal-escape surface consistent
  with existing path-embedding message style).

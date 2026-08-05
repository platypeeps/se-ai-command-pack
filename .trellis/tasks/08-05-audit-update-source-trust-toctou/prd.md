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

- [ ] Design records the chosen TOCTOU-narrowing approach and its platform
  fallbacks, with the residual (if any) stated explicitly.
- [ ] Test: a `.git` symlink is handled per the documented decision (rejected
  or ownership-validated), with no git/exec on refusal.
- [ ] Test: existing A-017 refusal and same-checkout/confirm paths still pass
  unchanged.
- [ ] Changelog + version bump discipline applied (installer is consumer
  contract).

## Notes

- Follow-up to A-017 (P2/S) — .trellis/audit/report-2026-07-25.md.
- Origin: PR #143 accepted-residual disposition (adversarial review C-2 and
  local review re-flags on installer/management.py:_source_checkout).

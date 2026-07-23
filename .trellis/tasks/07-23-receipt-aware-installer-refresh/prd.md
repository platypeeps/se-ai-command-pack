# Receipt-aware installer refresh

## Goal

Allow an installed payload that still matches the prior installer receipt to
refresh to new Claude, Codex, or shared-agent bytes without `--force`, while
preserving the conflict boundary for user-modified files.

## Background

The installer currently compares a destination only with the current payload.
When a release changes installer-generated platform variants, every pristine
file from the previous release therefore appears to be a conflict even though
`provenance.json` records the exact bytes the installer previously wrote.

## Requirements

- A normal install or refresh must classify a differing regular file as
  installer-managed only when its sha256 matches that target's prior
  `provenance.json` entry.
- A vouched installer-managed file must be updated atomically without
  `--force`, without creating a backup, and reported as `updated`.
- Missing, malformed, unreadable, or symlinked provenance; absent or invalid
  target hashes; symlink destinations; and destination/hash mismatches must
  remain conflicts.
- `if-not-exists` and force-preserved targets must retain their existing
  preservation semantics even if a receipt claims them.
- The plan-before-apply boundary must revalidate a vouched destination before
  writing so a concurrent user edit is never overwritten.
- The behavior must use the platform-neutral receipt mechanism; Claude and
  Codex are required regression cases, not special-cased paths.
- Dry-run, filtered refresh, update, removal, and receipt rewriting must retain
  their existing contracts.

## Acceptance Criteria

- [x] Pristine prior-version Claude and Codex files update without `--force`
      and the refreshed provenance records the new bytes.
- [x] A file edited after installation remains a conflict and no selected file
      or receipt is written.
- [x] Missing or untrusted provenance cannot authorize an overwrite.
- [x] A destination changed after preflight is reclassified safely and left
      untouched.
- [x] Existing force, backup, symlink, preservation, filtering, retirement,
      and removal tests remain green.
- [x] User documentation explains when normal refresh updates versus conflicts.
- [x] The release version and changelog describe the installer behavior change.
- [x] Focused tests, `make check`, and `git diff --check` pass.

## Verification

- Focused installer and provenance suites: 91 tests passed.
- Ruff passed for the changed Python surfaces.
- Mypy passed for `install.py` and `installer/`.
- `make check`: 515 tests plus generation, lint, type, and release gates passed.
- Repeated `make generate` was idempotent; `git diff --check` passed.

## Out of Scope

- Treating arbitrary Claude or Codex user customizations as installer-owned.
- Adding a new receipt schema or changing the manifest schema version.
- Creating automatic `.bak` files for receipt-vouched updates.

# Design: receipt-aware installer refresh

## Boundary

Keep ownership detection in the existing generic installer path. Read prior
file hashes with `read_existing_provenance_files()` and pass only selected,
vouchable target hashes into `install_file()`. Do not add platform-name checks.

## Classification contract

For an occupied regular-file destination:

1. If its bytes equal the current source, return `unchanged`.
2. If its install policy preserves existing content, return `preserved`.
3. If `--force` is active, retain the existing overwrite/backup behavior.
4. Otherwise, if its sha256 equals the prior provenance hash, plan or perform
   an atomic write and return `updated`.
5. Otherwise return `conflict`.

Symlinks never enter the provenance-vouched update branch. Missing or invalid
provenance naturally provides no matching hash and therefore fails closed.
Receipt files and force-preserved targets remain excluded through
`never_vouched_targets()`.

## Plan/apply data flow

Extend `InstallResult` with the destination digest observed during a planned
`updated` result. Applying that plan re-hashes the destination and reuses the
planned source bytes only when the digest still matches. If it does not, the
normal classifier runs again against the original vouched hash and returns a
conflict for concurrent drift.

This preserves the existing guarantees that all selected payload files are
planned before the first write and source changes after planning cannot mix
payload versions.

## Compatibility

No receipt schema change is needed: prior releases already store
`sha256:<hex>` values per target. Old, missing, malformed, and partial receipts
continue to load conservatively. `updated` is already a public install status
and is already included in provenance-vouchable statuses.

## Rollback

The implementation is isolated to installer classification and documentation.
Reverting the code restores the old force-required behavior; receipt files
written by the new version remain readable by old versions.

# Implement se-tutorial Implementation Plan

## Execution Order

1. Add platform/version/safety fixtures and failing tests for tutorial contracts and execution labels.
2. Implement audience/outcome/prerequisite resolution and incremental checkpoint step schema.
3. Add expected output, recovery/rollback, secret/destructive safeguards, final validation, and test inventory.
4. Integrate optional profile calibration, register under Create, add docs/release metadata, and regenerate.
5. Run focused/full checks and inspect representative tutorials.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manually exercise missing tools, macOS/Linux divergence, stale API, destructive
  command, secret placeholder, nondeterministic output, partial verification, and cleanup.

## Documentation And Spec Updates

Document execution-state vocabulary, checkpoint schema, safety/rollback rules,
version/date citations, profile limits, and final verification inventory.

## Review Notes

Confirm a reader can verify every major checkpoint and no untested behavior is
presented as executed or working.

## Follow-Ups

Publishing and execution on remote reader environments remain separate capabilities.

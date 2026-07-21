# Implement se-runbook Implementation Plan

## Execution Order

1. Add procedure fixtures and failing tests for step state, mutation authority, and safety fields.
2. Implement scope/preflight and ordered action/verification/failure/decision schema.
3. Add rollback/recovery, partial-state reconciliation, secret/destructive safeguards, ownership, and staleness.
4. Register under Operate, add shared references, docs/release metadata, and regenerate.
5. Run focused/full checks and inspect representative runbooks.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manually exercise missing access, partial failure, stale syntax, destructive target,
  no rollback, secret handling, unsupported version, and proposed-only recovery.

## Documentation And Spec Updates

Document execution-state vocabulary, step/mutation contract, safeguards, recovery
claims, validation metadata, stale warnings, and non-execution boundary.

## Review Notes

Confirm every mutation has authority, bounded scope, expected result, verification,
and failure handling.

## Rollback Points

- Revert the single feature commit before PR publication if focused or full
  validation exposes a contract conflict.
- Before merge, restore the prior release metadata and regenerate the manifest
  if the skill must be withdrawn without disturbing unrelated mainline work.
- After merge, use a follow-up revert PR; do not rewrite shared branch history.

## Follow-Ups

Runbook execution and incident-command orchestration remain separate capabilities.

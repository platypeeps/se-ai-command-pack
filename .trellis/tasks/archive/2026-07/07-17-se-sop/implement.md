# Implement se-sop Implementation Plan

## Execution Order

1. Add practice/policy fixtures and failing tests for provenance states, controls, and exceptions.
2. Implement scope, roles, routine procedure, outputs/records, and testable completion criteria.
3. Add control/guidance separation, proposed-state lane, exceptions/escalation, document control, and runbook routing.
4. Register under Operate, add shared references, docs/release metadata, and regenerate.
5. Run focused/full checks and inspect generated SOPs.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manually exercise conflicting practice, undocumented exceptions, unsupported
  compliance language, stale content, proposed improvement, and event-driven recovery.

## Documentation And Spec Updates

Document provenance states, mandatory controls versus guidance, exception handling,
document control, compliance evidence, and SOP/runbook boundary.

## Review Notes

Verify operative steps reflect observed/approved current practice and every control
has an observable compliance record or check.

## Follow-Ups

Policy approval, process enforcement, and staff assignment remain separate work.

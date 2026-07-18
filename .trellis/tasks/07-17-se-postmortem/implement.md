# Implement se-postmortem Implementation Plan

## Execution Order

1. Add incident fixtures and failing tests for timeline evidence and analytic categories.
2. Implement scope/source inventory, expected/actual/impact, and conflict-aware timeline.
3. Add causal/safeguard analysis, corrective action mapping, verification signals, and sensitivity handling.
4. Register under Improve, add shared references, docs/release metadata, and regenerate.
5. Run focused/full checks and inspect generated reports.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manually exercise incomplete/conflicting timelines, correlation-only claims,
  human error, unauthorized owners, sensitive data, and uncertain cause.

## Documentation And Spec Updates

Document category vocabulary, causal standard, blameless accountability, action/
verification schema, sensitivity handling, and distinction from `se-retro`.

## Review Notes

Trace impact, timeline, causes, and actions to evidence and confirm root-cause
language is withheld when causal support is inadequate.

## Follow-Ups

Incident response and action execution remain separate workflows.

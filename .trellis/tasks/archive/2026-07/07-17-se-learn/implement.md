# Implement se-learn Implementation Plan

## Execution Order

1. Add diagnostic, mastery, dependency, checkpoint, and time-constraint tests.
2. Implement goal/baseline contract and a small staged path.
3. Add adaptation, spaced review, resource-gap handling, and optional skill handoffs.
4. Register under Understand, add conditional source/safety coverage, docs/release, regenerate.
5. Run focused and full checks.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manual novice, experienced-gap, time-limited, inaccessible-resource,
  misconception, transfer failure, and approved scope-change cases.

## Documentation And Spec Updates

Document mastery signals, diagnostic evidence, adaptive checkpoint behavior,
and boundaries from explain/study-guide/Socratic review.

## Review Notes

Verify every stage has an observable outcome and that schedule pressure never
silently changes the target.

## Follow-Ups

Add persistent progress tracking or scheduling only as separate authorized capabilities.

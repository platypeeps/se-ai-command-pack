# Implement se-distill Implementation Plan

## Execution Order

1. Add fixtures and failing tests for size measurement, importance maps,
   invariants, ratios, conflicts, and unsafe-target escape.
2. Implement a single-corpus executive mode with loss ledger and attribution.
3. Add study/decision/technical modes and smallest-safe negotiation.
4. Register under Understand, fan in source standards, update docs/release, regenerate.
5. Run focused and full validation.

## Validation Plan

- `python3 -m unittest tests.test_skills tests.test_generate`
- `make generate`; `make check`; `git diff --check`
- Manual: short text, long mixed corpus, contradictory sources, technical spec,
  exact must-keeps, impossible 10%, and partial access.

## Documentation And Spec Updates

Document the 80/10 target as a heuristic, measurement disclosure, importance
map, smallest-safe behavior, and boundary from digest/summary.

## Review Notes

Try to locate every load-bearing source item in the output or loss ledger;
challenge any ratio claim that lacks consistent measurement.

## Follow-Ups

Add domain-specific invariant extractors only after real use demonstrates a
repeatable need; do not claim automatic semantic-retention measurement.

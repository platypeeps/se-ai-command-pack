# Implement se-evaluate Implementation Plan

## Execution Order

1. Add subject/rubric fixtures and failing tests for criterion validity and evidence states.
2. Implement rubric audit and criterion-level evidence/judgment/confidence ledger.
3. Add qualitative/numeric mode selection, aggregation, sensitivity analysis, improvements, and boundaries.
4. Register under Improve, add shared references, docs/release metadata, and regenerate.
5. Run focused/full checks and inspect generated evaluations.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manually exercise biased/dependent criteria, qualitative input, missing evidence,
  weight reversal, arbitrary threshold, incompatible comparator, and no overall score.

## Documentation And Spec Updates

Document rubric validation, evidence states, numeric preconditions, sensitivity,
bounded overall judgment, improvements, and decide/red-team boundaries.

## Review Notes

Confirm every judgment maps to criterion evidence and no missing evidence is
silently converted into a failed score.

## Follow-Ups

Certification, personnel assessment, and final decision authority remain out of scope.

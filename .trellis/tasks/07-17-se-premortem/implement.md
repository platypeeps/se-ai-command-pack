# Implement se-premortem Implementation Plan

## Execution Order

1. Add plan/failure fixtures and failing tests for lane coverage, evidence class, and tails.
2. Implement scope/failure definition, assumption inventory, and distinct failure-mode generation.
3. Add ordinal ranking, correlation, indicators, prevention/contingency, stop conditions, and residual risk.
4. Register under Improve, add shared references, docs/release metadata, and regenerate.
5. Run focused/full checks and inspect generated stress tests.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manually exercise a thin plan, common-cause failures, catastrophic low-likelihood
  risk, no mitigation, conflicting mitigations, and missing owners.

## Documentation And Spec Updates

Document scenario/evidence labels, ordinal ranking, tail treatment, mitigation-
indicator contract, residual risk, and non-approval boundary.

## Review Notes

Ensure speculative cases remain labeled and every mitigation has a named failure
mode plus an observable indicator.

## Follow-Ups

Security threat modeling and execution governance remain separate workflows.

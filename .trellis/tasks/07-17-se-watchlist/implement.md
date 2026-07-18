# Implement se-watchlist Implementation Plan

## Execution Order

1. Add multi-source checkpoint fixtures and failing delta/dedupe/exclusion tests.
2. Implement source coverage, checkpoint filtering, identity normalization, and deduplication.
3. Add relevance/novelty ranking, no-change output, safe explanations, and downstream route suggestions.
4. Integrate monitor/profile contracts, register under Operate, add docs/release metadata, and regenerate.
5. Run focused/full checks and inspect repeated-run behavior.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manually exercise initial baseline, same checkpoint twice, URL variants, stale feed,
  exclusions, empty delta, timezone edge, sensitive interest, and weak metadata.

## Documentation And Spec Updates

Document checkpoint and coverage semantics, dedupe identity, exclusion/ranking
rules, empty-result behavior, downstream routes, and monitor/brief boundaries.

## Review Notes

Confirm identical checkpoints cannot re-report unchanged items and coverage gaps
never masquerade as no material change.

## Follow-Ups

Scheduling, persistent checkpoints, subscriptions, and notifications remain host integrations.

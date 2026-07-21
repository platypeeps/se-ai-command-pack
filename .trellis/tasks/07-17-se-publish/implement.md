# Implement se-publish Implementation Plan

## Execution Order

1. Add source/destination fixtures and failing tests for traceability, adaptation, and write boundaries.
2. Implement source inventory and destination-neutral contracts for supported draft types.
3. Add adaptation/citation/sensitivity ledgers, accessibility checks, preview, and connector handoff.
4. Integrate outward-safe profile voice, register under Create, add docs/release metadata, and regenerate.
5. Run focused/full checks and inspect representative drafts.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manually exercise each destination, tight limits, sensitive/stale sources,
  citation conversion, promotional pressure, profile leakage, and a request to send.

## Documentation And Spec Updates

Document destination contracts, adaptation disclosure, citation/sensitivity checks,
profile scopes, preview requirements, and connector-specific write handoff.

## Rollback Points

- Before registration: remove the canonical `se-publish` template and focused
  tests if the contract cannot preserve source meaning across destinations.
- Before generation: revert the registry/reference additions and release
  metadata together; do not hand-edit generated manifest or catalog rows.
- Before shipping: require `make generate` idempotence, focused tests, the full
  repository gate, install fan-out audit, and a clean diff.

## Review Notes

Compare drafts to source load-bearing claims and ensure no adaptation broadens
audience, certainty, or personal disclosure without explicit support.

## Follow-Ups

Connector publication and media production remain separate capabilities.

# Implement se-diagram Implementation Plan

## Execution Order

1. Add synthetic fixtures and failing tests for form selection, ledgers,
   uncertainty/conflict, accessibility, and no-invention rules.
2. Create the canonical skill with `auto` selection and one simple Mermaid/brief path.
3. Add all supported forms, dense-view splitting, conservative Mermaid syntax,
   and tool-neutral fallback.
4. Register under Create, fan in source standards, add injection pins, update
   catalog/docs/release metadata, and regenerate.
5. Run focused tests, `make check`, and inspect generated payloads.

## Validation Plan

- `python3 -m unittest tests.test_skills tests.test_generate`
- `make generate`; `make check`; `git diff --check`
- Manual cases: cycle, async sequence, state guard, hierarchy, matrix, timeline,
  conflicting sources, dense model, inaccessible source, and renderer limitation.

## Documentation And Spec Updates

Document supported forms, evidence/inference notation, Mermaid fallback,
accessibility output, and the no-decoration/no-discovery boundaries.

## Review Notes

Trace every node/edge to the ledger, challenge causal arrows and temporal state,
and verify splitting preserves every relationship.

## Follow-Ups

Add raster/brand rendering only as a separate visual-production capability;
retain the tool-neutral specification as the authoritative artifact.

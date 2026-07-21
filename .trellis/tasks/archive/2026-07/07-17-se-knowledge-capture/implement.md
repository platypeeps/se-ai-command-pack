# Implement se-knowledge-capture Implementation Plan

## Execution Order

1. Add synthetic destination/schema records and failing duplicate/action-state tests.
2. Implement routing, multi-key lookup, action classification, and preservation-aware preview.
3. Add Obsidian/Notion mapping contracts, confirmation gates, idempotence, links, and partial-failure reporting.
4. Register under Operate, add shared references, docs/release metadata, and regenerate.
5. Run focused/full checks and inspect dry-run/apply payloads.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manually exercise create, managed update, skip, conflict, schema drift, unavailable
  connector, user edits, destructive replacement, dual-system request, and rerun.

## Documentation And Spec Updates

Document routing, identity matching, action states, preview/confirmation, managed
ownership, destination mappings, returned links, and connector-neutral limits.

## Review Notes

Verify every write has a preview and authority, and user-owned content survives
all non-destructive paths.

## Follow-Ups

Connector implementation and bidirectional synchronization remain separate work.

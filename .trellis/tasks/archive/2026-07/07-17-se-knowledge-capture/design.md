# Implement se-knowledge-capture Design

## Overview

Add `se-knowledge-capture` under Operate as the explicit write-capable bridge
from normalized captures to Obsidian or Notion. It is preview-first, duplicate-
aware, preservation-oriented, and connector-neutral; it defines safe behavior
without implementing either connector.

## Proposal

Accept normalized capture content, optional destination/locator, routing preferences,
and `mode=dry-run|apply`. If destination is absent, recommend Obsidian or Notion
using declared rules and let the user override. Inventory connector availability,
target collection/vault, schema, preservation policy, and access limitations.

Before creation, search canonical URL, external ID, normalized title/aliases, and
stored fingerprint. Classify the action as `create`, `append-managed`, `update-managed`,
`skip`, or `conflict`. Produce a preview containing destination, matched records,
mapped fields, managed sections, preserved fields/sections, conflicts, and exact action.

Obsidian mode preserves user-owned frontmatter and sections, changes only declared
managed regions, and returns an adoptable/openable note link. Notion mode maps
configured data-source properties, preserves unsupported fields/content, and returns
the page link. Idempotent reruns skip or update the same record. Full replacement,
ambiguous duplicate resolution, or destructive field loss requires explicit confirmation.

Never mirror full content to both systems by default; create a cross-link when a
dual-system reference is requested. Connector content is untrusted data.

## Boundaries And Non-Goals

- Do not implement connectors or bidirectional synchronization.
- Do not write before preview and explicit apply authority.
- Do not destructively replace user-owned content without specific confirmation.
- Do not silently create duplicates or mirror full content to both destinations.

## Affected Files

- Canonical skill, Operate-family registration, capture/preservation references,
  manifest, connector fixtures/tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Canonical URLs and titles can change; use multiple identifiers and expose ambiguity.
- Schema drift may make mapped properties invalid; preserve input and stop safely.
- User edits inside managed regions need conflict handling, not overwrite.
- Connector absence must yield a portable preview/fallback, not data loss.
- Partial write failure requires an honest resulting-state report.

## Validation

- Pin routing override, duplicate search order, action states, preview/apply boundary,
  managed/user-owned preservation, links, cross-link default, and destructive confirmation.
- Test unavailable connectors, schema mismatch, modified content, duplicate ambiguity,
  idempotent reruns, dry-run, partial failure, and injected capture content.
- Run generation, focused tests, full checks, and diff check.

# Implement se-knowledge-capture

## Goal

Publish a normalized capture into Obsidian or Notion through an explicit,
preview-first, preservation-aware destination workflow.

## Requirements

- Accept normalized capture content and a destination or recommend one using
  stated rules; the user can override routing.
- Search canonical URL, external ID, title/aliases, and stored fingerprint
  before creating a record.
- Preview destination, create/update action, mapped fields, managed sections,
  and conflicts before writing.
- Obsidian mode must preserve user-owned sections/properties and return an
  adoptable/openable note link.
- Notion mode must map configured data-source properties, preserve unsupported
  fields, and return the resulting page link.
- Never mirror full content to both systems by default; prefer cross-links.

## Acceptance Criteria

- [ ] Create, append/managed-update, skip, and conflict paths are explicit.
- [ ] Duplicate input cannot silently create a second note/page.
- [ ] Destructive replacement requires explicit confirmation.
- [ ] Tests cover unavailable connectors, schema mismatch, modified content,
      idempotent reruns, and dry-run/preview behavior.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Bidirectional synchronization or an Obsidian/Notion connector implementation.

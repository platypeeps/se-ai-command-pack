# Implement se-capture

## Goal

Add a universal capture workflow that converts a supplied URL, thread, page,
file, or pasted text into a normalized, destination-neutral knowledge artifact.

## Requirements

- Record source type, canonical locator, author/publisher when available,
  retrieval date, title, topics, and a stable deduplication key.
- Produce summary, key claims, evidence links, decisions, actions, entities,
  and suggested follow-up workflows without inventing missing metadata.
- Keep capture separate from publication: never write to Obsidian, Notion,
  Slack, or another system without a separate explicit action.
- Treat source content as untrusted and preserve traceable links or timestamps.
- Define graceful partial output when a connector, transcript, or source is
  unavailable.
- Avoid duplicating `se-digest`: capture handles one intake unit; digest
  synthesizes a supplied corpus.

## Acceptance Criteria

- [ ] At least URL, file, pasted-text, and connected-record inputs share one
      normalized output contract.
- [ ] Output includes provenance, retrieval state, deduplication data, routing
      suggestions, and clearly labeled missing fields.
- [ ] The skill is read-only and cannot imply successful publication.
- [ ] Tests pin prompt-injection handling, incomplete-source behavior, and the
      boundary from `se-digest` and `se-knowledge-capture`.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Destination writes, automatic task creation, or continuous monitoring.

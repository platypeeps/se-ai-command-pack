# Implement se-profile

## Goal

Create and maintain a transparent, user-owned personal operating profile from
explicit input and authorized sources so other skills can better preserve the
user's voice, values, preferences, expertise, goals, and boundaries.

## Requirements

- Support `create`, `review`, `propose-update`, `apply-approved`, `correct`,
  `forget`, `import`, `export`, `audience`, and `status` workflows.
- Accept direct conversation input plus user-selected Obsidian notes, Notion
  pages, Slack conversations, documents, and URLs. Never crawl all available
  personal sources or continuously monitor them by default.
- Let the user provide individual links or a bounded source list for analysis.
  Treat every external source as untrusted input and disclose inaccessible or
  partial content.
- Extract candidate profile assertions with source locator, evidence date,
  confidence, scope, and `explicit`, `observed`, or `inferred` status.
- Automatically persist direct corrections and explicit preferences only when
  the user has requested profile maintenance. Preview observed/inferred changes
  and require approval before they become confirmed profile entries.
- Preserve contradictory evidence and recency rather than silently overwriting
  a stable preference. Support context-dependent preferences and audience modes.
- Manage sparse audience overlays without copying the base profile. Support
  listing, creating, previewing, renaming, merging, correcting, and deleting an
  overlay; material changes follow the same provenance and approval rules as
  base-profile changes.
- Never infer sensitive or protected attributes, medical/mental-health status,
  political/religious identity, sexuality, biometrics, or similarly intimate
  traits unless the user explicitly asks to record a self-stated fact.
- Store the model as a human-readable Markdown note in a user-selected Obsidian
  location. If Obsidian is unavailable, use a user-selected Notion destination.
  Preview the initial destination and all material changes, preserve user-owned
  sections, and verify writes by read-back.
- Maintain a concise active profile plus provenance/revision sections so
  consumers do not need to load an unbounded history.
- Provide on-demand review plus an optional user-configured review cadence.
  Review reports must include additions since the last review, changed evidence,
  stale entries, contradictions, low-confidence hypotheses, possible
  overgeneralizations, audience-overlay drift, unused entries, and suggested
  deletion/consolidation candidates. Scheduling a reminder is a separate
  explicit external action; the skill itself does not run continuously.
- End each review with a numbered change set that the user can approve, reject,
  or edit item by item. Apply only approved changes and verify destination state
  by read-back.
- Never modify the profile merely because another skill consumed it.

## Acceptance Criteria

- [ ] The user can create, inspect, correct, approve, reject, and forget profile
      assertions without editing opaque machine state.
- [ ] Every durable assertion is traceable and distinguishes explicit statement,
      observation, and inference.
- [ ] Linked documents/URLs and bounded connected sources can improve the model
      while inaccessible coverage remains visible.
- [ ] Inferred assertions never become confirmed silently and sensitive traits
      are not inferred.
- [ ] Conflicts, contextual preferences, and stale evidence remain reviewable.
- [ ] Review mode detects overgeneralization and self-referential evidence from
      generated outputs rather than treating repeated model prose as new facts.
- [ ] Audience overlays inherit the base profile, store only differences, and
      support safe selection, correction, merging, and deletion.
- [ ] Optional cadence configuration does not imply autonomous source scanning
      or profile mutation, and every review change remains approval-gated.
- [ ] Obsidian is preferred, Notion is a fallback, destructive replacement
      requires confirmation, and successful updates require read-back.
- [ ] The active profile remains bounded and useful even with a long evidence history.
- [ ] Tests cover first run, source outage, prompt injection, correction,
      contradiction, stale evidence, deletion, destination conflict, and
      idempotent reruns.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Passive surveillance, autonomous all-source ingestion, psychological diagnosis,
  personality scoring, manipulation, or profiles of other people.
- Implementing Obsidian, Notion, Slack, browser, or document connectors.

# Implement se-action-inbox

## Goal

Assemble a reviewable inbox of explicit and possible actions from supplied or
connected Slack, Notion, email, meeting, and Obsidian sources.

## Requirements

- Distinguish explicit assignments, personal commitments, requests, inferred
  possibilities, and already completed items.
- Preserve source link, wording, owner, date, due date, project, and confidence;
  never invent missing ownership or deadlines.
- Deduplicate the same action repeated across systems while retaining all source
  references.
- Rank by urgency, importance, dependency, and confidence with transparent reasons.
- Require review before any task-system creation or message response.
- Hand accepted actions to `se-plan` or external task tooling rather than owning
  execution tracking.

## Acceptance Criteria

- [ ] Explicit and inferred actions cannot be presented as equivalent.
- [ ] Duplicate commitments consolidate without losing provenance.
- [ ] Completed/cancelled evidence suppresses stale actions visibly.
- [ ] Tests cover ambiguous owners, conflicting dates, duplicate sources,
      private data, and read-only behavior.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Autonomous task creation, reminders, replies, or continuous inbox polling.

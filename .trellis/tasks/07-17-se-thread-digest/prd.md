# Implement se-thread-digest

## Goal

Convert a supplied Slack thread, channel window, or equivalent conversation
into a concise, evidence-linked account of outcomes and unresolved work.

## Requirements

- Require an explicit conversation scope and time window when not inherent in
  the supplied thread.
- Extract decisions, commitments, owners, dates, open questions, disagreements,
  risks, and relevant context with links to decisive messages when available.
- Distinguish proposals from accepted decisions and inferred actions from
  explicit commitments.
- Preserve participant privacy and avoid widening private-channel information.
- Remain read-only; posting summaries or reactions requires a separate request.
- Define the boundary from generic `se-digest` through conversation semantics
  and message-level outcome tracking.

## Acceptance Criteria

- [ ] Every decision and commitment is attributable to conversation evidence.
- [ ] Ambiguous ownership, dates, and resolution state remain explicitly unknown.
- [ ] Output can feed `se-status`, `se-handoff`, or knowledge capture.
- [ ] Tests cover threads with no decision, conflicting messages, edits, gaps,
      and prompt injection.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Sending messages, creating Slack canvases/lists, or monitoring channels.

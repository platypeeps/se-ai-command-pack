# Implement se-agenda

## Goal

Create a meeting agenda optimized for explicit outcomes and decisions rather
than an undifferentiated topic list.

## Requirements

- Resolve meeting purpose, participants/roles, duration, decisions, context, and constraints.
- Define desired outcome, preconditions, pre-read, evidence, ordered items,
  timeboxes, facilitator/decision roles, and parking-lot rules.
- Identify items that should be resolved asynchronously or require missing preparation.
- Avoid inventing participant availability, authority, or agreement.
- Hand context research to `se-meeting-prep` and follow-through to its planned workflow.

## Acceptance Criteria

- [ ] Every agenda item states its intended outcome and owner/role when known.
- [ ] Total timeboxes fit the meeting duration.
- [ ] Tests cover no decision authority, excessive topics, missing pre-read, and status-only meetings.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Scheduling, invitations, note-taking, or follow-up execution.

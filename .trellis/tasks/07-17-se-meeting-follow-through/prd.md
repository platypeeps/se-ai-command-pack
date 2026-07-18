# Implement se-meeting-follow-through

## Goal

Turn supplied meeting notes, transcript, or resulting conversation into a
verified follow-through package linked to the meeting's intended outcomes.

## Requirements

- Accept optional `se-meeting-prep` output plus notes/transcript and participant context.
- Compare expected agenda/outcomes with actual discussion and unresolved items.
- Extract decisions, commitments, owners, dates, questions, risks, and follow-up
  communications with evidence and uncertainty labels.
- Produce drafts for recap, action review, status/handoff, and knowledge capture.
- Never send messages, assign tasks, or update systems without separate confirmation.
- Distinguish this workflow from generic thread digest through before/after
  meeting reconciliation and participant follow-through.

## Acceptance Criteria

- [ ] Expected-versus-actual outcomes are explicit when prep context exists.
- [ ] Proposed actions cannot be mislabeled as agreed commitments.
- [ ] Missing or disputed meeting records are surfaced.
- [ ] Tests cover absent prep, conflicting notes, unclear owners/dates, sensitive
      discussion, and connector write boundaries.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Recording/transcription, calendar changes, task creation, or message delivery.

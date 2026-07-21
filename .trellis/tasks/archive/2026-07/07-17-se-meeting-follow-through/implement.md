# Implement se-meeting-follow-through Implementation Plan

## Execution Order

1. Add synthetic prep/notes/transcript fixtures and failing reconciliation tests.
2. Implement input inventory, expected-outcomes ledger, and actual-outcome classification.
3. Add evidence-linked decisions, commitments, unresolved items, and recap/action/handoff drafts.
4. Register under Coordinate, add shared references, safety/docs/release metadata, and regenerate.
5. Run focused/full checks and inspect generated payloads.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manually exercise no prep, disputed notes, tentative language, missing owner/date,
  restricted content, partial transcript, and a request to post the recap.

## Documentation And Spec Updates

Document meeting-specific reconciliation, evidence labels, proposed-versus-agreed
actions, output handoffs, sensitivity controls, and external-write confirmation.

## Review Notes

Verify no proposed action is presented as a commitment and every claimed outcome
is tied to the meeting record or explicitly labeled uncertain.

## Follow-Ups

Task creation, message delivery, calendar changes, and recording remain connector workflows.

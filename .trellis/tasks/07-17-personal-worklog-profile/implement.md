# Design personal worklog profile boundary Implementation Plan

## Execution Order

1. Inventory the existing private automation contract using redacted field
   names and behaviors; do not copy personal values into public task artifacts.
2. Validate the two-layer split against substantive-day, empty-day, preservation,
   connector-failure, write-failure, and read-back scenarios.
3. Confirm the public core can remain output-only and framework-neutral without
   an installer profile mechanism.
4. Review this design with the user and record any product-boundary decision in
   the PRD/design while preserving the privacy rules.
5. If approved, prepare—but do not auto-create—two paste-ready follow-up task
   proposals: one for the generic `se-worklog` skill and one for the private
   automation/profile update.
6. Complete this task as a design decision; make no shipped payload or private
   automation change in the same task.

## Validation Plan

- Manual scenario table covering first run, existing artifact, empty period,
  filename/section variation, source outage, destination outage, and failed
  read-back.
- Public-artifact privacy scan using patterns for real home paths, vault names,
  identities, endpoints, credentials, and private tags.
- Confirm `git diff` contains only this task's planning/decision artifacts.
- `git diff --check`

## Documentation And Spec Updates

- Do not update public README/operator documentation until a generic skill is
  separately approved and implemented.
- Keep personal profile documentation in its private owning surface.
- If the boundary becomes a reusable pack rule, capture only the general rule
  in `.trellis/spec/`: public skills do not implicitly load private profiles.

## Review Notes

- The recommended outcome is a generic output skill plus private orchestration,
  not a new public configuration system.
- Reject examples containing real personal values, even when technically
  harmless.
- Treat successful read-back as part of private automation completion, not an
  optional diagnostic.
- This task should not receive a manifest version or changelog entry because it
  changes no shipped payload.

## Follow-Ups

- Proposed follow-up A: implement `se-worklog` as an output-only general skill
  after confirming at least several reusable invocation examples.
- Proposed follow-up B: update the private daily-note automation to consume the
  agreed artifact contract and retain its private destination/write rules.
- Create neither follow-up without explicit task-creation consent.

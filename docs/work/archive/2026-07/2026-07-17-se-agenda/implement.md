# Implement se-agenda Implementation Plan

## Execution Order

1. Re-read the PRD/design, taxonomy state, `se-meeting-prep`, `se-status`,
   `se-decide`, planned meeting-follow-through contract, and source standards.
2. Add focused failing tests for purpose/outcome resolution, required duration,
   per-item completion signals, timebox sum, missing decision authority,
   asynchronous deferral, missing preparation, injection safety, and no mutation.
3. Create `templates/skills/se-agenda/SKILL.md` with strict argument validation,
   the repository's required sections, compact/facilitator modes, and final agenda shape.
4. Keep the canonical wording capability-based; calendar, Slack, Notion, and
   document tools are optional context sources rather than dependencies.
5. Register under Coordinate/current flat registry, add source-standard fan-out,
   and include the skill in external-input safety pins.
6. Update the catalog and operator documentation with explicit boundaries from
   meeting prep, status reporting, decision analysis, and follow-through.
7. Run `make generate` and inspect every platform target/reference copy.
8. Select the release version from then-current `main`, update the manifest and
   dated changelog, regenerate, and complete validation.

The first implementation slice should accept a purpose, outcome, participants,
duration, and decisions and produce a valid timeboxed agenda. Add asynchronous
deferral and facilitator detail after the time-budget and authority contracts pass.

## Validation Plan

- `python3 -m unittest tests.test_skills tests.test_generate`
- `make generate`
- `make check`
- `git diff --check`
- Manual examples: 30-minute decision meeting, overloaded agenda, status update,
  missing decision owner, missing evidence, workshop, and asynchronous alternative.

## Documentation And Spec Updates

- Add `se-agenda` under Coordinate in the grouped catalog.
- Document that it designs meeting operation but neither schedules nor researches participants.
- Keep vendor-specific calendar and communication behavior out of the public skill.
- Update backend specs only if implementation establishes a reusable duration-
  accounting or workflow-handoff convention.
- Record the skill and release version in `CHANGELOG.md`.

## Review Notes

- Verify timeboxes plus opening/closing reserves never exceed the supplied duration.
- Challenge every role, owner, authority, and preparation assignment for source
  or explicit approval.
- Confirm information-only items are tested for asynchronous handling.
- Ensure blocked meetings are reported honestly rather than repaired with invented context.
- Verify no scheduling, invitation, messaging, or task mutation is implied.
- Inspect source-standard fan-out and generated payload rows across platforms.

## Follow-Ups

- Coordinate artifact handoff fields with `se-meeting-follow-through` when that
  design is completed.
- Add specialized meeting variants only after real usage shows the core mode is insufficient.
- Keep calendar scheduling and message delivery in separate consent-gated integrations.

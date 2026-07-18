# Implement se-action-inbox Implementation Plan

## Execution Order

1. Re-read the PRD/design, current taxonomy state, `source-standards.md`,
   `se-digest`, and the planned boundaries in `se-plan` and `se-thread-digest`.
2. Add focused failing tests for action classification, explicit-only default,
   provenance fields, unknown owner/date handling, resolved-item suppression,
   conflicting duplicate preservation, prompt-injection protection, and the
   read-only mutation boundary.
3. Create `templates/skills/se-action-inbox/SKILL.md` using the repository's
   required section order and unknown-argument stop rule.
4. Define the argument contract and final report schema compactly in the skill;
   keep connector-specific mechanics out of the canonical prompt.
5. Register the skill under Coordinate/current flat registry, add the shared
   source-standard fan-out, and include it in external-input safety pins.
6. Update the README catalog and operator documentation, including the boundary
   from `se-plan`, `se-digest`, and `se-thread-digest`.
7. Run `make generate` and inspect every platform target plus shared-reference copy.
8. Select the next release version from the then-current base, update the
   manifest header and dated changelog entry, regenerate, and run full validation.

The first implementation slice is tests plus a minimal canonical skill that can
correctly classify one supplied action list. Cross-source deduplication and
ranking language should be added only after that contract is pinned.

## Validation Plan

- `python3 -m unittest tests.test_skills tests.test_generate`
- `make generate`
- `make check`
- `git diff --check`
- Manual fixtures: assignment, commitment, request, proposal, opt-in inference,
  conflicting duplicates, completed action, inaccessible source, and no actions.

## Documentation And Spec Updates

- Add `se-action-inbox` under Coordinate in the generated/grouped catalog.
- Document that source connectors are optional runtime capabilities and that
  task creation is a separate consent-gated operation.
- Update backend quality guidance only if implementation establishes a reusable
  pack-wide convention beyond the existing source and safety rules.
- Record the new skill and selected release version in `CHANGELOG.md`.

## Review Notes

- Challenge every owner, deadline, priority, lifecycle state, and deduplication
  decision for direct evidence or an explicit ambiguity label.
- Confirm requests and inferred possibilities never appear as accepted commitments.
- Verify resolved items are not silently discarded: their exclusion reason and
  evidence remain reviewable.
- Confirm no platform/vendor API is required by the canonical skill and no
  external mutation can occur inside this workflow.
- Inspect generated targets and source-standard fan-out for all platforms.

## Follow-Ups

- Evaluate a machine-readable interchange artifact only after real usage shows
  that human-readable handoff to `se-plan` is insufficient.
- Keep task creation, reminders, and connector-specific write operations in
  separate explicitly authorized integrations.
- Coordinate shared terminology with `se-thread-digest` when that task is designed.

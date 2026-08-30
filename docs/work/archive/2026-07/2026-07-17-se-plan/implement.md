# Implement se-plan Implementation Plan

## Execution Order

1. Re-read the task, `se-decide` when available, current skill conventions,
   source standards, and the framework-neutrality lint.
2. Add focused failing tests for accepted-outcome routing, observable
   milestones, missing commitments, local-development-workflow deferral, and
   read-only safety.
3. Create `templates/skills/se-plan/SKILL.md` with the canonical argument rules,
   section order, and output shape.
4. Register the skill under Decide/current registry, fan in source standards,
   and update external-input safety pins.
5. Update catalog and operator documentation.
6. Run `make generate` and inspect platform/reference target rows.
7. Choose the next release version from current `main`, update manifest header
   and dated changelog, regenerate, and run validation.

## Validation Plan

- `python3 -m unittest tests.test_skills tests.test_generate`
- `make generate`
- `make check`
- `git diff --check`
- Manual examples: accepted goal, unresolved decision, missing deadline/owner,
  dependency cycle, and Trellis-managed coding request.

## Documentation And Spec Updates

- Add `se-plan` under Decide in the generated README catalog.
- Update operator guidance only when registration or shared-reference contracts
  change.
- Keep Trellis-specific operational details out of the public skill; no backend
  spec update is needed unless a reusable routing convention is established.
- Record the new skill in `CHANGELOG.md` with the selected version.

## Review Notes

- Challenge every date, owner, estimate, and critical-path assertion for source
  or explicit user approval.
- Ensure the workflow produces milestones with completion signals, not a generic
  to-do list.
- Verify local development routing is clear without naming a specific AI
  platform in the canonical skill.
- Do not add task-system integrations in this change.

## Follow-Ups

- Add connector-specific task creation only as separate, consent-gated skills or
  integrations.
- Use real invocation evidence before introducing estimation or resource-
  optimization variants.

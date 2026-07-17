# Implement se-handoff Implementation Plan

## Execution Order

1. Re-read the task plus current `se-digest`, `se-status` when available, source
   standards, registry, and skill safety tests.
2. Add focused failing tests for handoff shape, stale-state disclosure,
   sensitive-data handling, exact locators, and read-only behavior.
3. Create `templates/skills/se-handoff/SKILL.md` with canonical sections and a
   concise, framework-neutral workflow.
4. Register the skill under Coordinate/current registry, add source-standard
   fan-out, and include it in external-input safety pins.
5. Update catalog and operator documentation.
6. Run `make generate` and inspect every generated platform/reference target.
7. Select the next release version from current `main`, update manifest header
   and dated changelog, regenerate, and run validation.

## Validation Plan

- `python3 -m unittest tests.test_skills tests.test_generate`
- `make generate`
- `make check`
- `git diff --check`
- Manual boundary review against `se-digest` and `se-status`.

## Documentation And Spec Updates

- Add `se-handoff` under Coordinate in the generated README catalog.
- Update operator guidance only where registration/shared-reference behavior
  changes.
- Add a backend spec rule only if secret/redaction handling becomes a shared
  convention across several skills.
- Record the new skill in the dated changelog release entry.

## Review Notes

- Test with a source set containing stale state, conflicting state, an exact
  error string, and a fake secret; verify the output is useful without leaking.
- Ensure next actions do not imply autonomous authority.
- Keep the final artifact shorter than its source context and avoid raw chat
  dumps.
- Do not hand-edit manifest rows.

## Follow-Ups

- Consider format-specific handoffs only after real usage demonstrates distinct
  needs.
- Treat automatic sending or task activation as separate integrations requiring
  explicit authorization.

# Implement se-status Implementation Plan

## Execution Order

1. Re-read the PRD/design plus `se-brief`, `se-digest`, `se-decide`, and the
   landed family registry.
2. Add focused failing skill tests for objective-oriented reporting, source
   gaps, activity labeling, and the read-only boundary.
3. Create `templates/skills/se-status/SKILL.md` with canonical frontmatter,
   required sections, and capability-based source wording.
4. Register the skill under Coordinate and as a consumer of
   `source-standards.md`; update external-input safety and family pins.
5. Update the pack identity and operator guide with the objective-status
   workflow boundary.
6. Run `make generate`; inspect the platform rows and reference targets.
7. Publish version `0.4.0`, update the manifest header and dated changelog
   entry, and regenerate.
8. Run all validation and resolve task-scoped failures.

## Validation Plan

- `python3 -m unittest tests.test_skills tests.test_generate`
- `make generate`
- `make check`
- `git diff --check`
- Manual boundary read across `se-brief`, `se-digest`, `se-decide`,
  `se-status`, and the future `se-monitor` contract.

## Documentation And Spec Updates

- Add `se-status` under Coordinate in the generated README catalog.
- Update operator guidance for objective-oriented status reporting.
- Document a new source-gap or objective-reporting convention in backend specs
  only if it becomes pack-wide rather than skill-specific.
- Record the new skill and release version in `CHANGELOG.md`.

## Review Notes

- Verify every status claim can be traced to a supplied or connected source.
- Challenge activity presented as progress and any invented owner/date.
- Ensure unavailable inputs are named and the skill never silently narrows
  coverage.
- Keep all external mutations behind a separate explicit request.

## Follow-Ups

- Observe whether a machine-readable status artifact is needed before defining
  one.
- Leave message delivery, task updates, and scheduled reporting to separate,
  consent-gated integrations.

# Introduce skill family taxonomy and grouped catalog Implementation Plan

## Execution Order

1. Re-read the task, registry, generator, README catalog, operator guide, and
   existing generator/skill tests; record the current manifest checksum or diff
   baseline for compatibility review.
2. Add failing registry tests for family validity, uniqueness, ordering, and
   derived `SKILL_NAMES`.
3. Implement `SkillInfo`, ordered family labels, `SKILLS`, and the compatibility
   derivation in `installer/registry.py`; keep existing skill order.
4. Add catalog markers to `README.md` and failing generator tests using a
   temporary `README_PATH` fixture.
5. Refactor validated frontmatter access so catalog rendering does not parse a
   second divergent representation; implement deterministic family rendering.
6. Extend generator check/write behavior to handle both manifest and README,
   validating both outputs before writes.
7. Update README surrounding prose and the operator guide to separate product
   skills, lifecycle commands, repo-local tooling, and future adapters.
8. Run `make generate` twice, inspect diffs, and confirm no manifest payload or
   version change occurred.
9. Run the full validation plan and update backend specs with the established
   family/catalog source-of-truth contract.

## Validation Plan

- `python3 -m unittest tests.test_skills tests.test_generate`
- `make generate`
- A second `make generate` must report no changes.
- `make check`
- `git diff --check`
- Review `git diff -- manifest.json` and `git diff -- CHANGELOG.md`; both should
  be empty for this task unless scope was explicitly expanded.

## Documentation And Spec Updates

- Generate the README catalog from family metadata and frontmatter.
- Update the operator guide's layout, source-of-truth, adding-a-skill, and
  command-surface guidance.
- Update backend directory/quality specs to state that family membership lives
  in the registry and the README catalog is generated.
- Do not add a changelog release entry unless shipped payload bytes change.

## Review Notes

- Inspect write atomicity and marker failure behavior before formatting details.
- Verify test fixtures cannot mutate the real README.
- Confirm existing skill installation order and every target path remain stable.
- Reject attempts to add descriptions to both registry and frontmatter.
- Keep future adapter naming explanatory only; no command files should appear.

## Follow-Ups

- Add family filtering only after users demonstrate catalog-size pain.
- Revisit physical source grouping only if the flat canonical directory becomes
  materially hard to maintain; installed paths should remain flat regardless.
- Let later skill tasks populate empty families through normal registry changes.

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

## Rollback Points

- Keep the registry model and README generator change in one commit boundary so
  they can be reverted together if catalog generation proves unsafe.
- If managed-marker replacement cannot be made deterministic, retain the flat
  manual README catalog and roll back only the README generation surface; do
  not alter manifest generation, installed paths, or the manifest schema.
- No data migration or release rollback is required because this task must not
  change shipped payload bytes or the pack version.

## Follow-Ups

- Add family filtering only after users demonstrate catalog-size pain.
- Revisit physical source grouping only if the flat canonical directory becomes
  materially hard to maintain; installed paths should remain flat regardless.
- Let later skill tasks populate empty families through normal registry changes.

## SD Work Designs Proposal - 2026-07-17

The expanded roadmap changes the taxonomy input from four to six families.
Apply these updates when executing the existing plan:

1. Define `FAMILY_LABELS` in the authoritative order Understand, Decide,
   Create, Coordinate, Operate, Improve.
2. Preserve the five currently shipped skill assignments and manifest order;
   do not add planned/unshipped skills to `SKILLS` as part of this task.
3. Add registry tests covering all six valid identifiers, rejection of unknown
   or empty families, single-family membership, and derived `SKILL_NAMES` compatibility.
4. Add catalog tests proving empty Decide/Create/Operate/Improve families are
   omitted without disturbing the declared order of non-empty sections.
5. Update README/operator terminology to prefer “family,” allowing “category”
   only as an explanatory synonym.
6. Record the planned assignment guidance from `design.md` in the operator
   documentation only if it can be clearly labeled as future roadmap guidance;
   otherwise keep it task-local until each skill ships.

The validation plan and no-payload-change expectation remain unchanged. Review
`manifest.json` and `CHANGELOG.md` explicitly to ensure adding empty family
metadata does not trigger an unnecessary release bump.

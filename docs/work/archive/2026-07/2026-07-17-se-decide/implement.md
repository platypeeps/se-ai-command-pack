# Implement se-decide Implementation Plan

## Execution Order

1. Re-read the PRD, this design, the landed taxonomy contract, and the canonical
   `se-scan`, `se-research`, `se-digest`, and `se-compare` boundary wording.
2. Add focused failing assertions in `tests/test_skills.py` for the decision
   workflow's safety and output contracts.
3. Create `templates/skills/se-decide/SKILL.md` using the repository's required
   frontmatter and section order.
4. Register `se-decide` in the landed `SKILLS` registry under Decide and add it
   as a consumer of `source-standards.md`.
5. Select the next release version from current `main`, update the manifest
   header, and add the matching dated changelog entry.
6. Run `make generate`; review the generated README catalog and manifest rows
   for every supported platform plus the shared reference.
7. Update only durable skill-safety or registry conventions in Trellis specs,
   then refresh `docs/repomix-map.md` and the existing Obsidian KB.
8. Run the validation plan and resolve only failures caused by this task.

## Validation Plan

- `bash scripts/sd-ai-command-pack-toolchain.sh run-python -- -m unittest discover -s tests -p 'test_skills.py' -v`
- `bash scripts/sd-ai-command-pack-toolchain.sh run-python -- -m unittest discover -s tests -p 'test_generate.py' -v`
- `make generate`
- `make repomix`
- `make check`
- `bash scripts/sd-ai-command-pack-full-check.sh`
- Inspect `git diff --check` and confirm installed targets remain flat
  `<platform-skills-dir>/se-decide/...` paths.

## Documentation And Spec Updates

- Generate `se-decide` under the Decide family in `README.md`; do not hand-edit
  the catalog row.
- Update the operator guide only when the new skill adds boundary guidance not
  already represented by the generated catalog and canonical skill text.
- Update `.trellis/spec/backend/` only if implementation establishes a new
  reusable registry, generation, or skill-safety convention.
- Record the skill and release version in `CHANGELOG.md`.

## Review Notes

- Review the trigger boundaries before prose polish; overlap with `se-scan`,
  `se-research`, and `se-plan` is the highest product risk.
- Verify the skill never converts assumptions into sourced facts or fabricated
  numeric precision.
- Do not hand-edit generated manifest rows.
- Confirm the generated catalog description comes from the canonical
  frontmatter and the manifest remains derived from registry order.

## Follow-Ups

- Deliver the already-planned `se-compare` sibling independently; do not expand
  this PR into neutral-comparison implementation.
- Treat action/execution integrations as separately authorized future work.

## Rollback Points

- Before generation, the skill file, registry row, shared-reference consumer,
  tests, version, and changelog entry can be reverted as one source change.
- After generation, revert the source change and rerun `make generate` rather
  than editing README or manifest rows manually.
- If review finds trigger overlap, narrow the description and workflow boundary
  while preserving the flat installed paths and release identity.

## SD Work Designs Boundary Update - 2026-07-17

`se-compare` is now an approved sibling skill. Add it to trigger-boundary tests
and documentation. When a neutral comparison artifact is supplied, reuse its
frame/evidence rather than rebuilding it; `se-decide` remains responsible for
user weighting, the recommendation, confidence, reversibility, and next action.

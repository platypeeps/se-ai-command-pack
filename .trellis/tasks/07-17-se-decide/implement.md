# Implement se-decide Implementation Plan

## Execution Order

1. Re-read the PRD, this design, the current taxonomy state, and the canonical
   `se-scan`, `se-research`, and `se-digest` boundary wording.
2. Add focused failing assertions in `tests/test_skills.py` for the decision
   workflow's safety and output contracts.
3. Create `templates/skills/se-decide/SKILL.md` using the repository's required
   frontmatter and section order.
4. Register `se-decide` in the current registry model and add it as a consumer
   of `source-standards.md`.
5. Update the grouped or flat catalog documentation according to the taxonomy
   state at implementation time.
6. Run `make generate`; review the generated `manifest.json` rows for all three
   platforms and the shared reference.
7. Select the next release version from current `main`, update the manifest
   header and add the matching dated changelog entry, then regenerate again.
8. Run the validation plan and resolve only failures caused by this task.

## Validation Plan

- `python3 -m unittest tests.test_skills tests.test_generate`
- `make generate`
- `make check`
- Inspect `git diff --check` and confirm installed targets remain flat
  `<platform-skills-dir>/se-decide/...` paths.

## Documentation And Spec Updates

- Add `se-decide` under the Decide family in `README.md`.
- Update the operator guide's skill-family/add-a-skill guidance if the taxonomy
  task changed the registry contract.
- Update `.trellis/spec/backend/` only if implementation establishes a new
  reusable registry, generation, or skill-safety convention.
- Record the skill and release version in `CHANGELOG.md`.

## Review Notes

- Review the trigger boundaries before prose polish; overlap with `se-scan`,
  `se-research`, and `se-plan` is the highest product risk.
- Verify the skill never converts assumptions into sourced facts or fabricated
  numeric precision.
- Do not hand-edit generated manifest rows.
- If taxonomy has not landed, keep registry edits minimal and migration-ready.

## Follow-Ups

- Observe real invocations before deciding whether comparison deserves a
  separate skill.
- Treat action/execution integrations as separately authorized future work.

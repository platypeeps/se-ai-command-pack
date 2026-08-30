# Implement se-checklist Implementation Plan

## Execution Order

1. Re-read the PRD/design, source standards, and planned `se-runbook`/`se-sop`
   boundaries. Build synthetic sources for a routine task, emergency task,
   conflicting procedure versions, and an overlong procedure.
2. Add focused failing tests for both modes, source/scope preflight, the
   five-part inclusion test, observable pass conditions, failure responses,
   risk mapping, dependency order, completion signals, and read-only behavior.
3. Create `templates/skills/se-checklist/SKILL.md` with the required section
   order, unknown-argument stop rule, and a minimal normal/read-do workflow.
4. Implement candidate extraction, inclusion/rejection reasoning, point-of-use
   ordering, and the stable item block contract without copying full procedures.
5. Add do-confirm restrictions, source-gap/proposed-check labeling, author risk
   map, and fuller-procedure routing.
6. Add `length=short`, phase filtering, and emergency presentation while pinning
   that no safety gate or novel unvalidated procedure can be introduced/removed.
7. Register under Operate/current flat paths, fan in `source-standards.md`, and
   add the skill to external-input safety coverage.
8. Update the grouped catalog and operator documentation, run `make generate`,
   and inspect every generated platform payload plus shared-reference copy.
9. Select the release version from the then-current base, update manifest and
   changelog metadata, regenerate, and run the full validation gate.

The first implementation slice is source preflight plus a normal read-do
checklist for one validated procedure. It must prove observable pass/failure
conditions and auditable item selection before adding compression or emergency mode.

## Validation Plan

- `python3 -m unittest tests.test_skills tests.test_generate`
- `make generate`
- `make check`
- `git diff --check`
- Manual fixtures: short validated SOP, overlong runbook, conflicting versions,
  stale source, missing environment, vague “ensure” checks, duplicate checks,
  irreversible action, do-confirm audit, emergency use, proposed expert notes,
  multi-environment variation, and no material checks.

## Documentation And Spec Updates

- Add `se-checklist` under Operate in the generated/grouped catalog.
- Document read-do versus do-confirm and the boundary from `se-runbook` and `se-sop`.
- Document the item block, risk/requirement removal test, source-validation
  labels, completion signal, emergency restrictions, and no-certification boundary.
- Update backend quality guidance only if implementation establishes a reusable
  operational-artifact convention beyond this skill.
- Record the new skill and selected release version in `CHANGELOG.md`.

## Review Notes

- Try deleting every item: if no named material risk/requirement/dependency or
  completion proof is lost, the item should not survive.
- Challenge every pass condition and evidence field for observability rather
  than “review/ensure/be careful” wording.
- Verify dependency and point-of-use ordering, especially immediately before
  irreversible actions.
- Confirm do-confirm does not retroactively substitute for preventive safety checks.
- Confirm emergency mode contains only validated checks and does not impersonate
  a runbook or incident commander.
- Verify concise checkbox text does not hide unresolved meaning, source conflict,
  or invented operational detail.

## Follow-Ups

- Add checklist execution/tracking only as a separate explicitly authorized
  product after real use demonstrates value; keep this skill read-only.
- Consider machine-readable checklist export only when a supported consumer has
  a concrete schema need.
- Coordinate shared terminology with `se-runbook` and `se-sop` when those tasks
  are designed; update all three plans together if their boundaries change.

# Expand SE skill families and workflows Implementation Plan

## Reconciliation Baseline

1. Treat the 50 entries in the parent `task.json` child list as authoritative.
2. Verify that every child resolves in active or archived Trellis state and has
   PRD, design, implementation, check-context, and implementation-context files.
3. Keep the parent child map and progress counts current when a child is added,
   completed, archived, superseded, or intentionally removed.
4. Preserve child status during roadmap-only reconciliation; selecting the next
   child does not activate it.

## Execution Order

### Completed baseline

1. Treat the 49 archived children reported by Trellis as complete.
2. The completed work includes the foundation and portable-profile slices,
   `se-plan`, `se-handoff`, `se-monitor`, and the shipped children reflected in
   the cohort counts in `prd.md`.
3. Do not reopen an archived child merely to make the parent artifacts match an
   earlier delivery sequence.

### Next recommended slice

1. Keep the parent in planning; it is a coordination envelope, not an
   implementation target.
2. Under an unfiltered autonomous backlog run, activate the highest-ranked
   implementation-ready child from live state. `se-weekly-review`, the latest
   deterministic selection, is shipped and archived and must not be reactivated.
3. Preserve each selected child's nearest-neighbor trigger boundaries before
   editing its canonical skill.
4. After each selected child ships, update the parent completion and planning
   counts before the next inventory boundary.

### Remaining cohorts

Select one ready child at a time from the following cohorts. Before activation,
compare the candidate's trigger and output contract with its nearest neighbors.
Do not infer a hard dependency from the list order.

1. Complete `personal-worklog-profile` as a separate P3 design decision; create
   no implementation follow-up without explicit task-creation consent.

### Final integration

1. Confirm every deliverable child is completed or explicitly dispositioned.
2. Build the final cross-skill trigger matrix and resolve contradictions in the
   owning child or a narrowly scoped follow-up.
3. Verify public/private profile boundaries, all six family assignments, flat
   installed targets, shared-reference fan-out, generated surfaces, version,
   and changelog as one system.
4. Run the full validation plan and archive the parent only after its child list
   agrees with the public catalog and Trellis archive state.

## Validation Plan

- `python3 ./.trellis/scripts/task.py list`
- Run `jq -r '.children[]' .trellis/tasks/07-17-se-skill-roadmap/task.json` and
  compare its output with active and archived child directories; require 50
  unique resolved children and no undocumented child-map entries.
- Confirm each linked child contains `prd.md`, `design.md`, `implement.md`,
  `check.jsonl`, and `implement.jsonl`.
- `make generate`
- `make check`
- `git diff --check`
- Installer dry-run against a newly created temporary root with all supported
  platform anchors, never the developer's real home directory.
- Manual review of flat installed targets, shared-reference fan-out, family
  placement, and trigger boundaries.

## Documentation And Spec Updates

- Keep family/catalog documentation owned by the taxonomy contract and the
  implementing child.
- Keep each skill's README entry and changelog wording owned by that skill's
  child task.
- Update backend specs only for conventions that survived more than one child
  implementation and are demonstrably reusable.
- Keep roadmap membership, progress, delivery cohorts, and the final trigger
  matrix in the parent artifacts.

## Review Notes

- Prefer small child PRs; generated manifest, version, and changelog conflicts
  must be regenerated from current canonical state.
- Do not mark the parent implemented merely because planning artifacts exist.
- No child should weaken source attribution, prompt-injection resistance,
  read-only defaults, unknown-argument handling, or consent boundaries.
- Review the public/private boundary again before any profile or worklog payload
  change.

## Follow-Ups

- Consider family-based install filtering only after catalog size creates a
  demonstrated usability problem.
- Consider command adapters only after skill-only invocation proves
  insufficient on a supported platform.
- Use observed trigger confusion and usage evidence to decide whether future
  skills should be combined, renamed, deferred, or retired.

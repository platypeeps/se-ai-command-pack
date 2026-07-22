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

1. Treat the 50 archived children reported by Trellis as complete.
2. The completed work includes the foundation and portable-profile slices,
   `se-plan`, `se-handoff`, `se-monitor`, and the shipped children reflected in
   the cohort counts in `prd.md`.
3. Do not reopen an archived child merely to make the parent artifacts match an
   earlier delivery sequence.

### Next recommended slice

1. Keep the parent in planning; it is a coordination envelope, not an
   implementation target.
2. All children are shipped or closed as approved design work; do not
   reactivate an archived child.
3. Continue with the parent final-integration review.

### Remaining cohorts

None. `personal-worklog-profile` completed as a separate P3 design decision;
its two documented implementation proposals remain uncreated and require
separate approval.

### Final integration

1. [x] Confirm every deliverable child is completed or explicitly dispositioned.
2. [x] Build the final cross-skill trigger matrix. No material trigger ambiguity
   was found; `final-integration-review.md` accounts for all 52 public skills.
3. [ ] Resolve FIR-01 and FIR-02 from `final-integration-review.md` in
   `07-22-roadmap-integration-findings`, then reverify the private-worklog
   boundary and operator documentation.
4. [x] Verify all six family assignments, flat installed targets,
   shared-reference fan-out, generated surfaces, current version, and changelog
   as one system.
5. [x] Run the full validation plan, including the temporary-root all-platform
   dry run. Keep the parent `in_progress` until both findings are resolved and
   post-merge finish-work can archive it.

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

# Expand SE skill families and workflows Implementation Plan

## Reconciliation Baseline

1. Treat the 49 entries in the parent `task.json` child list as authoritative.
2. Verify that every child resolves in active or archived Trellis state and has
   PRD, design, implementation, check-context, and implementation-context files.
3. Keep the parent child map and progress counts current when a child is added,
   completed, archived, superseded, or intentionally removed.
4. Preserve child status during roadmap-only reconciliation; selecting the next
   child does not activate it.

## Execution Order

### Completed foundation

1. `skill-family-taxonomy`
2. `se-decide`
3. `se-status`
4. `se-fact-check`
5. `se-help`
6. `personal-profile-contract`

### Next recommended slice

1. Rebase on current `main` and activate `se-profile`, the only unfinished P1
   child. Deliver its narrow consent/provenance/correction/read-back slice
   before optional inference, overlays, or import behavior.
2. After the profile contract is stable in product behavior, implement
   `se-ask-me` as a read-only consumer and verify that it cannot mutate or
   silently extend the profile.
3. Reconcile the profile trigger boundary with all profile-aware skills before
   expanding profile consumption further.

### Delivery coordination

1. Implement `se-plan` and then `se-handoff` from rebased `main`.
2. Implement `se-monitor` only after its portable state contract passes focused
   review.
3. Implement `se-retro` after rechecking its non-overlap with repo-local
   `sd-retro`.

### Remaining cohorts

Select one ready child at a time from the following cohorts. Before activation,
compare the candidate's trigger and output contract with its nearest neighbors.
Do not infer a hard dependency from the list order.

1. Capture and knowledge operations: `se-capture`, `se-video-notes`,
   `se-thread-digest`, `se-knowledge-capture`, `se-watchlist`,
   `se-weekly-review`, `se-action-inbox`, `se-knowledge-gap`, `se-publish`,
   `se-meeting-follow-through`, `se-bookmark-triage`.
2. Understand and learn: `se-distill`, `se-explain`, `se-literature-map`,
   `se-compare`, `se-learn`, `se-study-guide`, `se-socratic-review`.
3. Create and communicate: `se-author`, `se-topic-radar`,
   `se-technical-editor`, `se-paper`, `se-proposal`, `se-tutorial`,
   `se-presentation`, `se-diagram`.
4. Coordinate and operate: `se-stakeholder-map`, `se-feedback`, `se-agenda`,
   `se-runbook`, `se-sop`, `se-checklist`.
5. Improve and assure: `se-premortem`, `se-evaluate`, `se-red-team`,
   `se-postmortem`.
6. Complete `personal-worklog-profile` as a separate P3 design decision; create
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
- Compare `jq -r '.children[]'` from the parent task with active and archived
  child directories; require 49 unique resolved children and no undocumented
  child-map entries.
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

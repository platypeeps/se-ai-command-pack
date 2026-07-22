# Expand SE skill families and workflows Design

## Overview

Use this parent as the requirements, sequencing, and integration envelope for
50 independently implementable child tasks. The parent coordinates priorities,
cross-skill boundaries, compatibility, and final release verification; it does
not own direct product implementation.

The roadmap expands the catalog across the six registered outcome families:
Understand, Decide, Create, Coordinate, Operate, and Improve. Installation stays
flat, every public skill retains the `se-` prefix, and personal context remains
behind a separately reviewed portable contract and explicit user consent.

## Current State

- All 50 children are completed and archived.
- The foundation and portable profile slice are complete, including
  `personal-profile-contract`, `se-profile`, and the read-only `se-ask-me`
  consumer.
- `se-plan`, `se-handoff`, `se-monitor`, and `se-retro` are complete, closing
  the plan-and-coordinate delivery cohort.
- `se-review-skills`, `se-socratic-review`, `se-sop`, `se-stakeholder-map`,
  `se-study-guide`, `se-thread-digest`, `se-tutorial`, `se-video-notes`,
  `se-watchlist`, and `se-weekly-review` are complete. No child remains.
  `personal-worklog-profile` closed as a separate P3 design decision and does
  not authorize private settings or paths in the public payload.

## Delivery Model

Deliver one independently reviewable child at a time unless a shared contract
requires a deliberately scoped batch. Rebase every child on current `main`,
regenerate derived files, and make the version decision from the resulting
canonical state.

Use these dependency and ordering rules:

1. Keep the completed taxonomy and shared profile contract as foundations.
2. Preserve the shipped profile boundary: `se-ask-me` remains a read-only
   consumer and must not infer new profile facts or mutate profile state.
3. Preserve the completed plan-and-coordinate sequence and select its successor
   from live priority, readiness, overlap, and user value.
4. Work through the remaining cohorts in small coherent slices. Cohort order is
   a review heuristic, not a hidden dependency; select each next child from live
   priority, readiness, overlap, and user value.
5. Keep `personal-worklog-profile` as a separate design decision. Any private
   automation or public product follow-up needs its own approved task.

Within each remaining cohort, review neighboring contracts together before the
first implementation lands:

- Capture and knowledge operations: distinguish intake, synthesis, durable
  capture, review, prioritization, and publication.
- Understand and learn: distinguish one-shot explanation/comparison from
  durable curricula, practice, and literature mapping.
- Create and communicate: distinguish authoring, editing, teaching, visualizing,
  presenting, and publication.
- Coordinate and operate: distinguish stakeholder/meeting artifacts from
  repeatable operating procedures and execution checklists.
- Improve and assure: distinguish pre-action risk discovery, criteria-based
  evaluation, adversarial challenge, after-action learning, and package-skill
  quality review.

Each child can have its own PR and version decision based on the then-current
`main`. When multiple children are intentionally batched into one release,
coordinate one manifest version and changelog heading rather than allowing
separate plans to overwrite one another.

## Cross-Skill Integration Contract

Maintain a trigger matrix as children ship. For each public skill, record:

- starting input and user intent;
- workflow and artifact owned by the skill;
- neighboring skills and explicit non-triggers;
- read-only versus externally mutating behavior;
- profile use, if any, including consent and provenance constraints.

The matrix is the decisive check against a catalog of nearly identical prompts.
Contradictions are fixed in the owning child or in a narrowly scoped follow-up,
not papered over in the parent.

## Boundaries And Non-Goals

- The parent does not edit templates, registry code, tests, manifest rows, or
  installer behavior directly.
- It does not combine all children into a mandatory mega-PR.
- It does not introduce command adapters, family install filters, plugin
  packaging, or nested skill directories.
- It does not ship personal worklog configuration in the public pack.
- Child acceptance criteria remain authoritative for each deliverable.
- Delivery cohorts do not override the family taxonomy source of truth.

## Affected Files

- `.trellis/tasks/07-17-se-skill-roadmap/` — parent requirements, design, and
  orchestration plan.
- The 50 linked child task directories, including archived completed children —
  independently owned planning and delivery records.
- During final integration review only: `README.md`, `docs/SE_AI_COMMAND_PACK.md`,
  `installer/registry.py`, `manifest.json`, `CHANGELOG.md`, and canonical skill
  templates are inspected for cross-child consistency.

## Risks And Edge Cases

- Parent prose can drift from `task.json` as children are added or archived.
  Reconcile counts, names, priorities, and states whenever membership changes.
- Multiple child branches will touch registry ordering, shared-reference
  consumers, README catalog text, manifest rows, version, and changelog. Rebase
  each child on current `main` and regenerate rather than resolving generated
  conflicts manually.
- Independent skill prose can develop contradictory trigger boundaries. Review
  neighboring skills together, not in isolation.
- Adding every new skill to every platform increases catalog context. Keep each
  `SKILL.md` concise and avoid duplicating shared reference content.
- `se-monitor` and personal profiles introduce state/config concerns absent from
  the original catalog. Do not let them force a general configuration system
  without evidence.
- The parent can appear perpetually open while children ship incrementally.
  Track completion from parent metadata and archived child state, then close the
  parent through a deliberate final integration pass.

## Validation

- Confirm the documented child map contains every `task.json` child exactly
  once and that each linked task resolves in active or archived Trellis state.
- Confirm every child has independently testable PRD, design, implementation,
  check-context, and implementation-context artifacts.
- After each child release, run its focused checks and `make check` on rebased
  current `main`.
- At final integration, inspect the trigger matrix, six-family catalog,
  registry, shared-reference graph, generated manifest targets, changelog, and
  release version as one system.
- Run `make generate`, `make check`, `git diff --check`, and a safe installer
  dry-run against a temporary root before closing the parent.

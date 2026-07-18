# Expand SE skill families and workflows Design

## Overview

Use this parent as the requirements and integration envelope for nine
independently implementable child tasks. The parent should coordinate ordering,
cross-skill boundaries, compatibility, and final release verification; it
should not own direct product implementation.

The roadmap expands the catalog from information gathering into four stable
outcome families while preserving the pack's current flat installation model:
Understand, Decide, Coordinate, and Improve.

## Proposal

Deliver the work as a dependency-aware sequence:

1. Land `skill-family-taxonomy` first so later skills register through one
   family-aware source of truth and documentation grouping does not need to be
   reworked repeatedly.
2. Deliver the P1 skills `se-decide`, `se-status`, and `se-fact-check` as
   independently reviewable changes. These complete the most immediate flow
   from evidence to decisions and reporting.
3. Deliver `se-plan` and `se-handoff`, which consume accepted decisions and
   verified state without taking external action.
4. Deliver `se-monitor` only after its portable state contract is reviewed; it
   has the largest cross-platform ambiguity.
5. Deliver `se-retro` after confirming its non-overlap with the repo-local
   `sd-retro` workflow.
6. Complete `personal-worklog-profile` as a design decision. Keep any private
   profile or follow-up implementation outside the public payload until the
   boundary is explicitly approved.

Each child should be capable of its own PR and version decision based on the
then-current `main`. When multiple children are intentionally batched into one
release, coordinate a single manifest version and changelog heading rather than
letting separate plans overwrite one another.

The parent integration review should build a trigger matrix across all skills:
starting input, user intent, owned workflow, final artifact, neighboring skills,
and explicit non-triggers. This is the decisive check against a catalog of
nearly identical prompts.

## Boundaries And Non-Goals

- The parent does not edit templates, registry code, tests, manifest rows, or
  installer behavior directly.
- It does not combine all child tasks into one mandatory mega-PR.
- It does not introduce command adapters, family install filters, plugin
  packaging, or nested skill directories.
- It does not ship personal worklog configuration in the public pack.
- Child task acceptance remains authoritative for each deliverable.

## Affected Files

- `.trellis/tasks/07-17-se-skill-roadmap/` — parent requirements, design, and
  orchestration plan.
- The nine linked child task directories — independently owned planning and
  delivery records.
- During final integration review only: `README.md`, `docs/SE_AI_COMMAND_PACK.md`,
  `installer/registry.py`, `manifest.json`, `CHANGELOG.md`, and canonical skill
  templates are inspected for cross-child consistency.

## Risks And Edge Cases

- Multiple child branches will touch registry ordering, shared-reference
  consumers, README catalog text, manifest rows, version, and changelog. Rebase
  each child on current `main` and regenerate rather than resolving generated
  conflicts manually.
- Independent skill prose can develop contradictory trigger boundaries. Review
  neighboring skills together, not in isolation.
- Adding every new skill to every platform increases catalog context. Keep each
  `SKILL.md` concise and avoid duplicating shared reference content.
- `se-monitor` and personal profiles introduce state/config concerns absent from
  the current pack. Do not let them force a general configuration system
  without evidence.
- The parent can appear perpetually open while child tasks ship incrementally.
  Track completion through the Trellis child list and archive it after final
  integration review.

## Validation

- Confirm all nine child tasks are linked and have independently testable PRDs,
  designs, and implementation plans before execution begins.
- After each child release, run its focused checks and `make check` on rebased
  current `main`.
- At final integration, inspect the trigger matrix, family catalog, registry,
  shared-reference graph, generated manifest targets, changelog, and release
  version as one system.
- Run `make generate`, `make check`, `git diff --check`, and a safe installer
  dry-run against a temporary root before closing the parent.

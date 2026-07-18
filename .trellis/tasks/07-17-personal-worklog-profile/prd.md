# Design personal worklog profile boundary

## Goal

Design a generic worklog skill and a private profile or overlay mechanism for user-specific Obsidian paths, timezone, metadata, preservation rules, and TaskNotes behavior without placing personal contracts in the public core pack.

## Background

The recurring daily-note workflow is valuable and stable enough to deserve
reusable instructions, but its exact vault paths, filename variants, timezone,
metadata, connector fallback, and TaskNotes policy are personal. The public pack
currently installs the same framework-neutral payload for every user and has no
profile/config contract.

## Requirements

- Separate portable worklog behavior from personal profile data and connector
  details.
- Define the portable workflow: determine the reporting window, inventory work
  sources, classify substantive activity, preserve unrelated existing content,
  write or patch the intended artifact, and verify by read-back.
- Treat timezone, destination paths, filename variants, metadata, section
  ownership, maximum follow-up links, TaskNotes policy, and connector/fallback
  choices as profile data rather than core instructions.
- Evaluate private standalone skill, optional overlay, and future installer
  profile mechanisms against privacy, portability, update safety, and platform
  neutrality.
- Specify precedence and failure behavior when a profile, source connector, or
  destination is unavailable.
- Recommend whether `se-worklog` belongs in the public core, an optional family,
  or a private companion after the boundary is proven.

## Acceptance Criteria

- [ ] The design identifies every personal datum that must not ship in the
      public default payload.
- [ ] The generic workflow can be described without an Obsidian-specific path or
      one user's naming convention.
- [ ] The chosen profile/overlay approach preserves user edits and supports
      explicit write-through/read-back verification.
- [ ] Privacy, migration, install/update/remove, and failure-mode implications
      are documented.
- [ ] Any implementation work is split into separately approved follow-up tasks
      with testable acceptance criteria.

## Out of Scope

- Shipping personal vault paths, identities, or private metadata in this task.
- Changing the existing daily-note automation before the design is approved.
- Adding a general configuration system solely to satisfy an unproven need.

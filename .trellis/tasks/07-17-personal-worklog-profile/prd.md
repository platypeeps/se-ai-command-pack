# Design personal worklog profile boundary

## Goal

Design a generic worklog skill and a private profile or overlay mechanism for user-specific Obsidian paths, timezone, metadata, preservation rules, and TaskNotes behavior without placing personal contracts in the public core pack.

## Background

The recurring daily-note workflow is valuable and stable enough to deserve
reusable instructions, but its exact vault paths, filename variants, timezone,
metadata, connector fallback, and TaskNotes policy are personal. The public pack
currently installs the same framework-neutral payload for every user and has no
profile/config contract.

## Approved Decision

**Approved on 2026-07-22.** The user approved a public, output-only
`se-worklog` skill plus a private automation/profile layer that owns
destinations, scheduling, write-back, and private operational values.

The approval evidence is the explicit boundary supplied for this task:
"a public, output-only `se-worklog` skill plus private automation/profile
handling destinations, scheduling, write-back, and private operational
values." This approval completes the design decision only. It does not
authorize creating either follow-up task, shipping the public skill, changing
public templates or release surfaces, or modifying private automation.

## Requirements

- Separate portable worklog behavior from personal profile data and connector
  details.
- Define portable synthesis: determine the reporting window, inventory supplied
  work sources, classify substantive activity, and return the intended artifact
  without destination discovery or mutation.
- Define private delivery: resolve the configured destination, preserve
  unrelated existing content, write or patch the owned content, and verify by
  direct read-back.
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

- [x] The design identifies every personal datum that must not ship in the
      public default payload. Evidence: `design.md`, "Private data inventory."
- [x] The generic workflow is described without a product-specific path or one
      user's naming convention. Evidence: `design.md`, "Portable public
      `se-worklog`."
- [x] The chosen private-layer approach preserves user edits and requires
      explicit write-through/read-back verification. Evidence: `design.md`,
      "Private automation/profile layer" and "Scenario validation."
- [x] Privacy, migration, install/update/remove, and failure-mode implications
      are documented. Evidence: `design.md`, "Lifecycle And Failure Contract."
- [x] Implementation work is split into two paste-ready follow-up proposals,
      each requiring separate approval and testable acceptance criteria.
      Evidence: `implement.md`, "Uncreated follow-up proposals." Neither task
      was created.

## Out of Scope

- Shipping personal vault paths, identities, or private metadata in this task.
- Changing the existing daily-note automation before the design is approved.
- Adding a general configuration system solely to satisfy an unproven need.

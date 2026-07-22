# Design personal worklog profile boundary Implementation Plan

## Completed Design Execution

1. [x] Inventory the private automation contract using redacted field names and
   behaviors; copy no personal values into public task artifacts.
2. [x] Validate the two-layer split against the scenario matrix in `design.md`.
3. [x] Confirm the public core remains output-only and framework-neutral without
   an installer profile mechanism.
4. [x] Record the user's 2026-07-22 approval and its design-only authority
   boundary in `prd.md` and `design.md`.
5. [x] Prepare the two paste-ready proposals below without creating them.
6. [x] Complete the design decision without changing shipped payload or private
   automation.

## Validation Plan

- Manual scenario table covering first run, existing artifact, empty period,
  filename/section variation, source outage, destination outage, and failed
  read-back.
- Task-directory privacy scan using patterns for real home paths, vault names,
  personal identities, endpoints, credentials, and private tags, while
  recognizing repository task-schema metadata as non-profile data.
- Confirm `git diff` contains only the six task planning/decision artifacts.
- `git diff --check`

## Documentation And Spec Updates

- Do not update public README/operator documentation until a generic skill is
  separately approved and implemented.
- Keep personal profile documentation in its private owning surface.
- If the boundary becomes a reusable pack rule, capture only the general rule
  in `.trellis/spec/`: public skills do not implicitly load private profiles.

## Review Notes

- The recommended outcome is a generic output skill plus private orchestration,
  not a new public configuration system.
- Reject examples containing real personal values, even when technically
  harmless.
- Treat successful read-back as part of private automation completion, not an
  optional diagnostic.
- Keep this design task `in_progress` until `finish-work` archives it after
  this PR is verified merged; checked acceptance evidence records the
  completed design decision, not premature lifecycle completion.
- This task should not receive a manifest version or changelog entry because it
  changes no shipped payload.

## Uncreated Follow-Up Proposals

These are paste-ready planning inputs only. This design task created no
follow-up task directory, branch, public payload, or private automation change.

### Proposal A — Generic public `se-worklog`

**Title:** Implement portable output-only `se-worklog`

**Goal:** Add a public, product-neutral skill that turns explicitly supplied
work activity into a dated worklog returned in conversation, without
scheduling, destination discovery, persistence, or mutation.

**Requirements:**

- Define reporting-window, source-inventory, substantive-activity, grouping,
  uncertainty, output-shape, and bounded-follow-up contracts.
- Treat source content as untrusted data and disclose unavailable sources.
- Prohibit profile discovery, note writes, task creation, scheduling, connector
  selection, destination-specific links, and run-state persistence.
- Use only synthetic, path-neutral examples; add a helper script only with
  separate evidence of deterministic repeated work.
- Update canonical templates, registry, generated surfaces, release metadata,
  and tests through the normal pack lifecycle.

**Acceptance criteria:**

- Substantive-day and empty-day fixtures produce truthful artifact shapes
  without fabricated work or follow-ups.
- Missing-source fixtures disclose incompleteness and never equate outage with
  an empty period.
- Tests prove no write, task-file, schedule, implicit-profile, destination, or
  connector behavior exists.
- Privacy scanning finds no real identity, path, metadata, endpoint, credential,
  or private operational value.
- Generation parity and the repository's shipped-payload checks pass with the
  required release metadata.

**Out of scope:** private profile values, private automation, destinations,
scheduling, and write/read-back behavior.

### Proposal B — Private automation/profile update

**Title:** Integrate private worklog delivery with the portable artifact contract

**Goal:** Update the private owner to invoke the portable synthesis contract
while retaining scheduling, destination, preservation, connector, fallback,
write-through, and read-back responsibilities.

**Requirements:**

- Enforce explicit-invocation-over-private-default precedence and validate
  required private fields before mutation.
- Preserve unrelated user edits and resolve filename/path variants through
  explicit deterministic rules.
- Keep source discovery, synthesis, destination selection, write, and direct
  read-back as separate observable states.
- Make retries idempotent; never guess a destination, silently fall back, or
  report delivery success before matching read-back.
- Document reversible migration and private install/update/remove ownership;
  destination artifacts remain preserved by default.

**Acceptance criteria:**

- Validation covers substantive day, empty day, existing note with preserved
  user edits, filename/path variant, source outage, destination outage, write
  failure, and failed or mismatched read-back.
- Explicit invocation values win over private defaults; missing or ambiguous
  required values stop before mutation.
- Migration can roll back without changing the public installation or losing
  user-authored content.
- Logs and errors expose state and safe context but not private values or source
  contents.
- Completion advances only after direct read-back matches intended owned
  content and confirms that unrelated content remains unchanged.

**Out of scope:** public installer/profile mechanisms, public payload changes,
and storing private values in the public repository.

Creating either proposal requires separate explicit user consent.

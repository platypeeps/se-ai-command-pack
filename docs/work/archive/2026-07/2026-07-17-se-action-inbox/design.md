# Implement se-action-inbox Design

## Overview

Add `se-action-inbox` as a read-only triage skill that turns a bounded set of
communication and knowledge sources into a deduplicated review queue. Its core
job is epistemic: distinguish actions somebody actually assigned or accepted
from requests, suggestions, and model inference before ranking anything.

The skill belongs to Coordinate. It sits after source-specific reading such as
thread digests and before `se-plan` or connector-specific task creation. The
canonical skill remains framework-neutral: Slack, Notion, email, meeting notes,
and Obsidian are capability examples rather than required integrations.

## Proposal

Create `templates/skills/se-action-inbox/SKILL.md` with this compact argument
surface:

- `sources=`: supplied files, links, threads, records, or connected-source hints;
  required when the current context does not identify a bounded source set.
- `since=`: optional reporting boundary; never imply full inbox coverage when
  history before the boundary was not searched.
- `owner=`: action owner to focus on; default to the requesting user only when
  identity is available, otherwise keep all owners explicit.
- `projects=`: optional project/domain filter.
- `include=inferred|explicit-only`: default `explicit-only`; inferred candidate
  actions are opt-in and always separated from commitments.
- `limit=`: maximum retained actions after classification and ranking.
- `detail=compact|standard`: queue-only or queue plus evidence and exclusions.

The workflow should:

1. Inventory sources, dates, access gaps, identities, and requested boundaries.
2. Extract candidate statements with their original wording and locators before
   normalizing them.
3. Classify each candidate as `assigned`, `committed`, `requested`, `proposed`,
   or `inferred`; separately classify lifecycle state as `open`, `completed`,
   `cancelled`, `superseded`, `blocked`, or `unclear`.
4. Preserve source, locator, speaker/author, owner, action text, evidence date,
   due date, project, confidence, and ambiguity notes. Unknown fields remain
   `unknown`; relative dates retain their source context until safely resolved.
5. Deduplicate only when normalized action, owner, and intended outcome match.
   Merge all locators and keep conflicting dates/states visible rather than
   selecting one silently.
6. Suppress completed, cancelled, or superseded candidates from the active
   queue while reporting why they were excluded.
7. Rank active items by sourced urgency, impact/importance, dependency pressure,
   and classification confidence. The rank explanation must expose which
   factors are evidence and which are judgment.
8. Return an active queue, possible-actions section when enabled, conflicts and
   ambiguities, excluded/resolved items, source coverage, and recommended next
   handling. Accepted actions may be handed to `se-plan`; task creation remains
   a separate explicit operation.

Register the skill under Coordinate/current registry and add it as a consumer
of `source-standards.md`. Add it to the external-input injection safety set.

## Boundaries And Non-Goals

- Do not create tasks, reminders, calendar events, replies, reactions, or source
  mutations.
- Do not treat mention, discussion, or a recommendation as assignment.
- Do not infer that the requesting user owns every unattributed action.
- Do not invent deadlines, priority, project, completion state, or authority.
- Do not replace `se-plan`; action inbox identifies and reviews commitments,
  while plan expands an accepted goal/action into milestones and dependencies.
- Do not replace `se-thread-digest`; the digest reconstructs conversation
  outcomes, while action inbox reconciles actionable records across sources.
- Do not claim comprehensive coverage when connectors, channels, pages, or the
  requested time range were inaccessible.

## Affected Files

- `templates/skills/se-action-inbox/SKILL.md` — new canonical skill.
- `installer/registry.py` — Coordinate/current registration and shared-reference fan-out.
- `manifest.json` — generated platform payload rows.
- `tests/test_skills.py` — classification, provenance, no-invented fields,
  deduplication, resolved-item, injection, and read-only pins.
- `tests/test_generate.py` — registry/fan-out coverage where needed.
- `README.md`, `docs/SE_AI_COMMAND_PACK.md`, `CHANGELOG.md`, and manifest version.

No connector implementation is required. Existing connector/tool calls remain
runtime capabilities selected by the host platform.

## Risks And Edge Cases

- “Can you…” can be a request or conversational question. Preserve ambiguity
  unless context establishes an action and owner.
- One action may be repeated with a changed deadline or owner. Treat conflicting
  metadata as a review item, not an ordinary duplicate.
- Completion evidence may occur in a different source or use indirect language.
  Exclude only when evidence is strong; otherwise mark state unclear.
- Forwarded messages and quoted threads can falsely attribute commitments.
  Track the original speaker and distinguish quotation from current instruction.
- Relative dates such as “Friday” depend on message timestamp and timezone.
  Resolve only when both are known; otherwise retain the phrase and ambiguity.
- Ranking can manufacture urgency from tone. Use explicit deadlines,
  dependencies, and stated impact before linguistic intensity.
- Private-source synthesis can expose information across audiences. Return only
  to the requesting context and flag sensitive excerpts rather than expanding them.
- Large inboxes can overwhelm context. Inventory and process in bounded pages,
  then report coverage and truncation.

## Validation

- Pin the five action classes and explicit-only default in skill-content tests.
- Pin required source locator, owner/due-date unknown handling, lifecycle state,
  deduplication conflict preservation, and resolved-item exclusion.
- Pin read-only language, separate mutation consent, external-input rule, and
  source-standard reference.
- Exercise manual scenarios for an explicit assignment, self-commitment,
  ambiguous request, repeated action with conflicting dates, completion in a
  second source, inaccessible source, and empty active queue.
- Run `make generate`, focused generator/skill tests, `make check`, and
  `git diff --check`.

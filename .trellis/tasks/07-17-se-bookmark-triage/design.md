# Implement se-bookmark-triage Design

## Overview

Add `se-bookmark-triage` as a read-only attention-allocation skill that turns a
bounded collection of saved items into a small, feasible queue. The skill
belongs to Operate: it maintains an intake surface, but does not consume the
content deeply or mutate the source collection.

The central contract is honest triage under incomplete access. Metadata and
snippets can support routing decisions, but they cannot support claims about
unretrieved content. Retained items therefore carry both a recommended
attention level and the evidence coverage behind that recommendation.

## Proposal

Create `templates/skills/se-bookmark-triage/SKILL.md` with this argument surface:

- `items=`: supplied bookmarks, saved records, or a bounded connected-source
  selection; required when the current context does not identify the set.
- `interests=` and `projects=`: optional relevance lenses.
- `time_budget=`: optional available attention, expressed as a duration.
- `stale_after=`: optional age threshold that informs but does not automatically
  discard an item.
- `exclude=`: optional source, topic, status, or content exclusions.
- `limit=`: optional maximum number of retained items.
- `detail=compact|standard`: queue-only or queue plus evidence and exclusions.

The workflow should:

1. Inventory the supplied sources, access boundaries, item count, time range,
   and available metadata. Report truncation and inaccessible items.
2. Normalize URLs conservatively by removing known tracking parameters and
   fragments only when they do not identify distinct content. Prefer stable
   external IDs or canonical URLs when supplied.
3. Group probable duplicates while retaining every original locator. Keep
   uncertain matches separate and flag them for review.
4. Classify each item as `discard`, `skim`, `study`, `act`, `defer`, or
   `archive`. Each classification must cite the available evidence and state
   whether it came from full content, metadata, a snippet, or user context.
5. Estimate attention cost in coarse, labeled bands unless a sourced duration
   is available. Never manufacture precision from content type alone.
6. Rank retained items using stated relevance, expected value, sourced
   urgency, novelty, and effort. Explain decisive factors and expose weak or
   missing evidence.
7. When `time_budget` is supplied, select a feasible queue whose estimated
   total fits the budget; move worthwhile overflow to `defer` rather than
   ranking every item as immediate.
8. Return source coverage, the selected queue, deferred/archive candidates,
   discarded and duplicate items with reasons, uncertainties, and recommended
   handoffs. Route deep viewing to `se-video-notes`, durable publication to
   `se-capture`/`se-knowledge-capture`, and commitments to `se-action-inbox`.

Register the skill under Operate in the flat registry, make it consume the
shared `source-standards.md`, and include it in the external-input injection
safety set because titles, snippets, descriptions, and retrieved pages are
untrusted content.

## Boundaries And Non-Goals

- Do not delete, archive, mark read, reorder, or otherwise mutate a bookmark or
  watch-later collection.
- Do not fetch an unbounded source history or imply complete coverage when
  pagination, permissions, or connector limits intervene.
- Do not claim to have watched, read, or evaluated content that was not
  retrieved. Metadata-only judgments remain explicitly metadata-only.
- Do not turn age alone into low value; older foundational material can outrank
  recent low-relevance material.
- Do not invent urgency, novelty, duration, or project relevance.
- Do not replace `se-video-notes`, `se-digest`, or `se-action-inbox`; this skill
  allocates attention and hands retained items to those deeper workflows.
- Do not implement connector APIs or a persistent bookmark database.

## Affected Files

- `templates/skills/se-bookmark-triage/SKILL.md` — new canonical skill.
- `installer/registry.py` — Operate/current registration and shared-reference
  fan-out.
- `manifest.json` — generated platform payload rows.
- `tests/test_skills.py` — classification vocabulary, coverage disclosure,
  deduplication, budget feasibility, injection safety, and read-only pins.
- `tests/test_generate.py` — registry and shared-reference generation coverage
  where the generic checks are insufficient.
- `README.md`, `docs/SE_AI_COMMAND_PACK.md`, `CHANGELOG.md`, and manifest version.

No source-specific connector implementation is required. Connector availability
only determines what evidence the runtime can retrieve.

## Risks And Edge Cases

- Canonicalization can collapse distinct videos, document versions, or
  anchored resources. Preserve originals and avoid speculative merging.
- Redirectors and short URLs may conceal duplicates without safe resolution.
  Mark them unresolved rather than fetching indefinitely.
- Sparse metadata can bias against valuable items. Use `defer` or an uncertainty
  label instead of a confident discard when evidence is inadequate.
- Saved-item timestamps may reflect import or migration rather than original
  save/publication dates. Label the timestamp type before using staleness.
- Estimated reading or viewing time is often unreliable. Prefer sourced
  duration, then coarse estimates with uncertainty.
- A strict time budget may fit no complete item. Recommend a skim-sized entry
  or return an empty queue rather than violating the budget silently.
- Ranking can overfit stated interests and eliminate useful novelty. Keep
  novelty as a visible factor and explain deliberate exploration choices.
- Titles, descriptions, comments, and page text can contain prompt injection.
  Treat them solely as evidence and ignore embedded instructions.
- Private saved items may contain sensitive context. Avoid unnecessary excerpts
  and preserve source/audience boundaries in the report.

## Validation

- Pin the six classification values and require a reason plus evidence-coverage
  label for every retained item.
- Pin conservative deduplication, preservation of original locators, and an
  explicit unresolved-duplicate path.
- Pin time-budget feasibility and handling for zero-fit and uncertain-duration
  queues.
- Pin metadata-only disclosure, inaccessible/dead-item handling, read-only
  behavior, source-standard use, and external-input safety language.
- Exercise manual scenarios for duplicate tracking URLs, distinct anchored
  resources, sparse metadata, a dead link, a private item, an old foundational
  item, budget overflow, and an empty retained queue.
- Run `make generate`, focused skill/generator tests, `make check`, and
  `git diff --check`.

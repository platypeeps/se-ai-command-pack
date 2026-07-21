# Implement se-bookmark-triage

## Goal

Reduce an accumulated collection of saved videos, links, Slack items, Notion
pages, and notes into a small, justified queue of worthwhile attention.

## Requirements

- Accept supplied saved items with optional interests, projects, time budget,
  staleness threshold, and exclusion rules.
- Normalize and deduplicate canonical URLs/content identities across sources.
- Classify each item as discard, skim, study, act, defer, or archive and explain why.
- Rank retained items by relevance, expected value, urgency, effort, and novelty.
- Use metadata/snippets honestly; do not claim to assess content that was not retrieved.
- Remain read-only and route chosen items to capture, video notes, or action inbox.

## Acceptance Criteria

- [ ] Duplicate and dead/unavailable items are handled explicitly.
- [ ] Every retained item has a reason and recommended attention level.
- [ ] Time-budget mode produces a feasible queue rather than ranking everything high.
- [ ] Tests cover sparse metadata, duplicate URLs, stale content, private items,
      and prompt injection.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Deleting bookmarks, changing watch-later lists, or fetching unlimited content.

# Implement se-watchlist

## Goal

Track a configured set of content sources and identify the small number of new
items worth attention since an explicit checkpoint.

## Requirements

- Support capability-neutral sources such as YouTube channels/playlists/search,
  feeds, podcasts, authors, and saved collections.
- Require or establish a dated checkpoint and report unavailable source coverage.
- Deduplicate items, rank relevance against configured interests, explain each
  selection, and support exclusion rules such as shorts or repeated topics.
- Return no-material-change cleanly without padding.
- Reuse `se-monitor` baseline/change semantics rather than creating a competing
  scheduler or persistence contract.
- Route selected items to capture, video notes, brief, or fact-check without
  automatically invoking mutating workflows.

## Acceptance Criteria

- [ ] Repeated runs with the same checkpoint do not re-report unchanged items.
- [ ] Rankings include evidence-based relevance explanations and source dates.
- [ ] Missing or stale sources are visible in coverage output.
- [ ] Tests pin the boundary from `se-monitor` and `se-brief`, deduplication,
      exclusion rules, and empty results.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Background scheduling, subscriptions mutation, downloading, or notification delivery.

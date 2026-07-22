# Implement se-watchlist Design

## Overview

Add `se-watchlist` under Operate as a read-only delta review over configured
content sources since an explicit checkpoint. It reuses `se-monitor` baseline/
change semantics, ranks only materially relevant new items, and returns a truthful
empty result rather than padding.

## Proposal

Accept capability-neutral source definitions (channels, playlists/searches, feeds,
podcasts, authors, saved collections), dated checkpoint, interests, exclusions,
ranking depth, and optional profile/overlay. If no checkpoint exists, establish a
visible baseline and avoid claiming historical completeness.

Inventory source coverage, retrieval time, source timezone/date semantics, access
gaps, and stale/unavailable sources. Normalize item identity using stable IDs,
canonical URLs, publication metadata, and content fingerprints; deduplicate cross-
posted or repeated items.

Filter items strictly after the checkpoint, apply exclusions such as shorts,
duration, language, or repeated topics, and score relevance with evidence from
configured interests and item metadata/content. Each selected item includes source,
date, why relevant, novelty, confidence, and suggested read-only route to capture,
video notes, brief, or fact-check. Do not invoke those routes automatically.

Return coverage, checkpoint/change summary, ranked selection, exclusions/dedupes,
and `no-material-change` when appropriate. Scheduling and checkpoint persistence
belong to `se-monitor` or the host, not a competing watchlist scheduler.

## Boundaries And Non-Goals

- Do not schedule, subscribe/unsubscribe, download, notify, or mutate source systems.
- Do not re-report unchanged items for the same checkpoint.
- Do not infer coverage for unavailable sources or pad empty results.
- Do not duplicate `se-brief` synthesis or `se-monitor` persistence.

## Affected Files

- Canonical skill, Operate-family registration, monitor/source/profile references,
  manifest, fixtures/tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Reposts and URL variants can evade dedupe; combine stable identifiers and fingerprints.
- Publication dates may change or lack timezone; disclose normalization.
- Stale feeds can look like no change; separate coverage failure from empty delta.
- Personal interest signals may be private; keep explanations outward-safe.
- Topic repetition requires semantic, not only title, comparison.

## Validation

- Pin checkpoint/baseline semantics, coverage, identity/dedupe, exclusions,
  evidence-based ranking, empty result, downstream routes, and skill boundaries.
- Test repeated runs, cross-posts, missing/stale sources, exclusion rules, empty
  deltas, timezone edges, repeated topics, sensitive interests, and injection.
- Run generation, focused tests, full checks, and diff check.

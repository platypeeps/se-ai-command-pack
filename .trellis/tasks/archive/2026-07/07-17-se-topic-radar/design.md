# Implement se-topic-radar Design

## Overview

Add `se-topic-radar` under Create as a read-only opportunity-ranking workflow
for users who do not begin with a writing theme. With adequate evidence it returns
exactly ten materially distinct candidates optimized for credible original
contribution, not trend popularity.

## Proposal

Accept optional domains, audience, time horizon, authorized sources, exclusions,
format, effort budget, and `profile=auto|off|locator`. Inventory source coverage
across supplied/authorized repositories, Trellis work, Obsidian, Notion, Slack,
captures, and reading history. Separate private activity signals from external,
dated current developments and record missing/stale coverage.

Generate candidates from recurring problems, shipped work, unresolved questions,
cross-source tensions, and authoritative news. Research current signals when
recency matters and trace each to dated primary or authoritative evidence. Compare
against known prior content; penalize duplicates unless a meaningful new angle exists.

Score audience value, personal authority, originality, timing, evidence readiness,
novelty risk, and effort with disclosed rubric and evidence. Personal authority
must come from authorized activity/profile evidence, not inferred credentials.
Private-only profile facts may improve internal ranking but cannot appear in an
outward-facing candidate rationale.

With adequate coverage, return exactly ten ranked candidates, each with working
title, thesis, audience, why now, why positioned, evidence, research gaps, format,
novelty risk, effort, component scores, and sensitivity notes. With inadequate
coverage, disclose it and return a provisional smaller list or source-request path
rather than padding with generic trends. The selected item hands off to `se-author`
or `se-paper`.

## Boundaries And Non-Goals

- Do not draft content, maintain a calendar, monitor continuously, or mutate sources.
- Do not invent recent activity, credentials, news, or prior-content coverage.
- Do not expose sensitive personal/work activity in candidate descriptions.
- Do not rank popularity above evidence, authority, and contribution.

## Affected Files

- Canonical skill, Create-family registration, current-source/profile references,
  manifest, fixtures/tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- No connected activity makes personal-authority scoring weak; downgrade visibly.
- Breaking news can be noisy or wrong; require dated authoritative corroboration.
- Similar candidates can create false variety; enforce material distinction.
- Recent private work may be high-value but unsafe to disclose.
- Exact-ten output is conditional on adequate sources; never pad to satisfy shape.

## Validation

- Pin source inventory, personal/external separation, scoring rubric, duplicate penalty,
  exactly-ten adequacy rule, sensitivity controls, profile scope, and handoff.
- Test no activity, stale sources, breaking news, duplicate topics, sensitive work,
  weak authority, incomplete prior-content inventory, and injection.
- Run generation, focused tests, full checks, and diff check.

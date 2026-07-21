# Implement se-knowledge-gap Design

## Overview

Add `se-knowledge-gap` under Understand as a bounded audit of an existing
knowledge system. It maps claims and decisions across authorized sources, then
identifies missing, conflicting, stale, unsupported, duplicated, or inaccessible
knowledge without conducting the new research needed to close those gaps.

## Proposal

Accept `topic=`, `decision=`, `audience=`, `sources=`, `fresh_after=`,
`authority=`, and `detail=brief|standard`. Require an explicit source inventory
or bounded connected-source scope; record connectors, containers, query terms,
date range, permissions, pagination/truncation, and inaccessible areas.

Normalize terminology/aliases before search and preserve the query map so a
vocabulary mismatch is not mistaken for absence. Build a claim/decision ledger
with statement, source/locator, owner/authority signal, date, status, confidence,
dependencies, and supporting/conflicting records.

Classify findings as:

- `missing` — required knowledge absent from sufficiently covered scope;
- `access-gap` — potentially present but unavailable/unsearched;
- `stale` — evidence older than the stated threshold or superseded;
- `conflicting` — incompatible positions with both authorities/dates preserved;
- `unsupported` — claim/decision lacks rationale or evidence;
- `duplicate-authority` — competing canonical records; or
- `unresolved` — known open question/decision.

Never turn “not found” into “does not exist” unless coverage is sufficient and
explicitly justified. Rank gaps by decision impact, urgency, dependency/blocking
effect, evidence confidence, and closure effort without fake precision.

Return audit scope/coverage, claim/decision map, prioritized gap register,
contradiction table, stale/duplicate authority findings, and closure plan. Route
individual claim verdicts to `se-fact-check`, new external evidence to
`se-research`, consolidation to an explicit documentation task, and monitoring
to `se-monitor`. Remain read-only.

Register under Understand, fan in source standards, and add injection safety.

## Boundaries And Non-Goals

- Do not rewrite notes/pages, select a canonical source, or resolve contradictions silently.
- Do not run unlimited external research or imply inaccessible sources are empty.
- Do not treat duplication as wrong when records serve distinct contexts.
- Do not expose private cross-source content beyond the authorized requesting context.

## Affected Files

- Canonical skill, registry/shared reference, manifest, coverage/classification
  tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Connector/query coverage is easy to overstate; report it structurally.
- Terminology drift creates false gaps; preserve aliases and query attempts.
- Authority may be social rather than documented; label inference and avoid choosing.
- Staleness thresholds vary by claim type; apply the user threshold and surface exceptions.
- Cross-system synthesis can leak sensitive data; minimize excerpts and preserve scopes.

## Validation

- Pin source/query coverage, alias handling, all finding classes, contradiction
  preservation, freshness, ranking factors, and read-only routing.
- Test incomplete access, stale source, terminology mismatch, duplicate canonical
  records, conflicting authority, empty result, and injection.
- Run generation, focused tests, full checks, and diff check.

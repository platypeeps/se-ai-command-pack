---
title: Argument vocabulary verbosity migration
status: done
created: 2026-08-04
branch: audit/arg-vocab-verbosity
---
# Argument vocabulary verbosity migration (mechanical)

## Goal

Canonicalize the verbosity axis to `depth=brief|standard|deep` across ~29 skills
— 23 that rename `length=`/verbosity-`detail=` → `depth=`, plus 6 that already
declare `depth=` with off-ladder values needing normalization — clearing the
`depth=` name collision first. Mechanical rename + value normalization only; the
`format=` density judgment is a separate child (D-3). Consumer-visible; part of
A-006.

Parent decision + rationale: `07-25-audit-skill-arg-vocabulary/design.md`.
Ordering + validation gate: parent `implement.md`. Land after
`08-04-arg-vocab-reference`, before `08-04-arg-vocab-format`.

## Requirements

- **First, clear the `depth=` collision:** rename `se-technical-editor`
  `depth=full|focused` (editorial coverage, requires `passes=`) →
  `coverage=full|focused`. Resolve `se-author length=` exact-word-count via a
  separate `target_words=` argument (the enforced `depth=` ladder has no numeric
  slot, so a numeric `depth=<n>` is not an option); its tier form migrates to
  `depth=`.
- Rename every `length=` and verbosity-sense `detail=` → `depth=` (23 skills),
  values a **subset** of the ladder `brief|standard|deep` (not order-dependent).
  Each skill defaults explicitly. `brief|full`→`brief|deep` (subset; no invented
  `standard`).
- **Also normalize the 6 existing `depth=` declarations that carry off-ladder
  values** so enforcement-last passes: `se-meeting-prep depth=quick|standard`,
  `se-handoff depth=compact|standard`, `se-red-team depth=quick|standard|deep`,
  `se-research depth=quick|standard|deep`, `se-postmortem depth=brief|full`,
  `se-premortem depth=brief|full`.
- Value map: `short`/`compact`/`quick`/`outline`→`brief`; `long`/`full`→`deep`;
  `standard` unchanged.
- **Do NOT touch `format=`** (format-density child), `sources=`/`input=`
  (locator child), or `sensitivity=`/`privacy=`/`evidence=`.
- Regenerate the `generated/skills/claude/` mirror; version bump + changelog.

## Acceptance Criteria

- [x] No skill declares `length=` or verbosity-sense `detail=`; no `depth=`
      collision remains (`coverage=` for se-technical-editor); verbosity is
      `depth=` with ladder-subset values.
- [x] `se-author` numeric length handled + documented.
- [x] `make test` + `make release-check` green; mirror regenerated; version bump
      + changelog citing A-006.

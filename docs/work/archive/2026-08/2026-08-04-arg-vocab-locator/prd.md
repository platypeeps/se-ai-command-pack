---
title: Argument vocabulary locator migration
status: done
created: 2026-08-04
branch: audit/arg-vocab-locator
---
# Argument vocabulary primary-artifact + discrete renames

## Goal

Canonicalize the *primary artifact under action* axis to `input=`, and apply the
remaining discrete renames (count collision, redaction). Consumer-visible;
part of A-006 (D-1/D-2).

Parent decision + rationale: `07-25-audit-skill-arg-vocabulary/design.md`.
Ordering + validation gate: parent `implement.md`. Land after
`08-04-arg-vocab-format`, before `08-04-arg-vocab-enforce`.

## Requirements

- **Primary-artifact rename → `input=`** (the artifact/subject being
  transformed): `source=` (se-capture, se-presentation, se-publish) and
  `inputs=` (se-digest) → `input=`. These transform a supplied primary artifact,
  the same concept as the existing `input=` on se-fact-check/se-feedback/
  se-technical-editor (left as-is).
- **Do NOT rename `sources=`** — it is the already-consistent reference-material
  axis (21 skills), a distinct reserved concept.
- **Count collision:** se-research `sources=N` → `min_sources=N`; update its
  downstream prose that references the `sources=` minimum.
- **Redaction rename:** se-red-team `detail=minimal|restricted|standard` →
  `sensitivity=minimal|restricted|standard` (values already in the canonical
  ladder; also ends se-red-team's `detail=`/`depth=` double-use). Leave
  `privacy=` and `evidence=` untouched (distinct reserved concepts, D-2).
- Preserve each argument's description; only the name changes. Regenerate the
  mirror; version bump + changelog.

## Acceptance Criteria

- [x] No primary artifact uses `source=`/`inputs=`; all use `input=`; `sources=`
      (reference) untouched.
- [x] se-research uses `min_sources=N`; no `sources=N` count remains; downstream
      prose updated.
- [x] se-red-team redaction uses `sensitivity=`; no `detail=` remains; `privacy=`
      / `evidence=` untouched.
- [x] `make test` + `make release-check` green; mirror regenerated; version bump
      + changelog citing A-006.

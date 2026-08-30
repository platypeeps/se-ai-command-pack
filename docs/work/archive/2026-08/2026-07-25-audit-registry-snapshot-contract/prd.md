---
title: Versioned registry snapshot for skill_review
status: done
created: 2026-07-25
branch: audit/registry-snapshot-contract
---
# Versioned registry snapshot for skill_review

## Goal

The shipped `skill_review.py` stops AST-parsing `installer/registry.py` of reviewed checkouts; it consumes a versioned machine-readable snapshot instead, so registry/layout refactors cannot silently break installed copies fleet-wide.

## Requirements

- Emit a machine-readable registry snapshot (e.g. generated JSON: skills, platform registry, shared references) as part of `make generate`, drift-gated like other generated surfaces.
- `skill_review.py` consumes the snapshot; schema carries a version so installed copies detect incompatibility instead of misparsing.
- Remove the hard-coded sibling-repo layout assumptions where the snapshot can carry them.
- Behavior parity: review output unchanged for current inputs.

## Acceptance Criteria

- [x] `skill_review.py` prefers the versioned snapshot and opens
      `installer/registry.py` only as a legacy fallback when the snapshot is
      absent (transitional; see follow-up). A present-but-version-incompatible
      or malformed snapshot fails closed instead of misparsing.
- [x] Snapshot regenerates via `make generate` and drifts fail `--check`.
- [x] Tests cover snapshot consumption, the version-mismatch error path, and
      the absent-snapshot fallback (behavior parity preserved for both packs).

## Scope decision (2026-08-04)

The consumer switch is **snapshot-preferred with an AST fallback** so neither
the SE pack nor the SD-pack checkout (a tested current input this SE
`skill_review.py` also reviews) regresses before the SD repo ships its own
snapshot producer. The strict "no longer opens `installer/registry.py`" end
state is a bounded follow-up: remove the fallback once the SD pack ships a
same-schema snapshot. Rationale in `design.md`; concern ledger C-1.

## Notes

- Audit finding: A-002 (P2/M) — .trellis/audit/report-2026-07-25.md.
- Evidence: templates/skills/se-review-skills/scripts/skill_review.py:325, :341, :403, :34.

## Cross-program coordination (2026-07-25 review)

- BLOCKS the registry reshaping in `07-25-agent-artifact-kind` (new `agent` kind +
  capability fields) — in BOTH packs: skill_review.py parses se and sd checkouts, and the
  sd-ai-command-pack twin task reshapes its registry too. Land this first (or in the same
  change) and version the snapshot schema.

# Versioned registry snapshot for skill_review

## Goal

The shipped `skill_review.py` stops AST-parsing `installer/registry.py` of reviewed checkouts; it consumes a versioned machine-readable snapshot instead, so registry/layout refactors cannot silently break installed copies fleet-wide.

## Requirements

- Emit a machine-readable registry snapshot (e.g. generated JSON: skills, platform registry, shared references) as part of `make generate`, drift-gated like other generated surfaces.
- `skill_review.py` consumes the snapshot; schema carries a version so installed copies detect incompatibility instead of misparsing.
- Remove the hard-coded sibling-repo layout assumptions where the snapshot can carry them.
- Behavior parity: review output unchanged for current inputs.

## Acceptance Criteria

- [ ] `skill_review.py` no longer opens `installer/registry.py`.
- [ ] Snapshot regenerates via `make generate` and drifts fail `--check`.
- [ ] Tests cover snapshot consumption and the version-mismatch error path.

## Notes

- Audit finding: A-002 (P2/M) — .trellis/audit/report-2026-07-25.md.
- Evidence: templates/skills/se-review-skills/scripts/skill_review.py:325, :341, :403, :34.

## Cross-program coordination (2026-07-25 review)

- BLOCKS the registry reshaping in `07-25-agent-artifact-kind` (new `agent` kind +
  capability fields) — in BOTH packs: skill_review.py parses se and sd checkouts, and the
  sd-ai-command-pack twin task reshapes its registry too. Land this first (or in the same
  change) and version the snapshot schema.

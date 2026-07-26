# Maintainer docs catch-up for generated surface and setup

## Goal

Maintainer-facing docs match reality: the fresh-clone contributor flow works as written, and the payload-definition and manifest-schema references match what actually ships. (The broader `generated/`-surface and RuntimeProfile documentation is owned by `07-25-runtime-profile-gaps` — see coordination note.)

## Requirements

- Add step 0 `make setup` to README "Maintaining the pack" and the CONTRIBUTING workflow (fresh clone currently crashes on missing PyYAML).
- Extend CONTRIBUTING's never-hand-edit rule to `generated/skills/`. (Layout-table row, `make generate` surface list, and runtime-profile docs are OWNED by `07-25-runtime-profile-gaps` R2 — do not duplicate them here.)
- Correct the manifest schema `source` row (docs/SE_AI_COMMAND_PACK.md:848) — 52 rows source from generated/, not templates/.
- Align CONTRIBUTING's payload definition with the enforced gate (templates/**, generated/**, manifest.json).

## Acceptance Criteria

- [ ] A fresh clone following only the documented steps gets through `make check`.
- [ ] Schema table matches manifest reality (326 templates/ + 52 generated/ rows).
- [ ] CONTRIBUTING payload definition matches check-release-payload.py PAYLOAD_PREFIXES.

## Notes

- Audit findings: A-024 + A-023 (both P2/S) — .trellis/audit/report-2026-07-25.md.
- Evidence: README.md:440, :430; CONTRIBUTING.md:14; docs/SE_AI_COMMAND_PACK.md:848; .github/scripts/generate-skill-surfaces.py:22; Makefile:2.

## Cross-program coordination (2026-07-25 review)

- Scope split with `07-25-runtime-profile-gaps` (agent-artifacts child): that task owns the
  operator-guide documentation of `generated/` and the RuntimeProfile/overlay system.
  This task keeps `make setup`, the manifest-schema `source` row, and the CONTRIBUTING
  payload-definition/never-hand-edit fixes. Land in either order; do not duplicate scope.

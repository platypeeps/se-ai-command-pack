# Move generated skill catalog out of templates

## Goal

The source/generated boundary holds for every file: templates/skills/ contains only hand-edited sources, or the one exception is documented exactly where the boundary is declared.

## Requirements

- Preferred: emit skill-catalog.md under generated/ and repoint the se-help manifest row; remove the GENERATED_SHARED_REFERENCES special case in generate-skill-surfaces.py (:52).
- Alternative: keep the location but document the single exception at README.md:426 where templates/skills/ is declared "the only place skills are edited".
- Fan-out to consumers must keep working; payload move follows release discipline.

## Acceptance Criteria

- [ ] No do-not-edit generated file sits undocumented under templates/ (moved, or exception documented at the boundary declaration).
- [ ] `make generate --check` green; se-help still ships the catalog to all platforms.

## Notes

- Audit finding: A-003 (P3/S) — .trellis/audit/report-2026-07-25.md.
- Evidence: .github/scripts/generate-skill-surfaces.py:52; templates/skills/_shared/references/skill-catalog.md:1; README.md:426.

## Cross-program coordination (2026-07-25 review)

- Preferred route: implement WITHIN `07-25-agent-artifact-kind`'s renderer-hook refactor
  (same generator code); standalone is acceptable only if that task is deferred — avoid
  two concurrent conflicting edits to generate-skill-surfaces.py.

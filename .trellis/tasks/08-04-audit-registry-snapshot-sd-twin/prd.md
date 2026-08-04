# SD pack twin: registry snapshot producer parity

## Goal

Mirror the generated registry-snapshot.json producer (schemaVersion 1) added to se-ai-command-pack's generate-skill-surfaces.py in the SD command pack, so SD checkouts ship the same-schema snapshot and skill_review.py can prefer it there too. Precondition for removing the AST fallback fleet-wide (see audit-registry-snapshot-ast-removal). Snapshot schema: schemaVersion, familyOrder, skills[{name,family}], platforms (sorted), sharedReferences.

## Requirements

- TBD

## Acceptance Criteria

- [ ] TBD

## Notes

- Keep `prd.md` focused on requirements, constraints, and acceptance criteria.
- Lightweight tasks can remain PRD-only.
- For complex tasks, add `design.md` for technical design and `implement.md` for execution planning before `task.py start`.

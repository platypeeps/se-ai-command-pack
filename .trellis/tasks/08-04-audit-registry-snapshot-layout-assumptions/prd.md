# Evaluate remaining skill_review layout assumptions for snapshot inclusion

## Goal

Speculative follow-up. skill_review.py still derives FIRST_PARTY_REMOTES, discovery globs, and adapter paths from code layout rather than the registry snapshot. Decide whether any of these are registry data that belong in the versioned snapshot (extending schemaVersion) or should stay layout-derived. Read-only assessment first; only expand the snapshot schema if it removes a real layout coupling.

## Requirements

- TBD

## Acceptance Criteria

- [ ] TBD

## Notes

- Keep `prd.md` focused on requirements, constraints, and acceptance criteria.
- Lightweight tasks can remain PRD-only.
- For complex tasks, add `design.md` for technical design and `implement.md` for execution planning before `task.py start`.

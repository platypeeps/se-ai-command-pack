# Remove skill_review AST registry fallback once both packs ship snapshots

## Goal

BLOCKED ON 08-04-audit-registry-snapshot-sd-twin. Once both SE and SD packs ship the generated registry snapshot producer, a bounded PR removes _parse_registry and its AST helpers (_assignment, _string_value, _call_value) plus the fallback branch and symlink-fallback path in skill_review.py, and makes _load_registry_snapshot the sole registry source. This meets the strict acceptance criterion 'skill_review.py no longer opens installer/registry.py' fleet-wide. Update the code-spec quality-guidelines.md snapshot-preferred section and drop the AST-fallback tests. Do not start until the SD twin producer has shipped.

## Requirements

- TBD

## Acceptance Criteria

- [ ] TBD

## Notes

- Keep `prd.md` focused on requirements, constraints, and acceptance criteria.
- Lightweight tasks can remain PRD-only.
- For complex tasks, add `design.md` for technical design and `implement.md` for execution planning before `task.py start`.

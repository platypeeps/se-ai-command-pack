# Lint gate for shipped payload Python

## Goal

The pack's only consumer-shipped executable, templates/skills/se-review-skills/scripts/skill_review.py (1952 lines), passes the same ruff/mypy bar as every other repo-own Python file — and the defects the tools already find are fixed.

## Requirements

- Add the script path to the ruff and mypy commands in Makefile and .github/workflows/tests.yml.
- Fix the known findings: ruff B905 (zip without strict=) at :297; mypy errors at :673 (Optional passed as required) and :268 (assignment type).
- Coordinate with the dead-wrapper question (ledger A-026): include scripts/se-ai-command-pack-skill-review.py in the gate only if it is kept.

## Acceptance Criteria

- [x] `make lint` covers skill_review.py and passes.
- [x] CI lint lane mirrors the scope.
- [x] The three known defects are fixed (payload change: version bump + changelog).

## Notes

- Audit finding: A-036 (P2/S, merged tooling+improvements) — .trellis/audit/report-2026-07-25.md.
- Evidence: Makefile:27-28; .github/workflows/tests.yml:44-45; skill_review.py:297, :673, :268.

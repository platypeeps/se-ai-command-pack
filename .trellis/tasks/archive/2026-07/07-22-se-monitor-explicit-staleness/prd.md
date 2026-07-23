# Define deterministic monitor-state staleness

## Goal

Review snapshot 726d2d57c275b1d600940fbd523528081a43a898bfdaac2cdad34dec06fba0ae; finding 5.2.12.1. Define when monitor state is stale through an explicit policy or source-specific continuity failure so identical state selects the same recovery branch. Affected templates: templates/skills/se-monitor/SKILL.md and templates/skills/_shared/references/state-schema.md; focused tests under tests/test_skills.py.

## Requirements

- Define a deterministic reason that a readable version-1 monitor state is
  stale instead of relying on an unstated age judgment.
- Support explicit caller policy and source-specific continuity or coverage
  failure without treating age alone as stale unless a freshness horizon is
  explicitly part of the contract.
- Keep stale-state dates, source coverage, gaps, and qualified-comparison rules
  visible.
- Preserve missing, malformed, newer-version, and first-baseline branches.
- Keep the shared state schema compatible with both `se-monitor` and
  `se-watchlist`.
- Change only canonical templates under `templates/skills/**`, then regenerate
  supported targets through the normal sync path.

## Acceptance Criteria

- [ ] Fresh, explicitly stale, coverage-gap stale, and no-policy fixtures select
      deterministic branches.
- [ ] A readable state is not labeled stale solely from an implicit age rule.
- [ ] Qualified stale-state comparison still cannot convert non-observation
      into resolution.
- [ ] Existing version, malformed-state, and source-recovery behavior remains
      intact.
- [ ] Focused monitor/state-schema tests and generated target checks pass.

## Notes

- Finding: `5.2.12.1`; routing state: `untracked`.
- Coordinate the shared state-schema wording with the separate watchlist
  sentinel task.

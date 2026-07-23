# Align watchlist state sentinel terminology

## Goal

Review snapshot 726d2d57c275b1d600940fbd523528081a43a898bfdaac2cdad34dec06fba0ae; finding 5.6.9.1. Document baseline=new for se-monitor and checkpoint=new for se-watchlist without causing either strict argument surface to accept the other's name. Affected templates: templates/skills/_shared/references/state-schema.md and templates/skills/se-watchlist/SKILL.md; focused tests under tests/test_skills.py.

## Requirements

- Make the shared state reference caller-neutral where it describes baseline
  creation.
- Explicitly document `baseline=new` for `se-monitor` and `checkpoint=new` for
  `se-watchlist`.
- Preserve each skill's strict unknown-argument stop rule; neither skill should
  accept the other skill's argument name.
- Preserve the shared version-1 state shape, recovery boundaries, pending-item
  semantics, and first-baseline behavior.
- Change only canonical templates under `templates/skills/**`, then regenerate
  supported targets through the normal sync path.

## Acceptance Criteria

- [ ] The shared reference names both caller-specific sentinels without
      implying they are interchangeable arguments.
- [ ] `se-monitor` accepts `baseline=new` and rejects `checkpoint=`.
- [ ] `se-watchlist` accepts `checkpoint=new` and rejects `baseline=`.
- [ ] First-baseline and per-source recovery behavior is unchanged.
- [ ] Focused watchlist/monitor contract tests and generated target checks pass.

## Notes

- Finding: `5.6.9.1`; routing state: `untracked`.
- Coordinate shared state-schema edits with the monitor-staleness task.

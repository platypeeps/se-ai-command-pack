# Pack-wide skill argument vocabulary

## Goal

One argument vocabulary across the 53-skill key=value interface: identical concepts use identical names and value sets, so a name learned on one skill transfers instead of hard-stopping on the next.

## Requirements

- Inventory the argument axes (input locators: sources=/inputs=/input=; verbosity: length=/detail=/depth=/format= with ~10 value vocabularies; any others surfaced by the inventory).
- Define the canonical name + value set per axis in a shared reference; resolve type collisions (se-research `sources=N` count vs list semantics elsewhere, e.g. rename to `min_sources=`).
- Migrate all skills; renames are consumer-visible and need changelog coverage.
- Enforce reserved names/values in generate-skill-surfaces validation so new skills cannot reintroduce drift.

## Acceptance Criteria

- [ ] Vocabulary documented in a shared reference shipped to skills.
- [ ] `make generate --check` (or validate_skills) fails on non-canonical argument names for covered axes.
- [ ] All 53 skills conform; changelog documents every rename.

## Notes

- Audit finding: A-006 (P2/M) — .trellis/audit/report-2026-07-25.md.
- Evidence: templates/skills/se-research/SKILL.md:37, se-monitor/SKILL.md:46, se-watchlist/SKILL.md:48, tests/test_skills.py:144.

## Cross-program coordination (2026-07-25 review)

- Land BEFORE `07-25-dispatch-pilot` / `07-25-dispatch-rollout` where practical: both
  waves edit the same 53 skill bodies (7 overlap directly), and dispatch sections should
  be written in the canonical argument vocabulary once instead of being renamed after.

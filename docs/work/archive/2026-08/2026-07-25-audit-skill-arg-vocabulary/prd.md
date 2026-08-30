---
title: Pack-wide skill argument vocabulary
status: done
created: 2026-07-25
branch: task/07-25-audit-skill-arg-vocabulary
---
# Pack-wide skill argument vocabulary

## Goal

One argument vocabulary across the 53-skill key=value interface: identical concepts use identical names and value sets, so a name learned on one skill transfers instead of hard-stopping on the next.

## Requirements

- Inventory the argument axes across the 53 skills. Result, after a two-lane
  adversarial review + operator taxonomy decisions (see `design.md`): **three**
  axes are genuine drift — **verbosity** (`length=`/`detail=`/density-`format=`
  → `depth=`), **primary artifact under action** (`source=`/`inputs=` →
  `input=`), and **redaction level** (stray `detail=` → `sensitivity=`).
  `sources=` (reference material to consult, 21 skills) is already consistent —
  reserved, not renamed. `privacy=` (distribution ceiling) and `evidence=`
  (supporting material) are distinct reserved names, not folded into any axis.
  `format=` structural shapes, `mode=`, `scope=`, `coverage=` keep per-skill
  value sets; only their names are reserved.
- Define the canonical names + ladders in a shared reference. Verbosity →
  `depth=brief|standard|deep`; primary artifact → `input=`; redaction →
  `sensitivity=minimal|restricted|standard`. Value checks are ladder **set
  membership** (skills list values default-first). Collision renames: se-research
  count `sources=N` → `min_sources=N`; se-technical-editor coverage
  `depth=full|focused` → `coverage=full|focused`.
- Migrate all covered skills; renames are consumer-visible and need changelog
  coverage + a manifest version bump per payload-changing child. Split into five
  ordered child tasks (see `implement.md` for ordering + rationale):
  `08-04-arg-vocab-reference`, `08-04-arg-vocab-verbosity`,
  `08-04-arg-vocab-format`, `08-04-arg-vocab-locator`,
  `08-04-arg-vocab-enforce`.
- Enforce covered-axis known-alias names + ladders in `validate_skill()`
  (`generate-skill-surfaces.py`), with negative fixtures in
  `tests/test_generate.py` and a live-corpus case in `tests/test_skills.py`.

## Acceptance Criteria

- [x] Three-axis canonical vocabulary + reserved-name registry documented in a
      shared reference shipped to skills.
- [x] `.venv/bin/python .github/scripts/generate-skill-surfaces.py --check`
      (and `make test`) rejects a **known** non-canonical covered-axis alias or
      off-ladder value (proven by a deliberate violation + negative fixtures).
      Note: `make generate --check` does NOT forward `--check`; the guarantee is
      regression-prevention under known aliases + ladders, not detection of an
      arbitrary future semantic alias.
- [x] All covered skills conform; `CHANGELOG.md` documents every rename citing
      A-006; `sources=` / `privacy=` / `evidence=` / `format=` shapes / `mode=` /
      `scope=` left intact.

## Notes

- Audit finding: A-006 (P2/M) — .trellis/audit/report-2026-07-25.md.
- Evidence: templates/skills/se-research/SKILL.md:37, se-monitor/SKILL.md:46, se-watchlist/SKILL.md:48, tests/test_skills.py:145.

## Cross-program coordination (2026-07-25 review)

- Land BEFORE `07-25-dispatch-pilot` / `07-25-dispatch-rollout` where practical: both
  waves edit the same 53 skill bodies (7 overlap directly), and dispatch sections should
  be written in the canonical argument vocabulary once instead of being renamed after.

---
title: Argument vocabulary enforcement
status: done
created: 2026-08-04
branch: audit/arg-vocab-enforce
---
# Argument vocabulary enforcement

## Goal

Make a **known** non-canonical covered-axis alias or an off-ladder value a hard
validation failure so the A-006 vocabulary cannot regress, and record the
consumer-visible renames in the changelog. Lands last; part of A-006.

Parent decision + rationale: `07-25-audit-skill-arg-vocabulary/design.md`.
Ordering: parent `implement.md`. Land after every migration child so
`make check` is green when the guard activates.

## Requirements

- Add covered-axis checks to `validate_skill()` in
  `.github/scripts/generate-skill-surfaces.py` (skills enumerated via
  `SKILL_NAMES`). Parse **every** inline-code `` `key=values` `` span per
  Arguments bullet (some bullets declare two args, e.g. `se-ask-me:46`). Reject:
  a verbosity axis under a known alias other than `depth=`; a primary-artifact
  axis under `source=`/`inputs=` (canonical `input=`); a redaction axis under
  the stray `detail=` (canonical `sensitivity=`); and `depth=`/`sensitivity=`
  values that are not a **subset** of their ladder (set membership, NOT
  declaration order). Bind names→concepts via the registry constant; do not
  attempt to infer concept from an arbitrary future name. Errors propagate
  through `validate_skills()` → `GenerationError`.
- Consume the single canonical-vocabulary constant from
  `08-04-arg-vocab-reference` (no duplicate list).
- Tests in two places: **negative validator fixtures** in
  `tests/test_generate.py` (`write_skill()`/`assert_validation_error()`) proving
  `validate_skill()` *rejects* malformed skills; a **live-corpus conformance**
  case beside `tests/test_skills.py:145` proving the real skills conform.
- Add a `CHANGELOG.md` entry (`## <semver> - <date>`) + manifest bump
  documenting the full A-006 rename set.

## Acceptance Criteria

- [x] `.venv/bin/python .github/scripts/generate-skill-surfaces.py --check`
      and `make test` reject a deliberately known-alias covered name or
      off-ladder value (proven; note `make generate --check` does not forward
      `--check`).
- [x] Negative fixtures in `tests/test_generate.py` + live-corpus case in
      `tests/test_skills.py` both present and green.
- [x] `make check` green with all covered skills conforming and the guard
      active; `CHANGELOG.md` documents every A-006 rename; version bump present.

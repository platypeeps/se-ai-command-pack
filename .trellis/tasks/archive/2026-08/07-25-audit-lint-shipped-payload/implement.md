# Implementation plan — Lint gate for shipped payload Python

## Ordered checklist

1. **Widen the lint gate — Makefile** (`lint` target)
   - ruff line: append `templates/skills/se-review-skills/scripts/skill_review.py`
     to the existing `ruff check install.py installer tests .github/scripts`.
   - mypy line: append the same path to `mypy installer install.py`.

2. **Widen the lint gate — `.github/workflows/tests.yml`** (CI `lint` lane)
   - Mirror both additions exactly so CI scope == Makefile scope.

3. **Fix the three defects in `skill_review.py`**
   - `:297` — **do not use `strict=True`** (breaks the 3.9 runtime floor and
     fails `test_analyzer_keeps_the_documented_python_39_runtime_floor`). Remove
     `zip`: iterate `for index, key_node in enumerate(shared.keys):` and read
     `value_node = shared.values[index]`. 3.9-safe, no `zip` so B905 cannot fire.
   - `:268` — rename the loop-local `value` to `assignment_node` at :268, :269,
     :271 (`assignment_node = _assignment(...)`; `isinstance(assignment_node, …)`;
     `for entry in assignment_node.elts`).
   - `:654`/:673 — change `if manifest_mapping:` to
     `if manifest_mapping and context_hint is not None:` so `context = context_hint`
     narrows to `PackageContext`.

4. **Release discipline**
   - `manifest.json` — `version`: `0.66.1` → `0.66.2`.
   - `CHANGELOG.md` — add a new top section `## 0.66.2 - 2026-08-04` describing
     the lint-gate widening and the three defect fixes.
   - Run `make generate` to regenerate version-bearing surfaces, then stage
     every file it rewrites — at minimum
     `templates/skills/_shared/references/skill-catalog.md`
     (`Bundled pack version: 0.66.1` → `0.66.2`). Without this,
     `make release-check` (`generate-skill-surfaces.py --check`) fails on drift.

## Validation commands

- `bash scripts/sd-ai-command-pack-toolchain.sh run-python -- -m ruff check templates/skills/se-review-skills/scripts/skill_review.py`
  → 0 errors (was B905 x1).
- `bash scripts/sd-ai-command-pack-toolchain.sh run-python -- -m mypy templates/skills/se-review-skills/scripts/skill_review.py`
  → 0 errors (was x2).
- `make lint` → clean over the widened scope.
- `make check` → green — must include
  `test_analyzer_keeps_the_documented_python_39_runtime_floor` passing (proves
  no `strict=True` crept in) plus test + lint + release-check.

## Review gates

- Before commit: `make check` green.
- sd-ship Stage 2 review (typed sd-check + configured GitHub/Copilot review).

## Rollback points

- Straight revert of the feature branch. No behavior change to the shipped
  script, no data/interface migration; the gate additions only widen
  enforcement.

## Out of scope

- The A-026 wrapper `scripts/se-ai-command-pack-skill-review.py` is not added to
  the gate (its keep/delete disposition is owned by task
  `07-25-audit-repo-tooling-ownership`). Follow-up pointer only.
- A dedicated Python 3.9 stdlib-only smoke lane for the shipped analyzer (the
  lint gate here targets py310, not the documented 3.9 floor; mypy cannot target
  3.9). Genuinely separate compatibility work — parked as a follow-up task, not
  expanded into this A-036 lint-bar task.

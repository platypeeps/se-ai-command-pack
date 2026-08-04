# Design — Coverage measurement and floor in gates (A-020)

## Summary

Add `coverage.py` measurement of repo-own Python to `make test` and the CI
`unittest` lane, failing below an agreed floor. The suite drives much of the
code through **subprocess** invocation (`install.py`, `.github/scripts/*`), so
the design must enable coverage's subprocess mode or the floor is meaningless.

## Decision 1 — tool: coverage.py (not pytest-cov)

The suite is stdlib `unittest discover`, not pytest. `coverage.py` wraps
`python -m unittest` directly with no test-runner migration. Add
`coverage==7.6.10` to `requirements-dev.txt`.

## Decision 2 — subprocess coverage is mandatory, not optional

Measured deltas (3.13 / macOS), source = `installer,install,.github/scripts`:

| file | in-process only | with subprocess capture |
|------|-----------------|-------------------------|
| install.py | 43% | 97% |
| .github/scripts/check-release-payload.py | 0% | 84% |
| .github/scripts/create-release-tag.py | 0% | 87% |
| .github/scripts/generate-skill-surfaces.py | 86% | 86% |
| installer/* | 66–97% | 78–100% |
| **TOTAL** | **66% / 68%** | **88%** |

Tests such as `tests/test_release_gate.py` and installer round-trip tests run
the code as a child `python` process. In-process-only numbers report tested
code as untested, which would force either an absurdly low floor or spurious
new tests. Enable subprocess capture:

- `.coveragerc` sets `[run] parallel = true` (per-process data files) and
  `source = installer,install,.github/scripts`.
- A tiny bootstrap importable on `PYTHONPATH` calls
  `coverage.process_startup()`, activated by the `COVERAGE_PROCESS_START`
  environment variable pointing at `.coveragerc`. This is coverage.py's
  documented subprocess mechanism and is portable across macOS/Linux and
  Python 3.10/3.13.
- After the run, `coverage combine` merges the per-process data, then
  `coverage report` / `--fail-under` evaluates the floor.

Bootstrap location: `tests/_coverage_subprocess/sitecustomize.py` (a directory
added to `PYTHONPATH` only for the coverage run). Using a dedicated directory
(not the repo root) keeps the auto-imported `sitecustomize` scoped to the
coverage invocation and out of normal `python` runs.

## Decision 3 — scope: repo-own code only

`source = installer,install,.github/scripts`. Vendored `scripts/` (command-pack
copies) and `.trellis/` are excluded by omission from `source`. No `omit`
needed — every in-scope file is genuinely exercised (lowest is
check-release-payload at 84%).

## Decision 4 — floor value: 80% (conservative introduction, documented ratchet)

Measured baseline is 88% on Python 3.13 / macOS — the only combo runnable
locally here. CI also runs **ubuntu 3.10** and **ubuntu 3.13**, and 3.10 is not
merely a platform variant: four tests are `@unittest.skipIf(tomllib is None,
…)` (tomllib is 3.11+), so 3.10 skips the codex-TOML rendering and codex-agent
install tests (`tests/test_generate.py:425,475,486`, `tests/test_install.py:371`).
Those skipped tests exercise real branches in `generate-skill-surfaces.py` and
the installer, so **3.10 coverage is expected to be measurably below the 88%
3.13 baseline**, by an amount that cannot be measured on this host.

`--fail-under` must hold for the *minimum* across the matrix. Rather than guess
a tight floor, introduce the gate at a conservative **80%** — comfortably below
the 88% 3.13 baseline and the (smaller) 3.10 total — so first CI is green with
margin, then **ratchet up**. The PR's own CI run prints the real per-combo
totals (all three lanes log `coverage report`); once the true 3.10 minimum is
observed, a follow-up raises the floor toward it. This is the standard
coverage-ratchet introduction: start at a floor you know passes, tighten with
evidence. `[report] precision` and the ratchet path are documented in
CONTRIBUTING.

Threshold semantics (corrected): coverage.py 7.6.10 does **not** truncate — it
`round(total, precision)` and fails when that is `< fail_under`
(`coverage.results.should_fail_under`). Set `[report] precision = 1`
explicitly and document that a `--fail-under=80` gate trips below ~79.95%
(rounding), not below exactly 80.000%.

## Decision 5 — wiring points

- **Makefile `test` target**: `coverage erase`, then coverage `run`, then
  `combine`, then `report --fail-under=80`. The goal (prd.md:5) requires
  **`make test` itself to fail below the floor**, not only CI, so the local
  target enforces the same `--fail-under` (it also prints the report → AC2).
  The leading `erase` prevents stale parallel `.coverage.*` data (from a prior
  aborted run) contaminating the combine. Keep `make check` → `test lint
  release-check` intact.
- **CI `unittest` lane** (`.github/workflows/tests.yml`, all 3 matrix combos):
  install dev deps (now including coverage), run the same
  erase→run→combine→`report --fail-under=80` sequence. The lane's failure
  already propagates to the aggregate job via its `needs`.

## Decision 6 — AC1 demonstration (in CI, then reverted)

AC1 requires proving **CI** fails below the floor once — not merely that
coverage.py returns a non-zero exit locally. After the gate is wired and green,
push one throwaway commit on the PR branch that forces the lane red (e.g.
temporarily set `--fail-under` above the baseline, or add a wholly-uncovered
function), confirm the CI `unittest` lane goes **red** and the failure
propagates to the aggregate job, capture the failing run URL as evidence, then
**revert** that commit so the PR ends green at the 80% floor. Record the run
URL + revert SHA in the journal. A local `coverage report --fail-under=95`
non-zero exit is kept as a secondary check, not the AC1 evidence.

## Non-goals

- No migration to pytest.
- No new coverage of `scripts/` (vendored) or `.trellis/`.
- No branch coverage (`[run] branch = true`) in v1 — statement coverage first;
  branch coverage can raise rigor later without reworking the wiring.

## Risks / verification boundary

- **Cross-matrix coverage variance** cannot be measured locally (only
  3.13/macOS is available here), and 3.10 provably skips tomllib-gated tests.
  Mitigated by introducing the floor at a conservative 80% with a documented
  ratchet; the CI run on the PR is the authoritative per-combo measurement. If
  any matrix combo unexpectedly reports below 80%, lower the floor to the
  observed minimum minus margin and document it before merge.
- Subprocess `PYTHONPATH` injection must not perturb test imports — verified
  locally (suite still exits 0 under the coverage wrapper).

# Coverage measurement and floor in gates

## Goal

`make test` and CI measure coverage for repo-own Python and fail below an agreed floor, so untested branches in the installer and build scripts can no longer merge green silently.

## Requirements

- Add a coverage tool to requirements-dev.txt and wire it into the test target and the CI unittest lane.
- Scope the floor to repo-own code: installer/, install.py, .github/scripts (exclude vendored scripts/ and .trellis/).
- Pick the initial floor from measured current coverage (planning decision); document how to raise it.

## Acceptance Criteria

- [x] CI fails when coverage drops below the floor (demonstrated once with an artificial drop).
- [x] `make test` prints a coverage report locally.
- [x] Floor value and scope documented (CONTRIBUTING or operator guide).

## Notes

- Audit finding: A-020 (P2/M) — .trellis/audit/report-2026-07-25.md.
- Evidence: Makefile:24, .github/workflows/tests.yml:32, requirements-dev.txt:3.

## Acceptance evidence

- AC1 (CI red demo): PR #124 temporary commit `8efae33` raised the CI floor to
  `--fail-under=99`; run
  https://github.com/platypeeps/se-ai-command-pack/actions/runs/30917091981
  failed the `unittest` step (`Coverage failure: total of 87.6 is less than
  fail-under=99.0`) and the `ci-result` aggregate job (proving `needs`
  propagation). Reverted in `677d330`, restoring the 80% floor.
- Real per-lane totals on green head `bdbf14c`: ubuntu-3.10 87.6%,
  ubuntu-3.13 87.7%, macos-3.13 87.7% — matrix minimum 87.6%, ~7.6% above the
  80% floor (planning C-2 resolved empirically; the 3.10 `tomllib` skips move
  the total by only 0.1%).
- AC2: `make test` -> TOTAL 87.7%, exit 0.
- AC3: `CONTRIBUTING.md` "Test coverage floor" section.

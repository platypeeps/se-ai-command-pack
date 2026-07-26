# Coverage measurement and floor in gates

## Goal

`make test` and CI measure coverage for repo-own Python and fail below an agreed floor, so untested branches in the installer and build scripts can no longer merge green silently.

## Requirements

- Add a coverage tool to requirements-dev.txt and wire it into the test target and the CI unittest lane.
- Scope the floor to repo-own code: installer/, install.py, .github/scripts (exclude vendored scripts/ and .trellis/).
- Pick the initial floor from measured current coverage (planning decision); document how to raise it.

## Acceptance Criteria

- [ ] CI fails when coverage drops below the floor (demonstrated once with an artificial drop).
- [ ] `make test` prints a coverage report locally.
- [ ] Floor value and scope documented (CONTRIBUTING or operator guide).

## Notes

- Audit finding: A-020 (P2/M) — .trellis/audit/report-2026-07-25.md.
- Evidence: Makefile:24, .github/workflows/tests.yml:32, requirements-dev.txt:3.

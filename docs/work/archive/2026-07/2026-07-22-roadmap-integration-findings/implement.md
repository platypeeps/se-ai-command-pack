# Resolve skill roadmap integration findings Implementation Plan

## Implementation Steps

1. [x] Start from current `main` and reread FIR-01/FIR-02 plus the archived
   personal-worklog boundary before editing product surfaces.
2. [x] Update the canonical `se-weekly-review` template with explicit/private-input
   timezone precedence and ask-or-stop unresolved behavior; preserve DST-safe
   reporting-window semantics.
3. [x] Add focused regression assertions that reject named/default locale fallbacks
   and pin the resolution contract.
4. [x] Add `se-review-skills` to the operator guide with its review-only boundary
   and distinctions from `se-help`, `sd-audit-repo`, and `sd-review-local`.
5. [x] Extend existing tests to compare registered public skills with operator-guide
   coverage.
6. [x] Bump the manifest release version, add the matching dated changelog entry,
   and run canonical generation. Do not hand-edit generated rows or platform
   copies.
7. [x] Review the diff for accidental `se-worklog`, private automation, path,
   schedule, destination, or write-back scope expansion.
8. [x] Complete the focused and full validation gates.
9. Ship the task normally and archive it only through the merge lifecycle.
10. Return to `se-skill-roadmap`, rerun its final integration audit, then close
   the parent only if FIR-01 and FIR-02 are demonstrably resolved.

## Validation Results - 2026-07-22

- Independent Trellis implementation and check passes completed.
- `make generate` was idempotent across two consecutive runs.
- Focused skill/documentation tests passed: 221 tests.
- `make check` passed: 458 tests, Ruff, mypy, generated-surface parity, and
  release-payload validation.
- Release `0.50.0` matches the dated changelog; 125 logical payloads remain
  identical across 375 Agents, Claude Code, and Codex manifest rows.
- The all-platform installer dry run left a fresh temporary root unchanged.
- `git diff --check` passed, and the diff contains no `se-worklog` or private
  automation implementation.

## Validation Plan

- Focused unittest module/methods covering skill prose and operator docs.
- `make generate`
- Repeat `make generate` and require no new diff.
- `make check`
- `git diff --check`
- Manifest/changelog/version and three-platform byte-parity inspection.
- `.venv/bin/python install.py --root <fresh-temp-root> --all --dry-run`, then
  verify the root is unchanged.

## Documentation And Release

- Add a `2026-07-22` changelog entry for the portable timezone fix and complete
  operator coverage.
- Use the next package version after `0.49.0`; generation owns manifest rows and
  hashes.
- The operator-guide edit is product documentation, not a second skill catalog
  source of truth.

## Delegation And Automation

- Use the required Trellis implementation and check agents with fresh task
  context. Give deterministic source/test edits to an implementation agent and
  reserve cross-surface semantic verification for the check agent.
- Reuse existing generation, release, test, and installer scripts. Do not add a
  one-off permanent script for two bounded semantic assertions.

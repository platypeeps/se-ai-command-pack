# Resolve skill roadmap integration findings Implementation Plan

## Implementation Steps

1. Start from current `main` and reread FIR-01/FIR-02 plus the archived
   personal-worklog boundary before editing product surfaces.
2. Update the canonical `se-weekly-review` template with explicit/private-input
   timezone precedence and ask-or-stop unresolved behavior; preserve DST-safe
   reporting-window semantics.
3. Add focused regression assertions that reject named/default locale fallbacks
   and pin the resolution contract.
4. Add `se-review-skills` to the operator guide with its review-only boundary
   and distinctions from `se-help`, `sd-audit-repo`, and `sd-review-local`.
5. Extend existing tests to compare registered public skills with operator-guide
   coverage.
6. Bump the manifest release version, add the matching dated changelog entry,
   and run canonical generation. Do not hand-edit generated rows or platform
   copies.
7. Review the diff for accidental `se-worklog`, private automation, path,
   schedule, destination, or write-back scope expansion.
8. Complete the focused and full validation gates, ship the task normally, and
   archive it only after merge.
9. Return to `se-skill-roadmap`, rerun its final integration audit, then close
   the parent only if FIR-01 and FIR-02 are demonstrably resolved.

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

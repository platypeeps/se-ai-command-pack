# Test hermeticity and update e2e coverage

## Goal

`make test` passes on any contributor machine regardless of global git configuration, and the `install.py update` lifecycle — the one command that mutates the user's checkout — has a real end-to-end test.

## Requirements

- Scrub git environment in every subprocess-git test helper: GIT_CONFIG_GLOBAL=/dev/null and GIT_CONFIG_SYSTEM=/dev/null (or HOME pointed at a temp dir) — covers tests/test_release_gate.py:17 and the raw `git init` sites in tests/test_skill_review.py:904, :1238. [A-021]
- Add one update e2e in the ReleaseTagTest style: temp clone with a local bare origin one commit ahead → run install.py update → assert the pull happened and installed files refreshed. [A-022]
- Cover a second hermeticity axis the audit findings do not name: a test that reads an untracked or gitignored file. Global git configuration is state a runner *has* and a contributor's machine differs on; this is the mirror case — state a working checkout has and a runner does not. It fails in the more dangerous direction, because the local run is the green one. Demonstrated below, so this requirement is drawn from an incident rather than from speculation.

## Acceptance Criteria

- [ ] Suite passes with a hostile global config (e.g. commit.gpgsign=true, core.hooksPath set) simulated in CI or a dedicated test.
- [ ] The update e2e runs in CI and fails when the pull/refresh handshake breaks.
- [ ] No test depends on a path that `git ls-files` does not report, unless it explicitly tolerates that path's absence; a check that enumerates from the tracked tree is preferred over one that reads a machine-local artifact.

## Evidence: the 2026-08-10 incident (task 07-25-audit-repo-tooling-ownership, PR #206)

A new `tests/test_repo_tooling_ownership.py` read `.trellis/.template-hashes.json` unconditionally. That file is gitignored at `.gitignore:94`, so a working checkout has one and a runner never does. `make check` was green locally and every CI lane failed at `564d252` with `FAILED (errors=8, skipped=1)`.

Three properties of that failure are worth designing against:

1. **The local gate could not catch it.** `make check` ran against a file the runner cannot see, so the pre-push signal was green for exactly the reason it should have been red. Any mitigation that lives only in `make check` reproduces the same blind spot.
2. **Crashing was the lesser failure mode.** Making the read merely optional would have been worse: that file is the sole source for 32 paths, so an absent-file fallback silently reclassified vendored `.trellis/scripts/**` as repo-own on CI alone — green, and wrong. A hermeticity fix that degrades a verdict instead of failing is a regression wearing a fix's clothing.
3. **The repository already documented the property.** `.trellis/spec/backend/quality-guidelines.md:798` branches on `if [ -f .trellis/.template-hashes.json ]` and `:2366` calls it "the machine-local Trellis hash file". The test contradicted a written contract, which suggests the gap is discoverability, not knowledge.

The fix landed with the task (merged in `9d8f37f`): the coverage guard now enumerates from `git ls-files` so it runs everywhere, and the one assertion that genuinely needs the machine-local receipt skips explicitly when it is absent rather than passing vacuously. That shape — enumerate from the tracked tree, skip loudly when you cannot — is a candidate convention for this task to generalize.

A cheap detection idea for design to weigh: run the suite once with untracked and ignored files stashed away, which is close to what a runner sees. Cost and false-positive rate are unmeasured; treat it as a starting point, not a settled decision.

## Notes

- Audit findings: A-021 (P3/S), A-022 (P3/M) — .trellis/audit/report-2026-07-25.md.
- Evidence: tests/test_release_gate.py:17, :51; tests/test_skill_review.py:904; tests/test_management.py:108; installer/management.py:146.
- Planning depth: **Complex — needs `design.md` and `implement.md` before `task.py start`.** A real end-to-end test for `install.py update` means designing a hermetic harness for the one command that mutates a user's checkout: fixture checkout, isolation from global git configuration, and rollback assertions. That harness is a design decision, not an implementation detail.

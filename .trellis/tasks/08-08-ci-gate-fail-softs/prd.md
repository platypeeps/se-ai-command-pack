# CI aggregate and gate fail-softs let real failures merge green

## Goal

Close the fail-soft paths in this repository's own quality gates: the CI
aggregate that treats skipped lanes as green, the release-tag job the aggregate
never sees, the merge policy that accepts stale branches, the shell scripts no
lane syntax-checks, and the deterministic local gate that runs neither tests
nor lint. Each item may resolve as a change or as a recorded "accepted, here is
why" — what must end is the unexamined state.

## Problem

Five independent fail-softs, all verified 2026-08-08:

1. **`ci-result` counts skipped lanes as success.** The aggregate at
   `.github/workflows/tests.yml:100-121` fails only on results
   `not in ("success", "skipped")`. Today no required lane can skip, so this is
   latent — but the first future `if:`-gated lane passes the required check
   silently when its condition turns it off.
2. **`auto-tag-release` is invisible to the aggregate.** `ci-result` needs only
   `[unittest, lint, release-payload-gate]` (`tests.yml:101`). A failed release
   tag on a `main` push never reaches the one required context.
3. **Branch protection does not require up-to-date branches.** The GitHub API
   reports `strict: false` and `required_approving_review_count: 0` for `main`.
   A green PR check therefore does not guarantee the post-merge tree is green;
   the push-to-main run catches breakage only after it has landed.
4. **4,620 lines of shell are never syntax-checked.** No workflow, Makefile
   target, or test invokes `shellcheck` or even `bash -n` on the seven
   `scripts/*.sh` files. They are vendored, but they execute inside this
   repository's own local gates (`sd-ai-command-pack-full-check.sh`,
   `-housekeeping.sh`), so a syntax error ships undetected until a gate run
   trips over it.
5. **`sd-check` cannot fail on a broken test or type error.**
   `scripts/sd-ai-command-pack-check.py:29` reads repo config from
   a `check.json` file under `.sd-ai-command-pack/`; no such file exists (the
   directory holds only `installed-targets.txt`, `manifest.json`,
   `provenance.json`). With no config, the script runs only its builtins —
   whitespace passes plus pack gates. Unit tests, ruff, mypy, and the release
   payload gate are in none of them, so the repository's deterministic gate
   passes on a tree where `make check` fails.

## Requirements

- For each of the five items, record a disposition: fix, or accept with
  reasoning. The required outcomes (mechanism is design's choice, not fixed
  here): item 1 — a skipped required lane can no longer pass the required
  check silently; item 2 — a failed release tag becomes visible in the gated
  result, or its invisibility is accepted in writing; item 3 — a
  branch-protection settings decision; item 4 — shell scripts that execute in
  this repo's gates get at least a syntax check somewhere a gate runs, or
  deep-checking vendored shell is declined explicitly; item 5 — either
  `sd-check` gains the repo's test/lint checks through its supported
  configuration mechanism, or its pack-gates-only scope is documented where a
  reader of its output will find it.
- Do not fold in the review-preflight-in-CI decision. That is
  `08-07-ci-no-preflight-lane`'s whole subject; this task must not preempt or
  duplicate it.
- Any CI change stays inside the existing single-workflow structure of
  `tests.yml`; no new workflow files.

## Acceptance Criteria

- [x] Each of the five fail-softs has a written disposition (fix or accept)
      with reasoning, citing the current behaviour by file and line where a
      positive occurrence exists; dated GitHub API evidence for
      repository-external state (item 3), and bounded repository-search
      evidence for absences (item 4), satisfy the citation requirement.
      SATISFIED 2026-08-09: all five dispositions recorded in `design.md`
      (items 1/2/4/5 fix, item 3 accept with reasoning and revisit triggers);
      durable gate guidance added to
      `.trellis/spec/backend/quality-guidelines.md`.
- [x] If item 1 is fixed: the new behaviour is demonstrated dynamically, not
      by reading YAML — either a controlled workflow run with a lane forced
      to skip, or the aggregation logic extracted into a form exercised by a
      test with a synthetic `skipped` result. Static inspection of the
      aggregate does not satisfy this criterion.
      SATISFIED 2026-08-09 via the extraction route: aggregation moved to
      `.github/scripts/aggregate-ci-result.py`;
      `tests/test_aggregate_ci_result.py::test_required_lane_skipped_fails`
      feeds a synthetic `unittest: skipped` payload and asserts nonzero exit.
- [x] If item 5 is fixed: `sd-check` fails on a tree with a deliberately broken
      unit test; if accepted instead, the pack-gates-only scope of `sd-check`
      is stated in repository guidance a reader can find from the check output.
      SATISFIED 2026-08-09: with a deliberately broken assertion in
      `tests/test_aggregate_ci_result.py`, `sd-check` exited 1 with
      `repo.test: failed`; after revert the run returned to overall passed
      with `stateGuard: passed`.
- [x] `08-07-ci-no-preflight-lane` remains the sole owner of the preflight
      lane decision — this task's changes neither add nor remove a preflight
      invocation in CI.
      SATISFIED 2026-08-09: the diff touches no preflight invocation;
      `review-preflight` had not landed at implementation time, so the
      aggregator ships the design-time floor lane sets and the reconciliation
      note in `implement.md` step 1 remains with that task.

## Out of scope

- Whether CI should run the vendored review preflight
  (`08-07-ci-no-preflight-lane`).
- Coverage scope for vendored `scripts/` (untested by design; see
  `.coveragerc` comment) — a separate decision from syntax-checking.
- The `unavailable`-vs-`failed` exit-code semantics inside vendored
  `sd-ai-command-pack-check.py` — upstream behaviour, routable via
  `08-07-vendored-artifact-upstream-route`.

## Notes

- Sourced from the 2026-08-08 deep review (CI/test lane). Items verified
  directly: `tests.yml:100-121` aggregate logic and `needs` list, absence of
  `check.json` in `.sd-ai-command-pack/`, `CONFIG_PATH` at
  `sd-ai-command-pack-check.py:29`, absence of any `shellcheck`/`bash -n`
  invocation in `tests.yml` and `Makefile`. Branch-protection values came from
  the GitHub API during the review.
- Originally filed lightweight/PRD-only. Superseded 2026-08-08 by the
  needs-design planning run: the dispositions interact (items 1/2 share the
  aggregator, item 5 is constrained by sd-check's state guard), so full
  `design.md` + `implement.md` were added. Scope still fits one PR; split
  only if execution proves otherwise.

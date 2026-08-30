# CI aggregate and gate fail-softs — Design

## Overview

The PRD names five verified fail-soft paths in this repository's own quality
gates and requires a recorded disposition — fix or accept-with-reasoning — for
each. This design records all five dispositions, and for the four "fix" items
specifies the mechanism. Everything stays inside the existing single-workflow
structure of `.github/workflows/tests.yml`; no new workflow files, and no
change to the review-preflight-in-CI question, which
`08-07-ci-no-preflight-lane` owns exclusively.

Dispositions at a glance:

| # | Fail-soft | Disposition |
|---|-----------|-------------|
| 1 | `ci-result` counts skipped lanes as success | **Fix** — extract aggregation into a tested script with per-lane skip policy |
| 2 | `auto-tag-release` invisible to the aggregate | **Fix** — add it to `ci-result`'s `needs` as a conditional lane |
| 3 | Branch protection `strict: false`, 0 approvals | **Accept** with recorded reasoning; no settings mutation |
| 4 | 4,620 lines of shell never syntax-checked | **Fix** — `bash -n` lane in `make check` and the CI `lint` job |
| 5 | `sd-check` runs neither tests nor lint | **Fix** — repo-own `.sd-ai-command-pack/check.json` registering guard-safe test/lint/shell-syntax targets |

## Proposal

### Item 1 — fix: extracted, tested aggregation with per-lane skip policy

Current behaviour: `tests.yml` `ci-result` step runs an inline Python heredoc
that fails only on results `not in ("success", "skipped")`
(`.github/workflows/tests.yml:100-121`). A future `if:`-gated required lane
that skips would pass the one required context silently.

Change: move the aggregation into a repo-own script,
`.github/scripts/aggregate-ci-result.py`, invoked from the same `ci-result`
step with the same `NEEDS_JSON` environment input. The `ci-result` job
currently has **no checkout step** (its only step is the inline heredoc), so
wiring the script requires adding `actions/checkout@v7` with
`persist-credentials: false` to that job first — without it the fresh job
workspace has no repository and the aggregate would fail before evaluating
any lane. Policy:

- Two lane classes, declared in the script:
  - `REQUIRED_LANES = {"unittest", "lint", "release-payload-gate"}` — result
    must be exactly `success`; `skipped` is a failure.
  - `CONDITIONAL_LANES = {"auto-tag-release"}` — `success` or `skipped`
    accepted (the job legitimately skips on every `pull_request` event and on
    non-`main` pushes); any other result is a failure.
- Fail closed on surprises: a lane present in `NEEDS_JSON` but not declared
  in either set, a declared lane missing from `NEEDS_JSON`, or an unparseable
  `NEEDS_JSON` all exit nonzero with a diagnostic naming the lane.
- Exit 0 only when every declared lane is accounted for and acceptable.

Cross-task reconciliation with `08-07-ci-no-preflight-lane`: if its
`review-preflight` job has landed by the time this is implemented, that lane
is **required** — it runs unconditionally, so it joins `REQUIRED_LANES`
(never the conditional set), every synthetic test payload includes it, and
`review-preflight: skipped` must exit nonzero. The lane sets above are the
floor at design time, not a frozen ceiling.

This satisfies the PRD's dynamic-proof acceptance criterion via the
"aggregation logic extracted into a form exercised by a test" route: a new
unit test module feeds the script synthetic `needs` payloads — including a
required lane with result `skipped` — and asserts the nonzero exit. Static
YAML reading proves nothing here; the test executes the exact logic CI runs.

### Item 2 — fix: `auto-tag-release` joins the aggregate as a conditional lane

Current behaviour: `ci-result` needs only
`[unittest, lint, release-payload-gate]` (`tests.yml:101`); a failed release
tag on a `main` push never reaches the one required context.

Change: add `auto-tag-release` to `ci-result`'s `needs` list. `ci-result`
already runs under `if: always()`, so a skipped or failed tag job cannot
deadlock the aggregate. Lane policy comes from item 1: on `pull_request`
events the tag job skips and the conditional class accepts that; on a `main`
push a tag failure now turns `ci-result` red in the push run — visible in the
Actions UI and in the commit status — instead of vanishing. This does not
retroactively gate the already-merged PR (nothing can), but the failure is no
longer invisible in the gated result, which is what the PRD requires.

### Item 3 — accept: branch protection stays `strict: false`, 0 approvals

Current behaviour (GitHub API, verified 2026-08-08): `main` requires the
`ci-result` context with `strict: false`,
`required_approving_review_count: 0`, `enforce_admins: true`.

Disposition: **accepted, no change**, for these reasons:

- Single-maintainer repository; the merge path is the sd-housekeeping gate,
  which merges immediately after a settled-green watch on the exact head, so
  the stale-branch window `strict: true` closes is minutes wide in practice.
- The push-to-main CI run (bare `push: branches: [main]` trigger,
  `tests.yml:4-5`) validates the actual post-merge tree on every merge; with
  item 2 fixed, that run's aggregate also covers the release tag, so a
  stale-merge breakage surfaces on the very next run.
- `strict: true` would force a branch update (and full re-run) on every PR
  merged after any other push — including dependabot PRs — for a protection
  whose failure mode has not been observed here.
- Zero required approvals matches reality: there is no second human reviewer;
  review depth comes from the sd-review loop and optional Copilot, neither of
  which GitHub counts as an approving review.

Accepted residual risk, stated honestly: consumers are **not** insulated from
a broken `main`. `install.py update` fast-forwards the recorded source
checkout (`installer/management.py:216,261` — `git pull --ff-only`, no tag
pinning), so a consumer whose checkout tracks `main` can pull an untagged
broken commit during the window between a stale-green merge and its fix. The
acceptance rests on the window being small and alarmed (previous two
bullets), not on distribution isolating consumers.

Changing branch-protection settings is an operator-owned, security-adjacent
mutation outside this run's authority in any case. Revisit triggers, recorded
here: a second maintainer joins, or one real stale-merge breakage reaches
`main`; the starting point then is `strict: true` plus
`required_approving_review_count: 1`.

### Item 4 — fix: `bash -n` syntax lane for vendored shell that local gates execute

Current behaviour: no workflow, Makefile target, or test invokes `shellcheck`
or `bash -n` on the seven `scripts/*.sh` files (4,620 lines total). They are
vendored, but `sd-ai-command-pack-full-check.sh`, `-housekeeping.sh`, and
`-toolchain.sh` execute inside this repository's own local gates, so a syntax
error ships undetected until a gate run trips over it.

Change, scoped deliberately to syntax only:

- New Makefile target `shell-syntax`: `bash -n` over `scripts/*.sh`,
  enumerated by glob at run time (no hard-coded file list to drift), failing
  on the first error. Add it to the `check` aggregate target.
- One new step in the existing CI `lint` job running the same loop. Adding a
  step to an existing job keeps the single-workflow constraint; `bash -n`
  needs no extra tooling on `ubuntu-latest`.
- `shellcheck` (deep linting) is explicitly declined for vendored shell:
  these files are upstream-owned payload, and a style/robustness lint would
  generate findings this repository must not fix locally (fork class
  documented in `08-07-review-py-local-fork`; routing owned by
  `08-07-vendored-artifact-upstream-route`). Syntax validity is the only
  property this repo's gates depend on.

### Item 5 — fix: register guard-safe test, lint, and shell-syntax gates in `check.json`

Current behaviour: `scripts/sd-ai-command-pack-check.py:29` reads repo config
from `.sd-ai-command-pack/check.json`; no such file exists, so `sd-check`
runs only its seven builtins — whitespace passes plus pack gates — and passes
on a tree where `make check` fails.

**Constraint that shapes this design:** `sd-check` runs a state guard around
every configured check (`state_snapshot`, `sd-ai-command-pack-check.py:311-343`;
enforcement at `:838-870`): any change to a `GUARDED_PATHS` entry
(`:103-113` — including `.coverage`, `.ruff_cache`, `.pytest_cache`) or to
tracked files fails the run. Therefore the existing `make test` (writes and
combines `.coverage` data) and `make lint` (ruff populates `.ruff_cache`)
**cannot be registered as-is** — the guard would fail them even on a green
tree. Registered commands must be guard-safe variants.

Change: two new guard-safe Makefile targets plus the registration file.

- `gate-test`: `$(RUN_PYTHON) -m unittest discover -s tests` — the same
  suite CI runs, without the coverage harness. No `.coverage` writes; Python
  bytecode caches (`__pycache__/`) are untracked and outside `GUARDED_PATHS`,
  so the guard is indifferent to them. The 80% coverage floor deliberately
  stays where it lives today (`make test`, CI `unittest` lane); `sd-check`'s
  job is "do the tests pass", which is exactly the PRD's item 5 acceptance
  criterion.
- `gate-lint`: `$(RUN_PYTHON) -m ruff check --no-cache <same path list as
  lint>` followed by the same mypy invocation as `lint`. `--no-cache` keeps
  `.ruff_cache` untouched; mypy's `.mypy_cache` is untracked and not in
  `GUARDED_PATHS`.
- `.sd-ai-command-pack/check.json` — a repo-authored configuration file (not
  pack payload: absent from `provenance.json` and `installed-targets.txt`,
  and `check.py` is designed to read it), using the supported schema
  (`load_configuration`, `sd-ai-command-pack-check.py:580-618`; every entry
  field is mandatory, including `cwd` — `ENTRY_KEYS` membership at `:65-66`,
  missing-field enforcement at `:533-535`):

```json
{
  "schemaVersion": 1,
  "prerequisites": [],
  "checks": [
    { "id": "repo.test", "argv": ["make", "gate-test"], "cwd": ".", "timeoutSeconds": 900 },
    { "id": "repo.lint", "argv": ["make", "gate-lint"], "cwd": ".", "timeoutSeconds": 600 },
    { "id": "repo.shellsyntax", "argv": ["make", "shell-syntax"], "cwd": ".", "timeoutSeconds": 60 }
  ]
}
```

- `make` passes `check.py`'s command policy (not in the forbidden set, not a
  shell/code-string/git invocation — `:476-519`), and the Makefile already
  resolves the correct interpreter (`.venv` first), so the entries reuse the
  repository's canonical command definitions rather than duplicating paths.
- Scope of registration: the developer-loop gates (tests, lint, shell
  syntax). `release-check` is deliberately not registered — release-payload
  gating is a publish-time concern owned by CI's `release-payload-gate` lane
  (`tests.yml:64`) and locally by `make release-check` inside the
  `make check` superset, not a per-review-loop invariant. This is a scoping
  decision, not an oversight.
- Cost: `sd-check` grows from ~5 s to roughly the uninstrumented test suite
  plus lint wall time. That is the point of the gate — the current 5 s pass
  is the fail-soft being closed. `timeoutSeconds` values leave headroom over
  observed times.

## Boundaries And Non-Goals

- **Not touched:** review-preflight-in-CI (owned by
  `08-07-ci-no-preflight-lane`; this change adds no preflight invocation and
  removes none), coverage scope for vendored `scripts/` (`.coveragerc`
  untouched), the `unavailable`-vs-`failed` semantics inside vendored
  `check.py` (upstream, routable via `08-07-vendored-artifact-upstream-route`),
  and branch-protection settings (item 3 accepted).
- **No new workflow files**; `tests.yml` remains the single workflow.
- **No local edits to any provenance-tracked vendored file.** New files
  (`aggregate-ci-result.py`, `check.json`, the test module) are repo-own;
  edited files (`tests.yml`, `Makefile`) are repo-own.
- Vendored shell gets syntax checking only; deep lint declined (item 4).

## Affected Files

| Path | Change | Ownership |
|------|--------|-----------|
| `.github/scripts/aggregate-ci-result.py` | new | repo-own |
| `tests/test_aggregate_ci_result.py` | new | repo-own |
| `.github/workflows/tests.yml` | edit `ci-result` step + `needs`; add lint-job step | repo-own |
| `Makefile` | new `shell-syntax`, `gate-test`, `gate-lint` targets; extend `check` | repo-own |
| `.sd-ai-command-pack/check.json` | new | repo-own config read by vendored `check.py` |
| `.trellis/tasks/08-08-ci-gate-fail-softs/*` | planning artifacts | task |

The new aggregator is ruff-linted in CI (the lint lane's ruff invocation
already covers `.github/scripts`); mypy's scope
(`installer install.py skill_review.py`) is unchanged and does not include
it. It is coverage-measured (`.coveragerc` `source` lists `.github/scripts`)
and its test module lands under `tests/`, discovered by
`unittest discover -s tests` like any repo-own test.

## Data And Command Contracts

- `aggregate-ci-result.py` contract: reads `NEEDS_JSON` env var (the
  workflow's `toJSON(needs)`); prints per-lane results; exit 0 iff all
  declared lanes acceptable; exit 1 with named lanes otherwise; exit 2 on
  malformed input or lane-set mismatch. Lane sets live at the top of the
  script as the single source of policy.
- `check.json` contract: schema version 1 per `load_configuration`; every
  entry carries all four mandatory fields (`id`, `argv`, `cwd`,
  `timeoutSeconds`); argv-only invocation with `cwd: "."`. `sd-check`'s JSON
  report gains three rows with `kind: "check"` (the emitter's kind for
  configured checks, `sd-ai-command-pack-check.py:1022`).
- `make gate-test` / `gate-lint` / `shell-syntax` contract: exit nonzero on
  any failure; write nothing under `GUARDED_PATHS` and nothing tracked —
  guard-safe by construction.

## Risks And Edge Cases

- **Lane rename drift:** renaming a job in `tests.yml` without updating the
  script's lane sets fails closed (exit 2, lane-set mismatch) rather than
  silently passing — by design.
- **`ci-result` waits on `auto-tag-release`:** on `main` pushes the aggregate
  now completes after the tag job. The tag job is seconds long; no material
  latency. On PRs it skips instantly.
- **Gate/`check` drift:** `gate-test`/`gate-lint` intentionally restate the
  test and lint commands minus their cache/coverage side effects. If `lint`'s
  path list changes without `gate-lint` following, the two drift. Mitigation:
  define the shared path list once as a Makefile variable both targets use.
- **`sd-check` runtime:** review loops get slower by the uninstrumented
  suite + lint wall time. If that proves unacceptable, the recorded fallback
  is to drop `repo.test` from `check.json` and document the pack-gates-only
  scope (the PRD's accept route for item 5) — a one-line revert, not a
  redesign.
- **`bash -n` false confidence:** syntax checking catches parse errors only,
  not runtime breakage; the design says so and claims nothing more (item 4
  scope statement).
- **Guard interaction of future entries:** anything later added to
  `check.json` must be guard-safe; the state-guard constraint paragraph in
  item 5 is the durable warning.

## Validation

- `python -m unittest tests.test_aggregate_ci_result` — synthetic `needs`
  payloads: all-success passes; required-lane `skipped` fails (the PRD's
  named dynamic proof); conditional-lane `skipped` passes; any `failure` /
  `cancelled` fails; undeclared or missing lane fails.
- `make shell-syntax` — passes on the current tree; fails when a deliberate
  syntax error is introduced into a scratch copy (demonstrated, not
  asserted, per PRD acceptance criteria).
- `sd-check` (via `bash scripts/sd-ai-command-pack-toolchain.sh run-python --
  scripts/sd-ai-command-pack-check.py`) — report contains `repo.test`,
  `repo.lint`, `repo.shellsyntax` rows, `stateGuard.status: passed`, overall
  pass on a clean tree. The guard-passing run is itself evidence the
  registered commands are guard-safe.
- Negative proof (PRD item 5 criterion): break one repo-own unit test with a
  scratch edit, run `sd-check`, confirm `repo.test` fails and the aggregate
  is nonzero; revert; re-run to green.
- `make check` — full aggregate stays green on the final tree.
- CI on the PR — all lanes green including the reworked `ci-result`, with
  `auto-tag-release` showing `skipped` on the PR run without failing the
  aggregate.

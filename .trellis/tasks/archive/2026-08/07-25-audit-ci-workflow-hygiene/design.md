# Design — CI workflow hygiene and release-script error contract

Scope: `.github/workflows/tests.yml` and `.github/scripts/create-release-tag.py`
plus one new test surface. Four audit findings: A-038, A-039, A-037, A-014. No
product code, generator, installer, or manifest changes; this is CI + release
tooling hardening only, so it carries no manifest version bump (nothing under a
shipped payload path changes).

## A-038 — pip caching on the three setup-python steps

Add `cache: pip` with `cache-dependency-path: requirements-dev.txt` to each of
the three `actions/setup-python@v6` steps: `unittest` (line ~28), `lint`
(~47), `release-payload-gate` (~62). `auto-tag-release` uses the runner's
system `python3` with no `setup-python` step and installs nothing, so it gets
no cache key. The dependency path is the single `requirements-dev.txt` every
lane installs, so all three lanes share one restore key.

Tradeoff: caching keys on the lockfile-equivalent (`requirements-dev.txt`).
The repo pins dev deps there, so a content change invalidates the cache
correctly. No separate cache action is added — `setup-python`'s built-in cache
is sufficient and needs no `actions/cache` permissions.

## A-039 — concurrency with PR-only cancellation

Add a top-level `concurrency:` block keyed on `${{ github.workflow }}-${{
github.ref }}`. Cancellation is conditional:
`cancel-in-progress: ${{ github.event_name == 'pull_request' }}`.

Rationale for the expression rather than a bare `true`: superseded PR runs
should be cancelled to save minutes, but a push-to-main run drives the release
tag lane (`auto-tag-release`) and must never be cancelled mid-flight by a
following push. Keying on `github.ref` already isolates each PR branch and the
`main` ref into separate groups; the conditional only decides whether a newer
run in the *same* group cancels the older one.

## A-037 — payload gate on push-to-main as an auto-tag prerequisite

The sibling task `07-25-audit-release-gate-scope` (archived) explicitly
recorded A-037 as a deferred follow-up rather than implementing it, so
ownership lands here. The prd's "implement in exactly one of the two tasks"
resolves to: implement here.

Design: widen the existing `release-payload-gate` job to also run on
push-to-main, and make `auto-tag-release` depend on it. Two problems to solve:

1. **Base selection differs by event.** On a pull request the base is
   `github.event.pull_request.base.sha`. On push-to-main there is no PR base;
   the correct base is the last release tag, so the gate asks "since the last
   release, does the accumulated payload change carry a version bump?" — the
   exact invariant `auto-tag-release` is about to act on.
2. **The gate script already accepts `--base <ref>`.** No script change is
   needed for A-037; only the workflow computes the base and passes it.

Concretely:

- Change `release-payload-gate` `if:` from pull-request-only to
  `github.event_name == 'pull_request' || (github.event_name == 'push' &&
  github.ref == 'refs/heads/main')`.
- Its checkout already uses `fetch-depth: 0`; add `fetch-tags: true` (or an
  explicit `git fetch --tags --force`) so the last release tag is resolvable
  on push.
- Compute the base in one step: PR → `${{ github.event.pull_request.base.sha
  }}`; push → `git describe --tags --abbrev=0` (last release tag). If no tag
  exists yet (first release), fall back to the empty-tree/`--base HEAD`
  degrade the script already documents, so a tagless repo does not hard-fail
  the push lane.
- Add `release-payload-gate` to `auto-tag-release`'s `needs:` alongside
  `unittest, lint`. `auto-tag-release` keeps its own push-to-main `if:`, so on
  pull requests it still does not run; on push it now waits for the gate.

`ci-result` already aggregates `[unittest, lint, release-payload-gate]` with
`if: always()`; on push the gate now executes instead of being skipped, which
is still a valid aggregate input (skipped or success both pass).

Alternative considered and rejected: a separate `push-release-gate` job. It
duplicates the checkout + setup-python + install boilerplate for no benefit;
widening the existing job's `if` and base computation is smaller and keeps one
gate definition.

## A-014 — create-release-tag.py error contract

`create-release-tag.py`'s `run_git` calls `subprocess.run(..., timeout=60)`
with no guard, so a `subprocess.TimeoutExpired` or `FileNotFoundError` (git
absent) escapes as a raw traceback. `check-release-payload.py` already models
the clean contract: a `GateError` exception, a `run_git` that converts
`FileNotFoundError`/`TimeoutExpired` into `GateError`, and a `main()` that
prints `error: <message>` to stderr and returns 1.

Mirror that here:

- Add a module-level `class ReleaseTagError(Exception): pass` (a distinct name;
  the two scripts do not share a module, and "GateError" is payload-gate
  vocabulary).
- Wrap `run_git`'s `subprocess.run` in `try/except`, raising
  `ReleaseTagError("git not found")` on `FileNotFoundError` and
  `ReleaseTagError(f"git {' '.join(args)} timed out")` on
  `subprocess.TimeoutExpired`.
- In `main()`, wrap the body that calls `run_git` in `try/except
  ReleaseTagError as error:` → `print(f"error: {error}", file=sys.stderr);
  return 1`. Keep the existing per-call `returncode != 0` handling unchanged —
  those already print clean `error:` lines and return 1.

The message prefix is `error: <detail>` to match the repo's script contract
(`check-release-payload.py` prefixes with `error: release payload gate:`; this
script has no gate framing, so a bare `error: <detail>` is the honest parallel
and matches this script's existing `error: cannot ...` lines).

## Testing

- **A-014 (unit, hard-testable):** in `tests/test_release_gate.py`'s tag-script
  class, add a test that monkeypatches/`patch`es `subprocess.run` to raise
  `subprocess.TimeoutExpired` and asserts the script prints
  `error: git ... timed out` to stderr and returns exit 1 — no traceback. A
  `FileNotFoundError` variant is optional but cheap; include it.
- **A-038/A-039/A-037 (text-parse lock-in):** pyyaml is not a dependency, so
  add a small `tests/test_release_gate.py` (or a sibling) text-assertion class
  that reads `.github/workflows/tests.yml` and asserts: `cache: pip` appears on
  the three setup-python steps; a top-level `concurrency:` block keyed on
  workflow+ref with the PR-only cancel expression exists; `release-payload-gate`
  is in `auto-tag-release`'s `needs`; and the gate's `if:` includes the
  push-to-main clause. These lock the wiring so a future edit that drops any of
  them fails a test. The observable-in-CI ACs (cache hits, run cancellation)
  are verified by CI itself; the text assertions are the local proxy.

## Out of scope

- No change to the version-bump / changelog rules (owned by the archived
  release-gate-scope task).
- No change to `check-release-payload.py`.
- No branch-protection configuration (A-037 is implemented as a CI gate, so the
  "or document branch protection" alternative is not taken).

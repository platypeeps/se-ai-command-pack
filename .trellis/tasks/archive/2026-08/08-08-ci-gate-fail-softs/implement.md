# CI aggregate and gate fail-softs — Implementation Plan

Execute after `task.py start`. One coherent PR. Design decisions (including
the item 3 acceptance and the item 4 shellcheck declination) are recorded in
`design.md`; this plan sequences the four fix items and their proofs.

## Execution Order

1. **Aggregator script.** Add `.github/scripts/aggregate-ci-result.py`:
   reads `NEEDS_JSON` env, declares
   `REQUIRED_LANES = {"unittest", "lint", "release-payload-gate"}` and
   `CONDITIONAL_LANES = {"auto-tag-release"}`, applies the policy from
   design.md ("Data And Command Contracts"), exits 0/1/2 accordingly.
   Perform design.md's cross-task reconciliation **here, in this step**: if
   `review-preflight` has landed by now, it joins `REQUIRED_LANES` in this
   initial version of the script — not later — so the tests added in step 2
   pass against it and steps 1–2 stay independently commit-able. Match
   the style of the existing `.github/scripts/*.py`, keep it stdlib-only,
   and make it importable (`main()` guarded by `if __name__ == "__main__"`)
   so the test can exercise it in-process.
2. **Aggregator test.** Add `tests/test_aggregate_ci_result.py` exercising
   the imported logic with synthetic payloads: all-success → 0;
   `unittest: skipped` → nonzero (the PRD's required dynamic proof);
   `auto-tag-release: skipped` → 0; `auto-tag-release: failure` → nonzero;
   `lint: cancelled` → nonzero; undeclared extra lane → nonzero; declared
   lane absent → nonzero; malformed JSON → nonzero. If `review-preflight`
   has landed by now (step 1's reconciliation), include it in every payload
   as a required lane and add `review-preflight: skipped` → nonzero. Import the hyphenated
   script via `importlib.util.spec_from_file_location`, following the
   existing precedent in `tests/test_release_gate.py:26-30` exactly
   (including its subprocess-coverage plumbing where applicable).
3. **Wire the workflow.** In `.github/workflows/tests.yml`:
   - `ci-result.needs`: add `auto-tag-release` to the existing list —
     extend, do not replace, so any lane added since this plan was written
     (e.g. `review-preflight` from `08-07-ci-no-preflight-lane`) survives.
     Every lane in the final `needs` list must be declared in the script's
     lane sets, with the classification design.md's reconciliation note
     fixes and step 1 already applied: `review-preflight`, if present, is
     unconditional and lives in `REQUIRED_LANES`, never
     `CONDITIONAL_LANES`. Keep `if: always()`.
   - Add a checkout step to the `ci-result` job (it currently has none —
     fresh workspace, no repository): `uses: actions/checkout@v7` with
     `persist-credentials: false`, matching the other read-only jobs
     (`auto-tag-release` alone omits it because it pushes the tag).
   - Replace the inline heredoc step body with
     `python3 .github/scripts/aggregate-ci-result.py`, keeping the
     `NEEDS_JSON: ${{ toJSON(needs) }}` env exactly as is.
   - Add one step to the existing `lint` job (after the mypy step):
     `for f in scripts/*.sh; do bash -n "$f" || exit 1; done`.
   No new jobs beyond the reworked steps; no new workflow files.
4. **Makefile.** Three new targets plus wiring, all in `.PHONY`:
   - `shell-syntax`: the same `bash -n` glob loop; add to the `check`
     aggregate target.
   - `gate-test`: `$(RUN_PYTHON) -m unittest discover -s tests` (no
     coverage harness — guard-safe per design.md item 5).
   - `gate-lint`: same path list as `lint` but `ruff check --no-cache`,
     then the same mypy invocation. Extract the shared path list into a
     Makefile variable used by both `lint` and `gate-lint` so they cannot
     drift.
5. **`check.json`.** Create `.sd-ai-command-pack/check.json` exactly as
   specified in design.md item 5: schemaVersion 1, empty `prerequisites`,
   three checks (`repo.test`/`gate-test`/900 s, `repo.lint`/`gate-lint`/
   600 s, `repo.shellsyntax`/`shell-syntax`/60 s), every entry carrying
   `id`, `argv`, `cwd: "."`, and `timeoutSeconds` — all four fields are
   mandatory (`ENTRY_KEYS` membership `sd-ai-command-pack-check.py:65-66`,
   enforcement `:533-535`).

## Validation Plan

Run in order; each proof is demonstrated, not asserted:

1. `make test` — new aggregator tests pass inside the normal suite; coverage
   floor (80%) still met.
2. `make shell-syntax` — passes. Then copy one `scripts/*.sh` to a scratch
   path outside the repo, introduce a syntax error, run `bash -n` on it to
   show the failure mode, delete the scratch copy. (Do not edit the vendored
   file itself.)
3. `make gate-test && make gate-lint` — both pass directly.
4. `sd-check` via the toolchain wrapper — report contains `repo.test`,
   `repo.lint`, `repo.shellsyntax` rows, `stateGuard.status: passed`
   (proves the registered commands are guard-safe), overall pass.
5. Negative proof for item 5 (PRD acceptance criterion): break one repo-own
   unit test with a scratch edit, run `sd-check`, confirm `repo.test` fails
   and the aggregate is nonzero; revert the scratch edit; re-run to green.
6. `make check` — full aggregate green on the final tree.
7. After PR creation: confirm the CI `ci-result` lane goes green with the
   new `needs` list, and `auto-tag-release` shows `skipped` on the PR run
   without failing the aggregate.

## Documentation And Spec Updates

- No README change: none of the five items is user-facing installer surface.
- `sd-update-spec` runs in the ship flow as usual; no manual spec edits
  expected. If the reviewer asks where dispositions live, the answer is this
  task's `design.md` (committed with the PR).

## Review Notes

- The diff touches CI gating logic — reviewers should check the lane sets in
  `aggregate-ci-result.py` against the actual job ids in `tests.yml`
  (rename drift fails closed at runtime, but catching it in review is
  cheaper).
- `.sd-ai-command-pack/check.json` is a **new repo-own file inside a
  directory that otherwise holds pack-generated records** — the PR
  description must say so explicitly to preempt a "should this be
  vendored?" review round (`provenance.json` does not and must not list it).
- `gate-test`/`gate-lint` exist because sd-check's state guard forbids
  `.coverage` and `.ruff_cache` writes (design.md item 5 constraint
  paragraph) — reviewers should not "simplify" them back to `test`/`lint`.
- The `pack.review-scope` check will demand a Tooling/generated scope section
  in the PR body (tooling files change); the `--prepare-tooling-body` helper
  handles it as in prior PRs.
- Item 1's test is the PRD's acceptance evidence; do not weaken it to a
  smoke test.

## Rollback Points

- Each numbered execution step is an independent commit-able unit; the
  workflow keeps working after steps 1–2 (script exists, unused), after step
  3 (fully wired), and after steps 4–5 (local gates extended).
- Full rollback = revert the single PR. Partial rollbacks: drop `repo.test`
  from `check.json` if gate runtime is unacceptable (recorded fallback in
  design.md); revert the lint-job step if `bash -n` misbehaves on a runner.

## Follow-Ups

Explicitly outside this PR:

- Review-preflight CI lane decision — `08-07-ci-no-preflight-lane`.
- Any shellcheck/deep-lint proposal for vendored shell — route via
  `08-07-vendored-artifact-upstream-route` (declined locally, design.md
  item 4).
- Branch-protection revisit trigger (second maintainer or stale-merge
  incident) — recorded in design.md item 3; no task filed until the trigger
  occurs.

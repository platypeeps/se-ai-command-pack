# Implement — Fix sd-review coordinator nested-check false-block

## Execution order

1. **Add the seam** — in `scripts/sd-ai-command-pack-review.py`, add module-level
   `_resolve_check(repo, state, state_path)` (near `_run_check`, ~line 677),
   with the recompute-always body and phase-non-regression from design.md.
2. **Rewire the gate** — replace the `state.get("check") is None` block at
   review.py:1796-1799 with `check = _resolve_check(repo, state, state_path)`
   followed by the unchanged `status != "passed"` guard.
3. **Regression test** — create `tests/test_review_coordinator.py` importing
   review.py via `importlib.util.spec_from_file_location`; implement the five
   assertions in design.md (AC1 recompute-over-cache, AC2 parity, AC3 genuine
   failure blocks, phase non-regression, first-entry advance). Use a `tmp`
   state file for the persistence assertions; stub `_run_check` by assigning
   `module._run_check = lambda repo: <report>` inside each test and restoring.
4. **No generated-surface impact** — review.py is not a generated payload;
   confirm `make generate --check` stays green and no version bump is needed
   (mirrors the prior two iterations: `.github/scripts` + tests are not gated
   release payload).

## Validation plan

- Narrow: `bash scripts/sd-ai-command-pack-toolchain.sh run-python -- \
  -m unittest discover -s tests -p test_review_coordinator.py` — all new tests
  pass (need `PYTHONPATH=tests` only if importing by module name; discover does
  not).
- Lint: `bash scripts/sd-ai-command-pack-toolchain.sh run -- ruff check \
  scripts/sd-ai-command-pack-review.py tests/test_review_coordinator.py`.
- Generated surfaces: `make generate --check` (or the toolchain-run generator
  `--check`) exit 0.
- Empirical parity smoke (best-effort, on the PR branch during ship): after the
  finalization commit, confirm the coordinator's `knowledge.obsidian-kb` row
  now tracks a fresh `.obsidian-kb` refresh at an unchanged head instead of
  serving a stale report.

## Named falsifiable check (pre-registered)

`run-python -- -m unittest discover -s tests -p test_review_coordinator.py`
must report **OK** with the AC1 test specifically asserting the fresh (passed)
report is returned when a stale failing report is cached. Failure = the gate
still serves the cache (fix ineffective) or a new test regression. Also: the
full existing suite shows **0 new failures**.

## Follow-ups / out of scope

- Do **not** change `local`/`remote`/`capability` memoization — their inputs
  are captured by identity; touching them risks resume idempotency.
- Broader question of whether other durable-cached stages read uncaptured live
  inputs is out of scope; none identified for `local`/`remote`.
- No history rewrite, no identity-schema change.

## Rollback

Single-file logic change plus one new test file. Rollback = revert the
`review.py` hunk (restore the `state.get("check") is None` gate) and delete
`tests/test_review_coordinator.py`. No data/schema migration.

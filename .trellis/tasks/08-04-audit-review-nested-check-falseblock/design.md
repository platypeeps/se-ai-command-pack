# Design — Fix sd-review coordinator nested-check false-block

## Root cause (confirmed empirically)

`scripts/sd-ai-command-pack-review.py` memoizes the **entire typed sd-check
report** into its durable per-attempt state and then serves that cached report
as the deterministic gate:

```
review.py:1796-1799
    if state.get("check") is None:
        check = _run_check(repo)
        _advance(state_path, state, "check", check=check)
    check = state["check"]
```

The state file (`<artifact-root>/<attempt_id>.json`) is keyed on `attempt_id`,
derived (`_attempt_id`, `_state_identity` at review.py:534-620) from
`repo, scope, head, base, worktreeDigest, prNumber, controls`. Two of the
deterministic checks read **live inputs that this identity deliberately does
not capture**:

- `knowledge.obsidian-kb` (check.py:927-952 -> `update-spec-kb.py --check`)
  enumerates the **live filesystem** — the gitignored `.obsidian-kb` directory
  **symlink** to an external Obsidian vault and the `.trellis/**` source tree.
  `_worktree_digest` (review.py:555-576) hashes only tracked diff plus
  `git ls-files --others --exclude-standard`, so the gitignored symlink target
  is excluded; and for **PR scope `worktree_digest` is `None`** (review.py:1706).
- `pack.review-scope` (check.py:954-962 -> `review-scope.sh:211`) reads the
  **live PR body** via `gh pr view`; only `prNumber` is in identity, not the
  body text.

Consequence: once a genuinely-stale computation is cached at a head (e.g. the
finalization commit adds archived-task docs so expected-copies rises to 481
before the `.obsidian-kb` target is refreshed, and the check legitimately
computes 478), every later run at the **same head** — including after the KB is
refreshed or the PR body is fixed — serves the stale 478/absent-section report
as the gate. Both rows live in the one cached report, so they false-fail
together. This is a single cause with a single fix. `--attempt` does not change
`attempt_id` (identity excludes it), so incrementing the attempt number does not
escape the cache; only a head change does.

Refuted alternatives: `build_tool_environment` (sd_ai_command_pack_lib.py:239-293)
only rewrites cache-dir env vars (XDG/UV/PIP/RUFF/NPM), none affecting symlink
resolution or `os.walk`; a fresh nested review with an empty artifact-root
returns both rows `passed`, identical to a direct `check.py` run. cwd/symlink
and git-ref-snapshot hypotheses are refuted — the KB helper reads the live tree.

## Fix

The deterministic sd-check is the **cheap, idempotent** gate whose inputs are
partly outside the state identity. It must be recomputed on every invocation
rather than served from cache. The expensive `local` and `remote` stages stay
memoized: their inputs (worktree content, head) **are** captured by
`worktreeDigest`/`head`, so their cache remains valid.

Introduce a small module-level helper and call it in `run()`:

```python
def _resolve_check(repo: Path, state: dict[str, Any], state_path: Path) -> dict[str, Any]:
    # Always recompute the deterministic sd-check. It is the cheap idempotent
    # gate and reads live inputs (the gitignored .obsidian-kb symlink target,
    # the live PR body) that the state identity deliberately does not capture,
    # so a memoized report would serve a stale pass/fail after those inputs
    # change at an unchanged head. Persist the fresh report for reporting
    # without regressing the phase on resume; the expensive local/remote stages
    # stay memoized because their inputs are captured by worktreeDigest/head.
    check = _run_check(repo)
    if state.get("check") is None:
        _advance(state_path, state, "check", check=check)
    else:
        state["check"] = check
        state["updatedAt"] = int(time.time())
        _atomic_json(state_path, state)
    return check
```

`run()` at 1796-1799 becomes:

```python
    check = _resolve_check(repo, state, state_path)
    if not isinstance(check, dict) or check.get("status") != "passed":
        return 1, _report(
            state=state,
            status="blocked",
            diagnostic="typed sd-check did not pass",
            limitations=("deterministic-check-not-passed",),
        )
```

### Why not just delete the guard inline

The extracted helper is the **testable seam**: a regression test can stub
`_run_check` and assert recompute-over-cache without standing up git/gh/PR
discovery and the local/remote providers that a full `run()` call needs.

### Phase non-regression

On a first entry (`state.get("check") is None`) the helper calls `_advance`,
exactly as today (phase -> `check`). On a **resume** where `local`/`remote` are
already cached, it persists the fresh check via `_atomic_json` **without**
calling `_advance`, so the recorded `phase` is not rolled back to `check`. The
downstream gates remain `state.get("local"/"remote") is None`, so cached stages
are still consumed unchanged.

## Contract

- `_resolve_check` returns the fresh `_run_check(repo)` result on every call.
- Post-fix, `review.py`'s gate pass/fail for `knowledge.obsidian-kb` and
  `pack.review-scope` equals a direct `check.py` run on the same tree, because
  the report is recomputed live each invocation.
- Genuine failures still block in both paths: a stale KB or an absent scope
  section makes `_run_check` return a failing report, which `_resolve_check`
  returns and the gate rejects — cache can no longer mask it.
- No change to `local`/`remote`/`capability` memoization or to identity.

## Risks and mitigations

- **R-1 — resume cost**: recomputing the cheap deterministic check on every
  resume adds one check.py run (git whitespace, preflight, install-audit, KB,
  scope). Acceptable: this is the gate's purpose and it is seconds-scale;
  correctness outranks reusing a stale gate.
- **R-2 — phase mislabel**: mitigated by not calling `_advance` on resume
  (above); the phase field is never rolled backward.
- **R-3 — hidden dependence on cached check elsewhere**: `state["check"]` is
  consumed only at this gate and in `_report`; the helper keeps `state["check"]`
  populated with the fresh report, so reporting is unaffected.
- **R-4 — over-broad change**: scope is strictly the check gate; `local` and
  `remote` memoization is deliberately untouched, preserving resume idempotency
  for the expensive stages.

## Test strategy (satisfies AC1-AC3)

New `tests/test_review_coordinator.py`, importing review.py via
`importlib.util.spec_from_file_location` (the `tests/test_generate.py` pattern):

1. **AC1 pre-fix divergence, reproduced at the seam**: seed a `state` dict with
   `check={"status":"failed",...}` (a stale report), `phase="remote"`, and
   cached `local`/`remote`. Stub `_run_check` to return
   `{"status":"passed",...}` (the live tree now passes). Assert
   `_resolve_check` returns the **passed** report (not the cached failed one) —
   the exact behavior the pre-fix `state.get("check") is None` gate got wrong
   (it would have returned the cached failure). Document in the test that the
   old gate served the cache.
2. **AC2 parity**: assert `_resolve_check`'s return equals the stubbed
   `_run_check` output for both passed and failed stubs — nested mirrors direct.
3. **AC3 genuine failure still blocks**: stub `_run_check` -> failed; assert
   `_resolve_check` returns failed and `state["check"]["status"] == "failed"`.
4. **Phase non-regression**: after a resume-path call (pre-existing `check`),
   assert `state["phase"]` is unchanged (`"remote"`) and cached
   `state["local"]`/`state["remote"]` are byte-identical.
5. **First-entry advance**: with no pre-existing `check`, assert `_advance`
   path ran (`state["phase"] == "check"`, `state["check"]` persisted to disk).

Validation commands (via toolchain; bare python/pytest unavailable):
`run-python -- -m unittest discover -s tests -p test_review_coordinator.py`,
plus `ruff` and `make generate --check` sanity (no generated-surface impact).

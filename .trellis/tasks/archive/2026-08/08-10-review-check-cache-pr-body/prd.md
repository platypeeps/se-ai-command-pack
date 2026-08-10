# Review controller caches sd-check results under an identity that omits the PR body

## Goal

Make a deterministic check whose input is the pull-request body re-runnable
after that body changes. Today the review controller can pin an attempt to a
stale check failure with no supported way to clear it.

## Background

`scripts/sd-ai-command-pack-review.py` stores the full typed `sd-check` payload
in its per-attempt private state and replays it:

```python
if state.get("check") is None:
    check = _run_check(repo)
    _advance(state_path, state, "check", check=check)
```

The attempt is keyed by `_state_identity(...)`, whose fields are the repository
root, scope, controls (`local`/`remote`/`fix`/`successor` plus the configuration
digest), pull-request number, base, head, and — for non-PR scopes — a worktree
digest. The pull-request **body** is not part of that identity.

`pack.review-scope` reads the PR body: it fails when tooling/generated files
changed and the body carries no recognized scope heading. So the two facts
compose into a trap:

1. The check fails because the body lacks the heading.
2. The operator fixes the body on GitHub — the correct remediation.
3. Identity is unchanged, so the same attempt is loaded, `state["check"]` is
   non-null, and the *failed* row is replayed forever.

Observed on PR #199 (2026-08-10): four consecutive invocations returned a
byte-identical row — `pack.review-scope`, `status failed`, `durationMs 952` —
under one unchanged `attemptId`, while running the check's own argv directly
under the coordinator's environment exited 0. `--attempt` does not help: it is
a round counter (`--attempt N`), not part of the state key. The only escape was
an operator-chosen `--attempt-id`: there is no `--recheck` control and no
per-stage input the caller can vary to force this stage to run again. That
discards the coordinator's attempt state — remote request, receipt, observation,
recorded dispositions — along with the stale check. (It does not discard the
local stage's provider receipt, which is keyed by target and plan rather than by
attempt id; an earlier draft of this PRD said otherwise.)

### Second observation: the same shape, one stage over

PR #201 (2026-08-10) hit a sibling of this trap in `state["local"]`:

```python
if state.get("local") is None or args.local_disposition:
    ...
    _advance(state_path, state, ..., local=local)
```

A disposition set naming finding IDs that no longer exist at the current head
makes `_run_local` return `invalid`. That `invalid` report is persisted, and
the next invocation — *with no dispositions at all* — takes the cached branch
and replays it. The observed diagnostic was byte-identical across invocations:

```
status invalid ... local disposition ids match no finding at this head:
84d387148b8086de, 8dda260b0a791816, ...
```

The escape used was again an operator-chosen `--attempt-id`. Unlike the check
trap it was not the only one available: `or args.local_disposition` re-enters
the stage whatever is cached, so a disposition set that *does* match a finding
at the current head would have replaced the rejection in place. That needs a
valid id to exist, which is exactly what a stale set means it might not.

Provenance of both observations: the invocation counts, `durationMs 952`, and
the finding ids are live coordinator output captured while working PRs #199 and
#201, and this PRD is the only place they are written down — the coordinator's
per-attempt state is private and short-lived, and neither pull request preserves
them in its body, comments, or review comments. Treat them as the report of the
run that saw them, not as figures a later reader can re-derive from GitHub. What
*is* independently reproducible is the defect itself: the regression tests in
platypeeps/sd-ai-command-pack#417 fail against `d7913054` and pass after it.

Both traps share one root cause, and it is narrower than "the identity omits an
input": the controller caches **terminal-failure results**. Caching exists so
an interrupted run resumes instead of repeating completed work. A `failed`
check and an `invalid` local report are not completed work — they are verdicts
that the next invocation is entitled to recompute. This was written as the
leading candidate design and is what shipped; it is smaller than all three
options below and closed a third manifestation the options did not name.

(The title above states the cause as first diagnosed — an identity that omits
the body. That framing is narrower than the truth in one direction and wider in
another: the body is one of several uncovered inputs, and widening the identity
was rejected. The paragraph above is the conclusion; the title is kept so the
task stays findable under the name it was filed with.)

## Requirements

- A change to an input that a registered check actually reads must be able to
  invalidate that check's cached result.
- The remediation must not require hand-editing controller private state, and
  must not force the operator to discard the attempt's durable local/remote
  review receipts to get one check re-run.
- Whatever mechanism is chosen must keep the existing idempotency guarantee:
  a plain re-invocation after an interruption still resumes rather than
  re-running completed work.

## Disposition

`scripts/sd-ai-command-pack-review.py` is vendored (Registry B,
`install: "always"`), so this task's deliverable is an upstream change, not a
local one. The routing decision, the fix, and its evidence are recorded in
[`disposition.md`](disposition.md); the acceptance criteria below are ticked
against **platypeeps/sd-ai-command-pack#417**. Nothing is implemented in this
repository, and the trap persists on any installed pack below v0.66.1.

## Design questions for the planning phase — resolved

All three were rejected in favour of the narrower root cause named above — the
controller caches terminal-failure verdicts — which is smaller than each of
them and closes both manifestations plus a third at once. See `disposition.md`
for the mechanism. The three are kept below as the record of what was weighed,
not as a choice still open:

- **Widen the identity.** Add a digest of the body (or of every declared check
  input) to `_state_identity`. Correct by construction, but a body edit then
  discards the whole attempt including remote receipts — the same loss the
  `--attempt-id` workaround causes.
- **Scope the cache to the check.** Store the check result under its own key
  including an input digest, so only the affected row re-runs and the local and
  remote stages keep their evidence. More moving parts, best behavior.
- **An explicit typed refresh control.** e.g. `--recheck`, which clears only
  `state["check"]`. Smallest change; relies on the operator noticing.

## Acceptance criteria

Each is met upstream in platypeeps/sd-ai-command-pack#417; the quoted evidence
is reproduced in full in `disposition.md`.

- [x] A test drives the PR #199 sequence at the layer that owns the defect:
      cache a check failure, re-invoke the same attempt, and assert the check
      re-runs and passes. It must fail against today's code.
      — `test_failed_check_is_recomputed_on_the_next_invocation`. Against
      `d7913054` it fails
      `AssertionError: Tuples differ: (1, 'blocked') != (0, 'ready')`.

      Reworded during review. The original criterion said "change only the body
      input", which no controller test can do: the body is read by
      `pack.review-scope` inside `sd-check`, two processes away, and the
      controller reaches it only through `_run_check`. The test mocks
      `_run_check` `failed` then `passed` — the faithful model of an operator
      fixing the body between invocations. What the controller owes is that the
      second invocation *asks again*; that it asks is the whole defect, and it
      is what the test pins. Nothing weaker than the original intent is being
      accepted, but the original wording promised evidence at a layer the fix
      does not live in.
- [x] The chosen mechanism is documented wherever the controller's caching and
      resume contract is described.
      — the `sd-review` skill definition in the upstream pack (canonical copy
      under its templates tree), in the paragraph that already states the
      resume-idempotency contract. Named without a repo-relative path on
      purpose: that path exists upstream, not here, and the preflight's
      path-reference check reads prose paths as local ones.
- [x] A plain re-invocation with no changed input still replays the cached
      result — the idempotency guarantee is covered by its own test.
      — `test_unchanged_passing_stages_still_replay_from_the_cache` asserts
      `_run_check` and `_run_local` are each called exactly once across two
      invocations. `test_policy_blocked_local_report_stays_cached` covers the
      complement: `blocked` is identity-determined, so it stays cached.
- [x] The `state["local"]` manifestation is closed by the same mechanism and
      covered by its own tests: produce an `invalid` local report from a stale
      disposition set, re-invoke with no dispositions, and assert the rejection
      is not replayed — recomputing when nothing durable was stored, and
      reusing the stored report when one was.
      — Two tests, because the guarantee has two arms and only stating both
      describes the mechanism honestly:
      `test_rejected_disposition_without_a_stored_report_recomputes` (nothing
      stored: `_run_local` runs twice across two invocations) and
      `test_rejected_disposition_neither_replays_nor_evicts_the_report` (a
      clean report already stored: it survives the rejection and the third,
      disposition-less invocation reuses it — `_run_local` runs twice across
      *three* invocations). Both fail against `d7913054` with
      `AssertionError: Tuples differ: (2, 'invalid') != (0, 'ready')`.

      Reworded and the first test added during review. The original criterion
      asserted a recompute unconditionally. That is true only when no durable
      report exists; when one does, not evicting it is the better outcome and
      the stage correctly does not re-run. The criterion now says what the
      mechanism actually guarantees: a rejection is never replayed, and it
      never costs a report that already existed.

A third manifestation of the same root cause was found while designing the fix
and closed with it: a local provider `unavailable`/`failed`/`cancelled` report
turns on provider reachability, which the attempt identity does not cover
(`test_local_provider_failure_is_recomputed_on_the_next_invocation`).

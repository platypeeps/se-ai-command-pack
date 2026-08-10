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
an operator-chosen `--attempt-id`, which discards the attempt's local and remote
review evidence along with the stale check.

## Requirements

- A change to an input that a registered check actually reads must be able to
  invalidate that check's cached result.
- The remediation must not require hand-editing controller private state, and
  must not force the operator to discard the attempt's durable local/remote
  review receipts to get one check re-run.
- Whatever mechanism is chosen must keep the existing idempotency guarantee:
  a plain re-invocation after an interruption still resumes rather than
  re-running completed work.

## Design questions for the planning phase

Choose deliberately between:

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

- [ ] A test drives the exact PR #199 sequence: cache a `pack.review-scope`
      failure, change only the body input, re-invoke, and assert the check
      re-runs and passes. It must fail against today's code.
- [ ] The chosen mechanism is documented wherever the controller's caching and
      resume contract is described.
- [ ] A plain re-invocation with no changed input still replays the cached
      result — the idempotency guarantee is covered by its own test.

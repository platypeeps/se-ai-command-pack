# Pack refresh destroys the local review.py stale-cache fix

## Goal

Make the local fork of `scripts/sd-ai-command-pack-review.py` survive contact
with a pack refresh — either by getting the fix upstream, or by recording the
fork so a refresh is a deliberate decision rather than a silent reversion.

The defect is not the stale cache. That bug is upstream's and is already fixed
here. The defect is that **the fix has no route to durability**: the file is
`install: "always"`, so every refresh reverts it, and nothing warns a run before
it does.

## Problem

> Line citations are pinned to installed pack `0.64.3`:
> `scripts/sd-ai-command-pack-review.py` at 2076 lines, `install: "always"` in
> `.sd-ai-command-pack/manifest.json`. Upstream citations are pinned to
> `sd-ai-command-pack` tag `v0.64.27`, path
> `templates/scripts/sd-ai-command-pack-review.py`, which is byte-identical to
> that repo's own installed `scripts/` copy. Every citation names its enclosing
> symbol — re-locate by symbol, not by line, on any other version.

This repository carries a committed local fix to a vendored file that no
upstream version has:

| | |
| --- | --- |
| `bc01bc2` (2026-08-04) | `fix(review): recompute deterministic sd-check every run, don't serve stale cache` — adds `_resolve_check`, plus `tests/test_review_coordinator.py` (5 tests) |
| `4d62cd9` (2026-08-04) | `chore(provenance): record review.py hash after coordinator fix` — re-records provenance so the install audit stays green |

The upstream bug `bc01bc2` fixes is real and still unfixed. Upstream's
coordinator gates on a memoized report (`main`,
`templates/scripts/sd-ai-command-pack-review.py:1827` at `v0.64.27`):

```python
if state.get("check") is None:
    check = _run_check(repo)
    _advance(state_path, state, "check", check=check)
check = state["check"]
```

`state["check"]` is initialised to `None` and is never invalidated anywhere in
that file, and the state identity captures only `worktreeDigest` and `prNumber`
— not the PR body, not the `.obsidian-kb` symlink target. So once a stale
computation is cached at a head, every later run at that head serves it, even
after the KB is refreshed or the PR body fixed. `bc01bc2`'s message records the
consequence: it false-blocks the post-finalization successor-head review on
every completed task.

### The fix exists in exactly one place, and refresh deletes it

Verified by doing it. Refreshing `0.64.3` → `0.64.27` with `--force`:

- `_resolve_check` went from 2 occurrences to 0
- the five `ResolveCheckTest` tests errored with
  `AttributeError: module 'sd_review_coordinator' has no attribute '_resolve_check'`
- `make test` went from `Ran 575 tests — OK (skipped=1)` to `FAILED (errors=5)`
- `make lint` and `make release-check` both still passed, so the guard tests are
  the *only* thing standing between a refresh and a silent behavioural
  regression

The refresh was reverted; the fork is intact. But the refresh was otherwise
clean — `state: current`, install audit passed, 34 changed paths all
manifest-declared — so a run with no knowledge of `bc01bc2` has every reason to
believe it succeeded, and only `make test` disagrees.

### `_resolve_check` is absent from every upstream version, not just the current one

Checked every `v0.6*` tag from `v0.64.0` back through `v0.6.0` and forward to
`v0.64.27` (33 tags): zero occurrences in
`templates/scripts/sd-ai-command-pack-review.py`. The symbol appears nowhere in
that repository's 1975-commit history. This is a fork, not a reverted upstream
change — a distinction worth stating because the reverse reading is the natural
one from the consumer side, where the symbol appears to *vanish* on refresh.

### The install audit cannot see the fork

`install.py . --check --audit` reports `Installed payload provenance: version
0.64.3; vouched file hashes match` while that file differs from its `v0.64.3`
template by 29 diff lines. This is structural, not a bug in the audit:
provenance records the hash of what was installed, and `4d62cd9` deliberately
re-recorded it after the local edit. The consequence still matters — no pack
command can tell an operator which vendored files a refresh will clobber, so
the fork is invisible at exactly the moment that knowledge is needed.

Whether the audit should be able to see it is a separate question and a separate
task; this one only needs the fact recorded.

## Requirements

- Record the fork durably: the file, the owning pack, the commit that introduced
  it, the upstream status, and the precondition that must hold before a refresh
  is safe. A run considering a refresh must be able to discover this without
  reading git history.
- State the refresh precondition as a checkable claim, not a warning: a refresh
  of this repository is safe only once `_resolve_check`'s behaviour exists
  upstream, or the fork is deliberately re-applied afterwards.
- Name the existing guard and its limits. `tests/test_review_coordinator.py`
  detects the reversion, but only after the refresh has already been applied,
  and only when the suite is run. It is a detector, not a preventer.
- Do not re-apply the fork by editing the vendored file as part of this task.
  The file is already correct in the working tree; this task is about the route,
  not the content.
- Do not weaken the authority boundary. The upstream fix is tracked separately
  in `sd-ai-command-pack` and needs explicit per-PR approval; this task does not
  grant it.
- Reconcile the vendored-artifact membership table in
  `08-07-vendored-artifact-upstream-route/prd.md` and every derived count. That
  table is authoritative for membership; the counts in its prose, `task.json`
  description and notes, and `implement.jsonl` are all derived and must agree.

## Acceptance Criteria

- [ ] A run holding the path `scripts/sd-ai-command-pack-review.py` can
      determine from the recorded guidance alone that it is a local fork, which
      commit owns it, and what must be true before a refresh.
- [ ] The recorded refresh precondition is verifiable by a command, and that
      command is shown to fail against a refreshed tree and pass against the
      current one. Demonstrated, not asserted.
- [ ] The record states that `make test` is the existing detector and that it
      only fires post-refresh, so it does not satisfy the precondition on its
      own.
- [ ] The vendored-artifact table in `08-07-vendored-artifact-upstream-route`
      gains this task as a row, and every derived count in that task agrees with
      the table. Verified by enumerating the counts, not by reading in sequence.
- [ ] The upstream task in `sd-ai-command-pack` is referenced by ID, and the
      record states plainly that no upstream PR has been opened.
- [ ] `scripts/sd-ai-command-pack-review.py` is unchanged by this task, verified
      against `bc01bc2`'s content.

## Out of scope

- Fixing the stale-cache bug upstream. That is the separate `sd-ai-command-pack`
  task, and opening its PR is approval-gated.
- Refreshing the pack. Blocked by this task, not performed by it.
- Making the install audit detect deliberate forks. Real, distinct, and worth its
  own task with its own justification — provenance recording installed hashes is
  a design choice, not an oversight.
- Any change to `tests/test_review_coordinator.py`. The five tests are correct
  and caught this; weakening them to accommodate a refresh would delete the only
  detector.

## Notes

- Eighth instance of the vendored-artifact pattern whose canonical membership
  table lives in `08-07-vendored-artifact-upstream-route/prd.md`. It is the
  sharpest instance so far and differs from the other seven in kind: in those,
  a defect sits unfixed in a vendored file. Here the **fix exists and a refresh
  destroys it**. That strengthens T-10's argument — the local-only route is not
  merely a lesser outcome, it is a standing liability with an expiry date set by
  the next refresh.
- Discovered 2026-08-07 while attempting the long-deferred `0.64.3` → `0.64.27`
  refresh. The refresh was completed, verified, and reverted in one session; the
  reversion is why the fork is still intact.
- The same refresh attempt confirmed PR #164's thesis empirically: every line
  number in the T-1 and T-2 citations moved (`render_local` 2090 → 2146,
  `status.py` 2631 → 2706) and all 13 symbol anchors still resolved.
- Ordered last in the `quality-guidelines.md` landing cluster (order 70, after
  `08-07-status-collector-pack-drift` at 60). It depends on T-10's shared
  guidance existing (order 5), because the record this task writes is an
  application of that guidance rather than a restatement of it.
- Planning depth: PRD-only. The deliverable is a recorded fork register and a
  checkable precondition; there is no design to make.

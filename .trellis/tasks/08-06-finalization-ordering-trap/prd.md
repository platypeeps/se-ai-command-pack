# Planning finalization cannot absorb a review fix that lands after the journal commit

## Goal

Give an `sd-ship` chain a sanctioned way to finish when a remote review arrives
after Stage 2b's finalization, instead of stopping at a merge gate whose only
exit is a command the chain is forbidden to run.

## Problem

Stage 2b records the journal commit and captures a finalization base. Stage 4
must recompute the receipt against **that same captured base** when the head has
moved, and it must invoke zero finish-work flows. Those two rules are
individually correct and jointly unsatisfiable once a review-fix commit lands
after the journal commit:

```
81fc2cb fix(docs): ...          <- review fixes, touches an authored spec file
a63a871 chore: record journal   <- Stage 2b finalization
392954f docs: ...               <- work; captured as the finalization base
```

Recomputing `--mode planning --base 392954f --head 81fc2cb` yields:

```
status: invalid   reasonCodes: ['bundle_scope_invalid']
path: .trellis/spec/backend/quality-guidelines.md
message: finalization delta contains a non-bookkeeping path
```

Planning finalization requires the base-to-head delta to be bookkeeping only.
The fix commit put an authored path inside that range, so no valid receipt
exists for any base the chain is permitted to use. Stage 4 stops; Stage 3 was
already green; nothing in the chain can advance.

The recovery that works is a **fresh** `sd-finish-work` invocation, which
re-captures the base at the current tip and writes a second journal session:

```
status: valid   reasonCodes: ['planning_bundle_valid']
subtype: journal-only-recovery
changedPaths: ['.trellis/workspace/.../index.md', '.trellis/workspace/.../journal-3.md']
```

That is outside the chain, so the do-not-rerun rule does not apply — but nothing
in `sd-ship`'s report says so. The stopping report names the validator failure,
not the route out.

## Why this recurs rather than being a one-off

The trigger is *when the remote review arrives*, not what it says.

When the review router is `absent` (`routerCapability.state: absent`,
`limitations: ['router-not-configured', 'zero-remote-confidence']`), Stage 2 has
no remote stage to wait on and completes as soon as local checks pass. A
platform auto-review — GitHub Copilot here — then lands during Stage 2b or
Stage 3. Any finding it raises against authored content produces a fix commit
after the journal commit, which is exactly the failing shape.

Contrast PR #156, where the ordering was fix → journal → merge and the receipt
validated on the first attempt. The difference was review timing alone.

So the failure is systematic for repositories with an auto-reviewer and no
configured router, which is this repository's current configuration.

## Requirements

- Decide and record a disposition:
  - **Documentation-only.** Teach the stopping report — or this repository's
    spec — that a `bundle_scope_invalid` recomputation after a post-finalization
    fix is resolved by a fresh `sd-finish-work`, not by retrying Stage 4. Cheap,
    local, and available without upstream approval.
  - **Upstream.** Let Stage 4 recognize this exact shape and either re-derive
    the base at the last non-bookkeeping commit or hand back a typed
    `needs-refinalization` outcome that names the recovery command.
- Any upstream proposal must preserve the properties the current rules protect:
  finish-work runs once per chain, Stage 4 never produces bookkeeping, and the
  merge gate still requires an exact-head receipt. Reordering or amending
  published commits is not an acceptable route.
- The recovery must stay valid when the fix commit touches only bookkeeping
  paths, where the existing recomputation already succeeds. Do not regress that
  case into an unnecessary second journal session.
- Record the interaction with review timing explicitly, so a reader understands
  the trap is reachable only when a review lands post-finalization.

## Constraint: the stages are not owned by this repository

`sd-ship` and `sd-finish-work` are installed from the sd-ai-command-pack
(`.sd-ai-command-pack/manifest.json`). Edits here are overwritten by the next
pack refresh, so any change to stage behaviour or to the stopping report is an
**upstream** pull request needing its own approval. Only this repository's
`.trellis/spec/` guidance is editable locally — which is why the
documentation-only route must be viable on its own.

## Acceptance Criteria

- [ ] The disposition is recorded with reasoning, including whether upstream
      approval was sought.
- [ ] A run that hits `bundle_scope_invalid` after a post-finalization fix can
      reach the correct recovery from the written guidance alone, without
      re-deriving it from the validator's `findings` array.
- [ ] The guidance states plainly that the in-chain rerun is forbidden and the
      fresh invocation is not, and why the two differ.
- [ ] The bookkeeping-only fix case is explicitly excluded, with its passing
      behaviour named.
- [ ] If the upstream route is chosen, the local documentation lands first and
      does not depend on the upstream change merging.

## Out of scope

- Changing the planning bundle's scope rules so authored paths become
  acceptable in a finalization delta. That would weaken the gate this task
  depends on.
- Making Stage 2 wait for an unconfigured remote reviewer. Review-timing
  configuration is a separate question from the ordering trap.
- Any history rewriting — amend, reset, rebase — as a recovery.

## Notes

- Observed end-to-end on PR #157 (2026-08-06); the merge succeeded only after a
  separate `sd-finish-work` invocation.
- Sibling of `08-06-work-loop-shipped-sha-after-branch-delete`: both are cases
  where a documented call shape cannot be satisfied against the state the
  preceding stage actually leaves behind.
- Lightweight enough to stay PRD-only unless the upstream route is chosen.

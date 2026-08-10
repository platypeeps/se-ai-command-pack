# Planning finalization cannot absorb a review fix that lands after the journal commit

## Goal

Give an operator a sanctioned, documented recovery when an `sd-ship` chain
stops because a remote review arrived after Stage 2b's finalization — from the
`bundle_scope_invalid` stop through to the merge — instead of leaving the only
exit undocumented. An in-chain exit (the chain itself recognizing the shape)
is upstream substance and is not what this task delivers.

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
evidence.planningSubtype: journal-only-recovery
changedPaths: ['.trellis/workspace/.../index.md', '.trellis/workspace/.../journal-3.md']
```

(The subtype is reported as `evidence.planningSubtype` in the validator's JSON
— `scripts/sd-ai-command-pack-review-preflight.mjs:697-703`, `:2551-2560` — not as a top-level `subtype`
key. The recovery is also conditional, not unconditional: it requires exactly
one newly completed journal session whose bundle contains only that journal
and its sibling index, with bounded, published, single-parent cited commits —
`scripts/sd-ai-command-pack-review-preflight.mjs:2536-2573`, `:2593-2623`, `:2668-2725`.)

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

Every implementation surface classifies as vendored under the ownership lookup
in `.trellis/spec/backend/quality-guidelines.md` ("Vendored-Artifact Ownership
And Upstream Route"), all via Registry B (`.sd-ai-command-pack/manifest.json`):

- `.agents/skills/sd-ship/SKILL.md` and `.agents/skills/sd-finish-work/SKILL.md`
  — `kind: skill`, `install: "always"`.
- `.claude/skills/sd-ship/SKILL.md` and `.claude/skills/sd-finish-work/SKILL.md`
  — `kind: skill`, `anchor: ".claude"` with no `install` key
  (`if-anchor-exists`, vendored).
- `scripts/sd-ai-command-pack-review-preflight.mjs` — `kind: script`,
  `install: "always"`.

That section's disposition rule applies: no in-place vendored edits, an
upstream PR needs explicit per-PR approval (excluded from run-level authority),
and local-only is a legitimate terminal record carrying the four-field record
format defined there. Only this repository's `.trellis/spec/` guidance is
editable locally — which is why the documentation-only route must be viable on
its own.

## Disposition

**Documentation-only, with an upstream relay issue.** Chosen at planning,
executed by this task's implementation:

- Write the recovery guidance into
  `.trellis/spec/backend/quality-guidelines.md`, covering the **whole route to
  the merge**, not just the receipt: the failing shape (`bundle_scope_invalid`
  on a planning-mode receipt recomputation after a post-finalization fix
  commit touches an authored path), the sanctioned recovery (a **fresh**
  `sd-finish-work` invocation outside the stopped chain, which re-captures the
  base and — when its delta is exactly the one new journal session plus its
  sibling index — validates as `evidence.planningSubtype:
  journal-only-recovery`), the completion of the recovery (push, checks green,
  then `sd-housekeeping` invoked directly with the fresh receipt via
  `--finish-work-receipt`; the stopped chain itself is never restarted), why
  the in-chain rerun stays forbidden while the fresh invocation is not, and
  the explicitly excluded bookkeeping-only case, where the existing captured-
  base recomputation already passes the path-scope check (later validator
  checks — file modes, whitespace, journal structure — can still fail
  independently).
- Record the four-field local-only record in both this PRD and the guidance
  section, per the record format in the ownership-lookup guidance. The fourth
  field is the explicit statement that **no upstream PR was opened**; the
  relay issue URL is appended to that same field, not substituted for it.
- File one upstream relay **issue** (not a PR) on platypeeps/sd-ai-command-pack
  proposing that Stage 4 recognize this exact shape — re-derive the base at the
  last non-bookkeeping commit, or return a typed `needs-refinalization` outcome
  naming the recovery command — while preserving finish-work-once, no Stage 4
  bookkeeping, and the exact-head merge gate. Relay issues are precedented
  (#397–#399, #404, #405) and inside run authority; the upstream PR itself is
  not sought. **Filed:**
  <https://github.com/platypeeps/sd-ai-command-pack/issues/408>.
- This is a mitigation for the stopping report, not a change to it: the chain's
  own report remains vendored and still names only the validator failure. The
  guidance closes the gap on the operator's side. No upstream pull request was
  opened.

## Acceptance Criteria

- [ ] The disposition is recorded with reasoning, including whether upstream
      approval was sought.
- [ ] A run that hits `bundle_scope_invalid` on a planning-mode recomputation
      after a post-finalization authored-path fix — the eligible shape: one
      stopped chain, fix commits published on the same branch — can reach the
      correct recovery from the written guidance alone, without re-deriving it
      from the validator's `findings` array. The guidance names the expected
      validating result (`evidence.planningSubtype: journal-only-recovery`)
      and what to do when the recovery recomputation itself fails.
- [ ] The guidance covers the recovery through to the merge: fresh
      `sd-finish-work`, push and green checks, then a direct `sd-housekeeping`
      invocation with the fresh receipt. It states plainly that the stopped
      chain is never restarted, the in-chain rerun is forbidden and the fresh
      invocation is not, and why the two differ.
- [ ] The bookkeeping-only fix case is explicitly excluded, stating that the
      existing captured-base recomputation already passes the path-scope check
      there — and that later validator checks can still fail that recomputation
      for independent reasons.
- [ ] The upstream relay issue exists on platypeeps/sd-ai-command-pack and its
      URL is recorded in both this PRD and the guidance section's four-field
      record.
- [ ] If the upstream **implementation** route (a stage-behaviour PR, distinct
      from the relay issue) were chosen, the local documentation lands first
      and does not depend on the upstream change merging. Not chosen here; the
      relay issue does not trigger this criterion or the complex-task artifact
      requirement at `.trellis/workflow.md:164`.

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
- The trap is **planning-mode-specific**. The installed `sd-ship` skill's Stage
  4 moved-head rule (`.agents/skills/sd-ship/SKILL.md:179-186`) recomputes
  completion-mode receipts with base equal to the current head — the empty
  delta activates the post-archive-review-successor recovery — so a
  post-finalization fix does not strand an **eligible** completion-mode
  successor. That recovery is itself bounded (anchor, history-size, linearity,
  and path constraints — `scripts/sd-ai-command-pack-review-preflight.mjs:1245-1351`, `:1875-1969`) and
  can fail on an ineligible one. Operator-observed on run c441624d (PRs #187
  and #188, 2026-08-09): both completion-mode recomputations validated after
  post-finalization movement; the validator output was not retained in the
  journal, so this is an observation, not archived evidence. Planning mode
  alone re-runs the captured base against the new head, which is the shape
  that fails when the fix touches an authored path.
- Sibling of `08-06-work-loop-shipped-sha-after-branch-delete`: both are cases
  where a documented call shape cannot be satisfied against the state the
  preceding stage actually leaves behind.
- Lightweight enough to stay PRD-only unless the upstream route is chosen,
  which would warrant a `design.md` and an `implement.md` together — the
  contract at `.trellis/workflow.md:164` requires both for a complex task.

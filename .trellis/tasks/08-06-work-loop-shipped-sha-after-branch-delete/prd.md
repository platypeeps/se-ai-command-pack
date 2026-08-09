# Work-loop reconcile cannot record lastShippedSha after housekeeping deletes the merged branch

## Goal

Let the autonomous work loop record its final shipped feature SHA at the merge
boundary that `sd-housekeeping` actually produces, instead of forcing the
operator to recreate a deleted branch ref to get past a validation dead-end.

## Problem

`sd-work-backlog` instructs the controller: "When housekeeping returns a
verified clean default branch and merge HEAD, record `branch`, `head`, and the
final shipped feature SHA before transitioning to `followups`." By the time
housekeeping returns it has already deleted the merged feature branch — that
deletion is step 8 of its own task list. Two validations in
`scripts/sd-ai-command-pack-work-loop.py` then contradict each other:

- around lines 1892-1900, a branch change to the base branch is allowed only at
  a "verified merge boundary", which **requires** `lastShippedSha` in the same
  call; and
- around lines 1981-2006, when the branch changes the ancestry check resolves
  the tip from `_branch_commit(remembered_branch)` — the deleted feature branch,
  so `None` — and falls back to `remembered_head`, the pre-finalization head.
  The real shipped SHA is not an ancestor of that fallback tip, so the call
  fails with `lastShippedSha evidence must belong to the shipped branch`.

Passing the feature branch instead fails a third check,
`branch evidence is not a local Git branch: <branch>`, because the ref is gone.

Every ordering fails:

| `--branch` | `--head` | `--last-shipped-sha` | Result |
|---|---|---|---|
| `main` | merge commit | shipped SHA | `must belong to the shipped branch` |
| feature branch | shipped SHA | shipped SHA | `not a local Git branch` |
| `main` | merge commit | omitted | `may change only to the base branch at a verified merge boundary` |

Observed on run `17ab8b2853724fb481696ba6d4dcc057`, iteration 2, PR #153. Each
rejected attempt increments the context epoch and drives `contextHealth` to
`red`, which by the controller's own rules is a stop-or-park condition — so a
fully merged, successful iteration reports a red run.

## Constraint: every implementation surface is vendored

Under the ownership lookup in `.trellis/spec/backend/quality-guidelines.md`
("Vendored-Artifact Ownership And Upstream Route"), all three surfaces this
task would change are Registry B (`.sd-ai-command-pack/manifest.json`)
entries: `scripts/sd-ai-command-pack-work-loop.py` (`install: "always"`),
`.agents/skills/sd-work-backlog/SKILL.md` (`install: "always"`), and
`.claude/skills/sd-work-backlog/SKILL.md` (no `install` key =
`if-anchor-exists`) — all pack-vendored, none editable locally. That
section's disposition rule applies: an upstream PR needs explicit per-PR
approval (excluded from run-level authority), in-place vendored edits are
forbidden, and local-only is a legitimate terminal record carrying the
four-field record format defined there.

## Disposition

Execution route (chosen at planning, executed by this task's implementation):
the local-only route plus an upstream relay, per the recorded guidance. The
filled four-field record lives in **both** places the guidance requires — this
section (below, filled at implementation) and the guidance section itself:

- Record the four-field local-only record (owning pack, file, behaviour, "no
  upstream PR was opened") in `.trellis/spec/backend/quality-guidelines.md`,
  together with the operator procedure that works today: the two-step
  merge-boundary evidence sequence reproduced under Notes.
- File the upstream relay as an issue against `platypeeps/sd-ai-command-pack`
  (relay precedent: #397, #398, #399), carrying both gaps below and the
  reproduction evidence. An issue is a relay, not a pull request; the
  upstream *code change* remains approval-gated and is not made by this task.
- The Requirements and Acceptance Criteria sections below are preserved as
  the substance of the upstream proposal — they specify what the helper fix
  must do, and are verifiable only upstream. The locally verifiable outcomes
  are in "Local acceptance criteria" below.

Filled four-field record (2026-08-09):

1. **Owning pack**: sd-ai-command-pack.
2. **File**: `scripts/sd-ai-command-pack-work-loop.py` (`install: "always"`);
   documented call shape in `.agents/skills/sd-work-backlog/SKILL.md`
   (`install: "always"`) and `.claude/skills/sd-work-backlog/SKILL.md`
   (default mode, `if-anchor-exists`).
3. **Behaviour**: one-shot merge-boundary evidence rejected after
   housekeeping deletes the merged branch (stale fallback tip); no legal
   `selected -> inventory` transition for the documented pre-mutation skip.
4. **Upstream**: relayed as platypeeps/sd-ai-command-pack#404 (issue). No
   upstream PR was opened; a PR needs explicit per-PR approval. The relay
   batch also filed platypeeps/sd-ai-command-pack#405 for the 08-07 relay
   log's unfiled sd-review stale-disposition candidate.

## Local acceptance criteria

- [x] The filled four-field local-only record for this defect exists in
      **both** required places — this PRD's Disposition section and
      `.trellis/spec/backend/quality-guidelines.md` — following the recorded
      format, and the guidance copy includes the two-step evidence workaround
      as the operator procedure, naming the exact subcommand (`evidence`).
- [x] An upstream relay issue exists on `platypeeps/sd-ai-command-pack`
      carrying both gaps (merge-boundary evidence and the missing
      pre-mutation skip) with the reproduction evidence, and its number is
      recorded in this PRD.
- [x] The unfiled sd-review stale-disposition candidate from the 08-07 relay
      log ("route with the next relay batch") is filed in the same relay
      batch, and its issue number is recorded here.
- [x] No vendored file is modified.

## Workaround used

Recreate the deleted branch at the merge commit's second parent
(`git rev-list --parents -n1 <merge>`), reconcile twice — once with the feature
branch at the shipped SHA, once advancing to `main` at the merge commit — then
delete the temporary ref. The ref points at already-merged history so it invents
no evidence, but needing it is the defect: the controller's documented sequence
should work against the state housekeeping actually leaves behind.

## Requirements (upstream proposal substance — not locally verifiable)

- Reconcile must accept the merge boundary using evidence that survives branch
  deletion. The merge commit's second parent is the shipped feature tip and is
  reachable from the base branch, so ancestry is provable without the ref.
- A recorded branch that no longer exists locally must not by itself be an error
  at a proven merge boundary; it is the expected post-housekeeping state.
- A green reconciliation must clear red reasons accumulated from earlier
  rejected calls in the same run, so operator input errors do not permanently
  mark a successful iteration red.
- The controller's documented call shape in `sd-work-backlog` and the helper's
  validation must agree. If the helper keeps requiring two calls, the skill has
  to say so.

## Acceptance Criteria (upstream proposal substance — not locally verifiable)

- [ ] A single `reconcile --verified-live-advance` call carrying the base
      branch, the merge commit, and the shipped feature SHA succeeds against a
      repository whose feature branch has already been deleted.
- [ ] The rejected orderings above produce one actionable diagnostic naming the
      missing evidence instead of three mutually exclusive errors.
- [ ] A green reconciliation clears stale red reasons accumulated from earlier
      rejected calls in the same run.
- [ ] Regression coverage pins the post-housekeeping merge boundary: deleted
      feature ref, merge commit on the base branch, shipped SHA as the merge
      commit's second parent.
- [ ] `sd-work-backlog` step 3's wording matches the helper's accepted call
      shape.

## Second gap: no sanctioned skip from `selected`

Same run, same session. `sd-work-backlog` says "`skip current` is allowed only
before mutation", but `LEGAL_TRANSITIONS` (around line 146) gives `selected`
only `{planning, implementing, checkpoint, stopped}`. There is no route back to
`inventory` and no route to `complete`, so `result --outcome skipped` fails with
`illegal work-loop transition: selected -> complete`. Writing a checkpoint does
not help: the overlay keeps `resumePhase: selected` and leaves the phase at
`selected`, and `checkpoint`'s own outbound set is only reachable once the phase
is literally `checkpoint`.

The trigger is ordinary: ranking selects a task whose PRD, read after selection,
disqualifies it. Here it was `07-25-agent-artifacts`, a parent task whose own PRD
says it "has no direct implementation work and must not be started". Nothing in
the ranked candidate list exposes that — it is prose inside the PRD body — so a
correct ranking can still produce a selection that must be abandoned before any
mutation, which is precisely the case the skill's `skip current` control names.

The only exits are to walk the full phase path with no work, fabricating
`implementing`/`validating`/`shipping` evidence that never happened, or to stop
the run under a stop reason that is not true.

### Additional requirements

- Provide a sanctioned pre-mutation skip: either `selected -> inventory` as a
  legal transition guarded by "no branch, head, or PR evidence recorded", or a
  `result --outcome skipped` path valid from `selected`.
- The skip must record the skipped task and its reason in the run's counters and
  decisions, so the final report can list it. It must not consume an iteration
  that produced no work, or it must state clearly that it does.
- `sd-work-backlog`'s `skip current` wording and the helper's legal transitions
  must agree.

### Additional acceptance criteria

- [ ] `skip current` from `selected` with no recorded branch/head/PR evidence
      succeeds and returns the run to `inventory`.
- [ ] The same call fails closed once branch, head, or PR evidence exists.
- [ ] The skipped task and reason appear in the run's decisions and counters.
- [ ] Regression coverage pins both the allowed and the refused case.

## Out of scope

- Changing when `sd-housekeeping` deletes the merged branch.
- Extending `--recover-stale-lock` to `reconcile`. The flag is implemented on
  `start` (line 2726) and `reconcile-terminal` (line 2782); only `reconcile`
  lacks it, and no observed failure in this run needed it there. An earlier
  revision of this PRD claimed the helper did not implement the flag at all —
  that was generalized from one `reconcile --help` and is wrong.
- Broader ledger schema changes.

## Notes

- Lightweight enough to stay PRD-only until design work proves otherwise, at
  which point `design.md` and `implement.md` are both required
  (`.trellis/workflow.md:164`).
- 2026-08-09 (run 548ccf3e, iteration 3, PR #186): reproduced. The one-shot
  merge-boundary evidence call failed twice — first "lastShippedSha evidence
  must belong to the shipped branch" (deleted branch resolves to None, so the
  ancestor check falls back to the remembered head, which was stale at the
  pre-finalization commit), then "branch evidence may change only to the base
  branch at a verified merge boundary" when the shipped SHA was omitted (the
  branch flip requires it, `sd-ai-command-pack-work-loop.py:1905-1914`).
  Workaround that succeeded — both steps are `evidence` subcommand calls, not
  `reconcile`: first `evidence --head <final feature commit>` alone
  (same-phase descendant update), then `evidence --branch main --head <merge>
  --base-branch main --pr-number N --last-shipped-sha <final feature commit>`
  — the fallback tip then resolves to the freshly remembered head and the
  ancestor check passes. Re-confirmed 2026-08-09 (run c441624d, iteration 1,
  PR #187): the same two `evidence` calls executed in that order succeed
  first-try from a green ledger. This procedure is for the green/amber path; a
  run already holding a blocked recovery checkpoint from rejected `reconcile`
  calls must instead satisfy reconcile's complete-recovery-evidence
  requirement (partial `evidence` updates do not clear a recovery
  checkpoint). The fix should make the merge-boundary call work one-shot; the
  two-step dance is undocumented order dependence.

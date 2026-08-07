# task.py create records the current branch as base_branch

## Goal

Stop a newly created task from inheriting a short-lived feature branch as its
PR target, so `base_branch` still names a live branch by the time the task is
actually worked.

## Problem

`task.py create` records whatever branch happens to be checked out:

```python
# Record current branch as base_branch (PR target)
_, branch_out, _ = run_git(["branch", "--show-current"], cwd=repo_root)
current_branch = branch_out.strip() or "main"
```

(`.trellis/scripts/common/task_store.py:296-298`), written straight into the
new task at `:325`:

```python
"base_branch": current_branch,
```

The `or "main"` fallback covers only an empty branch name — a detached HEAD. It
never covers the ordinary case, which is the defective one.

The comment says this is deliberate, and for the flow it was written for it is
correct: a task created while stacking on another branch does target that
branch. The dominant flow in this repository is the opposite. Follow-up tasks
are created *during* a ship cycle — while a feature branch is checked out,
usually from a review finding — for work that will be done later, on its own
branch, targeting the default branch. That source branch is deleted at merge,
minutes to hours after the task is written.

Nothing detects the result. `base_branch` is not validated at `create`, at
`start`, or at PR creation, and no command warns that it names a branch that no
longer exists. The task carries a dead ref until someone reads the JSON.

### Observed

Two tasks were found holding `"base_branch": "task/07-28-enhance-skills-workflow"`,
a branch deleted when its PR merged: `08-06-session-first-skill-review` and
`08-06-ship-gate-ordering-docs`. Both were hand-corrected to `main`.

Two more were created wrong during the same session —
`08-06-prism-rules-lane-divergence` and `08-06-sd-review-local-rebuttal-gap` —
each created from the feature branch of the PR whose review surfaced it, each
corrected immediately. The defect reproduces every time a follow-up task is
created the way follow-up tasks are supposed to be created.

### Why it is worth fixing rather than remembering

The correction is invisible unless someone already knows to look. A wrong
`base_branch` produces no error at creation, no error at `start`, and no error
at PR time — the value is simply carried. The cost lands on whoever works the
task later, and a wrong PR target is then discovered after the PR exists rather
than before.

The failure is also silent in the direction that matters: inheriting a
*surviving* branch is indistinguishable from a deliberate stacked base, so no
later reader can tell an intended base from an inherited one.

## Constraint: the file is vendored

`.trellis/scripts/common/task_store.py` is tracked in
`.trellis/.template-hashes.json` and is upstream-Trellis, not repo-owned.
Changing it is an **upstream** pull request needing its own approval, which the
autonomous run-level authority explicitly excludes. Only this repository's
`.trellis/spec/` guidance is editable locally, so the local-only route must
stand on its own.

## Requirements

- Decide and record a disposition:
  - **Local-only.** Document in `.trellis/spec/backend/quality-guidelines.md`
    that `task.py create` inherits the current branch, that a task created from
    a feature branch must have its `base_branch` corrected before that branch is
    deleted, and give the exact correction command.
  - **Upstream.** Propose a change to `task_store.py`. Any proposal must keep
    the deliberate stacked-base case reachable — an explicit `--base-branch`
    flag, or a default of the repository default branch with the current
    behaviour available on request. Silently swapping the default with no opt-in
    is not acceptable.
- Whatever the disposition, the corrected value must be reachable without a
  hand edit of `task.json`. `task.py set-base-branch <dir> <branch>` already
  exists and is the sanctioned route; name it explicitly.
- Do not change how `base_branch` is consumed at PR creation, and do not touch
  the detached-HEAD `or "main"` fallback, which is independently correct.
- Any upstream proposal must state what happens to existing tasks already
  holding a dead `base_branch`. A change that only fixes new tasks leaves the
  existing ones untouched and must say so rather than implying a sweep.

## Acceptance Criteria

- [ ] The disposition (local-only or upstream) is recorded with its reasoning,
      including whether upstream approval was sought.
- [ ] The written guidance names the exact source line (`task_store.py:325`)
      and the exact correction command, so a reader can confirm the behaviour
      without re-deriving it from the script.
- [ ] The guidance states *when* the correction must happen — before the source
      branch is deleted — not merely that it should happen eventually.
- [ ] A sweep of active tasks confirms no remaining `base_branch` names a branch
      absent from `git branch -a`, or lists each exception with its reason.
- [ ] If the upstream route is chosen, the proposal preserves an explicit way to
      request the current stacked-base behaviour, and the local documentation
      lands first without depending on the upstream change merging.

## Out of scope

- The trailing-newline defect in the same script family. That is
  `08-06-task-json-trailing-newline`; the two share a file tree and nothing else.
- Validating `base_branch` at `task.py start` or at PR creation. Detection is a
  larger change than defaulting and needs its own task.
- Any change to branch naming, the ship chain's branch handling, or Trellis
  archive behaviour.

## Notes

- Four confirmed occurrences: `08-06-session-first-skill-review` and
  `08-06-ship-gate-ordering-docs` (found stale, corrected), plus
  `08-06-prism-rules-lane-divergence` and `08-06-sd-review-local-rebuttal-gap`
  (created wrong, corrected immediately).
- Sixth instance of the vendored-artifact pattern, alongside
  `08-06-sd-review-local-rebuttal-gap`, `08-06-prism-rules-lane-divergence`,
  `08-06-watch-coordinator-infra-classification`,
  `08-06-finalization-ordering-trap`, and
  `08-06-work-loop-shipped-sha-after-branch-delete`. The pattern now warrants a
  task of its own rather than a note repeated in each PRD.
- Lightweight enough to stay PRD-only unless the upstream route is chosen.

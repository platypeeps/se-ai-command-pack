# task.py create records the current branch as base_branch

## Goal

Stop a newly created task from recording a short-lived feature branch in
`base_branch`, so the field still names a live branch by the time the task is
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

### What actually consumes the field — and what does not

The impact must be stated accurately, because the obvious assumption is wrong:

- **`sd-create-pr` never reads it.** It resolves the PR base independently:
  `SD_AI_COMMAND_PACK_CREATE_PR_BASE`, then `gh repo view --json
  defaultBranchRef`, then the local `refs/remotes/origin/HEAD`
  (`.agents/skills/sd-create-pr/SKILL.md:112-124`), and passes that value to
  `gh pr create --base "$BASE_BRANCH"` (`:273`). A dead `base_branch` in
  `task.json` therefore does **not** produce a wrong PR target.
- **`sd-finish-work` reads it as an inequality guard only.** When it sets a
  task's `branch`, it stops if the resolved working branch equals the record's
  `base_branch` (`.agents/skills/sd-finish-work/SKILL.md:61-66`). A stale value
  naming a deleted branch never equals the live one, so the guard passes — the
  wrong value degrades a safety check into a no-op rather than tripping it.
- **The review preflight checks the referent for child tasks, not just the
  shape** — but permissively. Beyond the non-empty-string check at
  `scripts/sd-ai-command-pack-review-preflight.mjs:3217`,
  `validateTrellisPlanningBaseInheritance` (`:3223-3242`) requires a child's
  `base_branch` to equal its parent's `base_branch` *or the parent's active
  branch*, and `:3299-3309` requires `branch` to differ from `base_branch`.
  Inheriting the parent's active branch is therefore explicitly allowed, so a
  child created mid-cycle usually passes. It fails once the parent is no longer
  active — verified by direct evaluation: the same record passes with an active
  parent and fails after the parent moves to `completed`.

So the defect is a stored dead reference plus a silently weakened guard, not a
mis-targeted pull request. The one place it becomes a hard gate failure is a
child task whose parent has since completed. That is a smaller blast radius than
"wrong PR target" implies but not a cosmetic one, and the disposition below
should be priced against this, not against an assumed PR-targeting failure.

### Observed

Two tasks were found holding `"base_branch": "task/07-28-enhance-skills-workflow"`,
a branch deleted when its PR merged: `08-06-session-first-skill-review` and
`08-06-ship-gate-ordering-docs`. Both were hand-corrected to `main`.

Two more were created wrong during the same session —
`08-06-prism-rules-lane-divergence` and `08-06-sd-review-local-rebuttal-gap` —
each created from the feature branch of the PR whose review surfaced it, each
corrected immediately. The defect reproduces every time a follow-up task is
created the way follow-up tasks are supposed to be created.

A fifth occurrence on 2026-08-07 is the one that shows the cost, because it was
not caught at creation. `08-07-review-py-local-fork` was created from
`task/08-07-review-py-local-fork`, recorded that branch, and reached PR #166
still holding it, where a paid Copilot round flagged it; corrected in `9f16829`.
No deterministic check objected, and the reason is visible in the citations
above: a freshly created task has `branch: null`, so the inequality at
`scripts/sd-ai-command-pack-review-preflight.mjs:3299-3309` is guarded off
before it can compare, and `validateTrellisPlanningBaseInheritance` constrains
child tasks only. Both facts were confirmed by reading the record as created and
the guard itself, not inferred.

The same session filed a task in the source pack repository from that
repository's own feature branch, and it reached that repository's pull request
with the same wrong value and was caught the same way. The behaviour therefore
follows the vendored script rather than this checkout. That repository tracks its
own occurrence in its own task; do not restate its record or its counts here.

A sweep on 2026-08-07 found all 25 active task records naming `main`, so this
repository currently stores no dead reference. That is the product of five hand
corrections, not evidence the defect is absent — and it is worth recording
because the acceptance criterion below asks for exactly this sweep, which will
pass on a repository that is still creating the value wrongly every time.

### Why it is worth fixing rather than remembering

The correction is invisible unless someone already knows to look. A wrong
`base_branch` produces no error at creation, no error at `start`, and no error
at PR time — the value is simply carried. The cost lands on whoever works the
task later: the record asserts a PR target that no tool honours, and the one
consumer that reads it silently loses the check it was meant to perform.

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
- [ ] The record states plainly that the local-only route does not satisfy the
      Goal, and names which criteria it can satisfy anyway. This matters because
      every criterion above except the upstream one is satisfiable by
      documentation alone: the sweep passes on a repository that still records the
      wrong value on every `create`, so a green sweep is not evidence the seeding
      defect is fixed. Choosing local-only is legitimate — the file is vendored —
      but it must be recorded as a mitigation, not as a fix.
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

- Five confirmed occurrences: `08-06-session-first-skill-review` and
  `08-06-ship-gate-ordering-docs` (found stale, corrected), plus
  `08-06-prism-rules-lane-divergence` and `08-06-sd-review-local-rebuttal-gap`
  (created wrong, corrected immediately), plus `08-07-review-py-local-fork`
  (created wrong, reached PR #166, corrected only after a paid review round).
- One of the vendored-artifact instances enumerated in the table in
  `08-07-vendored-artifact-upstream-route/prd.md`, which is the canonical list.
  Do not restate a running count or a membership list here; both drifted once
  already. `08-06-work-loop-shipped-sha-after-branch-delete` was previously
  listed as a member and is not one — it carries no vendored-ownership
  constraint section, and it is ordinary unblocked planning work. (The recorded
  operator deferral belongs to `08-06-watch-coordinator-infra-classification`,
  not to it.)
- Lightweight enough to stay PRD-only unless the upstream route is chosen,
  which would warrant a `design.md` and an `implement.md` together — the
  contract at `.trellis/workflow.md:164` requires both for a complex task.

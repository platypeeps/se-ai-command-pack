---
title: task.py create records the current branch as base_branch
status: done
created: 2026-08-06
branch: task/08-06-task-create-base-branch-default
---
# task.py create records the current branch as base_branch

## Goal

Record the current state of the `base_branch` seeding defect accurately and
close the local gap it leaves: the behavioural fix already shipped upstream
(Trellis v0.6.8, below) but is not installed here, the installed pack's
preflight now hard-gates a wrong root value with a diagnostic that names a
command absent from the installed Trellis version, and no local guidance
explains any of it. This
task delivers the guidance, the upstream-status record, and the relay of the
remaining cross-owner incompatibility — not the seeding change itself, which
is adopted by a Trellis upgrade, not by this task.

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

The `or "main"` fallback fires on any empty output — a detached HEAD, but
also a failed `git` invocation, since the caller discards the return code —
and hardcodes a name that is not universally the repository default. It never
covers the ordinary case, which is the defective one. It is a legacy fallback
and out of scope here, not "independently correct".

**Upstream status (verified 2026-08-09).** This exact defect was reported as
[mindfold-ai/Trellis#399](https://github.com/mindfold-ai/Trellis/issues/399)
(closed), fixed by merged
[PR #448](https://github.com/mindfold-ai/Trellis/pull/448) (2026-07-20), and
released in **v0.6.8**: `create` resolves the repository default branch
(`origin/HEAD`) instead of inheriting the checkout, and an explicit
`--base-branch` flag preserves the deliberate stacked-base case. This
checkout runs Trellis `0.6.7` (`.trellis/.version`), so the fix exists but
is not installed. Adopting it is a Trellis upgrade — an operator-controlled
vendored refresh, not this task's work.

The comment says this is deliberate, and for the flow it was written for it is
correct: a task created while stacking on another branch does target that
branch. The dominant flow in this repository is the opposite. Follow-up tasks
are created *during* a ship cycle — while a feature branch is checked out,
usually from a review finding — for work that will be done later, on its own
branch, targeting the default branch. That source branch is deleted at merge,
minutes to hours after the task is written.

At `create` and `start`, nothing detects the result. Since the current pack
version, however, the review preflight **does** hard-gate the value at PR
time for changed root-task records:
`validateTrellisRootTaskBaseBranch`
(`scripts/sd-ai-command-pack-review-preflight.mjs:3331-3354`, wired at
`:3159-3188`) requires a root task's `base_branch` to equal the repository
default branch or carry a `meta.base_branch_exemption` reason — and
`sd-create-pr` mandates that preflight before publication
(`.agents/skills/sd-create-pr/SKILL.md:203-220`). Verified by direct
evaluation: a root record with `base_branch: "task/feature"` fails with
`root task base_branch "task/feature" must equal ... "main"`. So a wrongly
seeded root task created mid-cycle is now caught at the next PR that touches
its record — later than creation, but no longer silent. The gate has its own
defect, below.

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
- **The review preflight checks the referent, with different rules for root
  and child tasks.** Root tasks: default-branch-or-exemption, as above
  (`:3331-3354`). Child tasks: `validateTrellisPlanningBaseInheritance`
  (`:3294-3328`) requires a child's `base_branch` to equal its parent's
  `base_branch` *or the parent's active branch* — permissive while the
  parent is active, failing once the parent completes (verified by direct
  evaluation both ways). The shape checks — non-empty string at
  `:3409-3410`, `branch` differing from `base_branch` at `:3412-3420` — are
  guarded off for a fresh task whose `branch` is `null`.
- **The root gate's escape hatch is unreachable without a hand edit.** Its
  diagnostic recommends
  `python3 ./.trellis/scripts/task.py set-meta <task-dir>
  base_branch_exemption "<reason>"` (`:3353`), but no `set-meta` command
  exists in the installed Trellis `0.6.7` `task.py` — nor in upstream
  `v0.6.8` (both verified by direct search). A deliberate stacked root base
  therefore cannot pass this repository's PR gate through any sanctioned
  command: the pack validator (sd-ai-command-pack-owned) and the Trellis CLI
  (upstream-Trellis-owned) disagree across the ownership boundary **at the
  installed versions**: Trellis shipped `set-meta` in v0.6.9 (verified
  present through v0.6.14 and `main`), so the incompatibility is a
  minimum-version gap — the pack diagnostic assumes a Trellis ≥ v0.6.9
  command without stating or checking that floor, and the installed 0.6.7
  (and v0.6.8) cannot execute it. That version-conditioned gap is the proper
  subject of this task's relay.

So the defect is a stored dead reference plus a silently weakened guard, not a
mis-targeted pull request. It becomes a hard gate failure in two places: a
changed root-task record whose `base_branch` is not the repository default
(`:3331-3354`), and a child task whose parent has since completed. That is a
smaller blast radius than
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
No deterministic check objected **at the time**: a freshly created task has
`branch: null`, so the branch-vs-base inequality (now at
`scripts/sd-ai-command-pack-review-preflight.mjs:3412-3420`) is guarded off
before it can compare, and `validateTrellisPlanningBaseInheritance` (now
`:3294-3328`) constrains child tasks only. Both facts were confirmed by
reading the record as created and the guard itself, not inferred. The root
default-branch gate (`:3331-3354`) did not exist then; today it would catch
this occurrence at PR time.

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
`base_branch` produces no error at creation and no error at `start` — the
value is carried until the next PR whose preflight inspects the changed
record, where the root gate (`:3331-3354`) now fails it. Between creation
and that PR the cost still lands on whoever works the task: the record
asserts a PR target that no tool honours, and the one consumer that reads it
silently loses the check it was meant to perform.

The failure is also silent in the direction that matters: inheriting a
*surviving* branch is indistinguishable from a deliberate stacked base, so no
later reader can tell an intended base from an inherited one.

## Constraint: the file is vendored

`.trellis/scripts/common/task_store.py` classifies as a Registry A
(`.trellis/.template-hashes.json`) entry under the ownership lookup in
`.trellis/spec/backend/quality-guidelines.md` ("Vendored-Artifact Ownership
And Upstream Route"): upstream-Trellis vendored, not editable locally. That
section's disposition rule applies — an upstream PR needs explicit per-PR
approval (excluded from run-level authority), local-only is a legitimate
terminal record, and the local-only route must carry the four-field record
format defined there.

## Requirements

- Record the disposition and the upstream status accurately. The seeding
  defect is **already fixed upstream** (v0.6.8); do not file a duplicate
  seeding issue, and do not propose a `task_store.py` change that upstream
  has already shipped. The open work is local guidance, the upgrade-adoption
  record, and the cross-owner exemption incompatibility relay.
- The corrected value must be reachable without a hand edit of `task.json`.
  `task.py set-base-branch <dir> <branch>` already exists and is the
  sanctioned route; name it explicitly.
- Do not change how `base_branch` is consumed at PR creation, and do not
  touch the `or "main"` fallback — a legacy fallback, out of scope (not
  "independently correct": it also fires on discarded `git` failure and
  hardcodes a name that may not be the default).
- The guidance must state what happens to existing wrongly seeded records
  under the v0.6.8 fix: nothing — it changes seeding for new tasks only; the
  sweep plus `set-base-branch` remains the route for stored values.

## Disposition

**Local-only guidance plus upstream-status record, with one relay issue for
the remaining cross-owner incompatibility.** Chosen at planning (revised
after adversarial review established the upstream fix had already shipped),
executed by this task's implementation:

- Document in `.trellis/spec/backend/quality-guidelines.md`, in one
  subsection: `task.py create` under the installed Trellis `0.6.7` records
  the checked-out branch as `base_branch`
  (`.trellis/scripts/common/task_store.py:296-298`, written at `:325`);
  upstream fixed this in v0.6.8 (Trellis#399 / PR #448 — default-branch
  resolution with an explicit `--base-branch` opt-in for stacking) and the
  fix arrives here only through a Trellis upgrade, which changes seeding for
  new tasks only; until then the correction is
  `python3 ./.trellis/scripts/task.py set-base-branch <dir> <branch>` —
  never a hand edit — applied **before the source branch is deleted**, i.e.
  within the ship cycle that created the task; detection today is the root
  preflight gate (`validateTrellisRootTaskBaseBranch`, `:3331-3354`) at the
  next PR touching the record, with `create`/`start` still silent and the
  child rules permissive while a parent is active; what the field does and
  does not affect (`sd-create-pr` resolves the PR base independently;
  `sd-finish-work` uses it as an inequality guard that a stale value
  silently degrades to a no-op); and the gate's version-conditioned defect —
  the `meta.base_branch_exemption` escape hatch whose recommended `set-meta`
  command shipped in Trellis v0.6.9 and is absent from the installed 0.6.7
  (and from v0.6.8), making a deliberate stacked root base unpassable
  without a hand edit until the upgrade lands.
- State plainly that the guidance route is a **mitigation plus adoption
  record, not the fix**: the fix is a Trellis upgrade (v0.6.8 for the
  seeding default; ≥ v0.6.9 for the reachable exemption command), an
  operator-controlled vendored refresh outside this task; a green sweep of
  stored values is not evidence the seeding defect is gone from this
  checkout.
- Record the complete four-field local-only record — all four fields — in
  **both** this PRD's Disposition and the guidance section. The fourth field
  is the explicit statement that **no upstream PR was opened**, with the
  relay issue URL appended to it.
- File one relay **issue** on platypeeps/sd-ai-command-pack — the correct
  tracker, because the diagnostic is owned by the pack's validator, not by
  Trellis — reframed as a **minimum-version gap**, whose body contains each
  contract element by name: the `validateTrellisRootTaskBaseBranch`
  diagnostic recommends `task.py set-meta` (`review-preflight.mjs:3353`);
  `set-meta` shipped in Trellis v0.6.9 and exists through v0.6.14 and
  `main`, but not in v0.6.7 or v0.6.8 (all verified by direct search), and
  the pack neither states nor checks that version floor — so on a
  pre-v0.6.9 install the `meta.base_branch_exemption` escape hatch is
  unreachable through any sanctioned command and an intentional stacked
  root base cannot pass the PR gate without hand-editing `task.json`;
  proposed fix shapes (declare and check a minimum Trellis version for the
  recommended command, degrade the diagnostic to name the version
  requirement on older installs, or have the pack ship an equivalent
  helper), with upgrading the consumer to Trellis ≥ v0.6.9 named as the
  adoption-side resolution; and the upstream-fixed status of the original
  seeding defect (v0.6.8) plus the `set-meta` availability (v0.6.9) so the
  issue is not misread as a duplicate of Trellis#399. Do **not** file a
  seeding-defect issue on the Trellis tracker — Trellis#399 already covered
  it and is closed as fixed. The upstream PR itself is not sought.
  **Filed:** <https://github.com/platypeeps/sd-ai-command-pack/issues/410>.

Four-field local-only record:

- Owning pack: upstream Trellis for the seeding surface
  (`.trellis/scripts/common/task_store.py`, Registry A) and
  sd-ai-command-pack for the gate diagnostic
  (`scripts/sd-ai-command-pack-review-preflight.mjs`, Registry B,
  `kind: script`, `install: "always"`).
- Files: as above, each with its registry entry.
- Behaviour: pre-v0.6.8 `create` seeds `base_branch` from the checkout, and
  the pack's root-gate diagnostic recommends a Trellis ≥ v0.6.9 command
  without stating or checking that floor, leaving the exemption unreachable
  on this install.
- No upstream PR was opened; the seeding defect was already fixed upstream
  (Trellis v0.6.8 via #399/#448 — no duplicate filed); relay issue for the
  version-floor gap:
  <https://github.com/platypeeps/sd-ai-command-pack/issues/410>.

## Acceptance Criteria

- [x] The disposition is recorded with its reasoning, including the verified
      upstream status: seeding fixed in Trellis v0.6.8 (#399 / PR #448),
      installed version 0.6.7, adoption is a Trellis upgrade outside this
      task, and no duplicate seeding issue was filed on the Trellis tracker.
- [x] The written guidance names the exact source line (`task_store.py:325`
      in the installed 0.6.7) and the exact correction command
      (`task.py set-base-branch`), so a reader can confirm the behaviour
      without re-deriving it from the script.
- [x] The guidance states *when* the correction must happen — before the source
      branch is deleted — not merely that it should happen eventually.
- [x] A sweep of active tasks confirms every `base_branch` names the
      repository default branch or carries a documented
      stacked-base/exemption reason, after `git fetch --prune` (so cached
      remote-tracking refs cannot vouch for deleted branches), normalizing
      `main` / `origin/main` / `remotes/origin/main` to one form; each
      exception is listed with its reason. Liveness against unpruned
      `git branch -a` is explicitly not the check.
- [x] The record states plainly that the guidance is a mitigation plus
      adoption record, not the fix: this checkout still seeds wrongly on
      every mid-cycle `create` until the v0.6.8 upgrade lands, so a green
      sweep is not evidence the seeding defect is gone.
- [x] The relay issue exists on platypeeps/sd-ai-command-pack, its body
      contains each contract element named in the Disposition (the
      minimum-version gap: `set-meta` recommended at
      `review-preflight.mjs:3353`, shipped in Trellis v0.6.9, absent from
      the installed 0.6.7 and from v0.6.8, no version floor stated or
      checked; proposed fix shapes including the ≥ v0.6.9 upgrade as the
      adoption-side resolution; the tracker-choice rationale — the
      diagnostic is pack-owned; and the v0.6.8/v0.6.9 status notes
      distinguishing it from Trellis#399), verified by reading the issue at
      its URL, and the URL is recorded in the complete four-field record in
      **both** this PRD's Disposition and the guidance section.
- [x] The guidance's degradation and detection claims match the verified
      code: root-task PR-time gate at `:3331-3354` (wired `:3159-3188`),
      child inheritance at `:3294-3328`, shape checks at `:3409-3420`
      guarded off for `branch: null`, and `create`/`start` silent. No claim
      of "nothing detects" survives anywhere in the shipped guidance.

### Completion evidence

- Guidance subsection "task.py create seeds base_branch from the checkout:
  correct it before the source branch dies" added to
  `.trellis/spec/backend/quality-guidelines.md` with the installed-0.6.7
  behaviour (`task_store.py:296-298`/`:325`), the v0.6.8 upstream fix and
  upgrade-only adoption, the `set-base-branch` correction command and its
  before-branch-deletion deadline, detection facts (root gate `:3331-3354`
  wired `:3159-3188`, children `:3294-3328`, shape checks `:3409-3420`
  guarded for `branch: null`, `create`/`start` silent), field consumption,
  the version-conditioned `set-meta` trap (Trellis >= v0.6.9), the sweep
  check, and the four-field record naming relay #410.
- Relay issue filed and verified at
  <https://github.com/platypeeps/sd-ai-command-pack/issues/410>: body
  contains the diagnostic citation (`:3353`), the v0.6.9 floor absent from
  0.6.7/0.6.8, the unstated/unchecked floor, three fix shapes with the
  >= v0.6.9 upgrade as adoption-side resolution, the pack-owned tracker
  rationale, and status notes distinguishing it from Trellis#399. URL
  recorded in the four-field record in both this Disposition and the
  guidance section (`grep -c "issues/410"`: PRD 2, guidance 1).
- Sweep: after `git fetch --prune` (default resolved from
  `refs/remotes/origin/HEAD` = `main`), all 15 active `task.json`
  `base_branch` values normalize to `main`; zero undocumented exceptions.
- `make check`: `Ran 640 tests ... OK (skipped=1)`, `All checks passed!`
- Shipped as PR #191; Copilot round 1 finding (stale task.json
  description) fixed in 060d595, round 2 returned no new comments; one
  false prism trailing-newline finding rebutted with byte-level evidence
  (`tail -c 1` = `0a` at HEAD).

## Out of scope

- The trailing-newline defect in the same script family. That is
  `08-06-task-json-trailing-newline`; the two share a file tree and nothing else.
- Adding validation of `base_branch` at `task.py start`, or changing the
  existing PR-time root gate (`validateTrellisRootTaskBaseBranch`) beyond
  relaying its unreachable-exemption defect. Both surfaces are vendored.
- Any change to branch naming, the ship chain's branch handling, or Trellis
  archive behaviour.

## Notes

- Five confirmed occurrences: `08-06-session-first-skill-review` and
  `08-06-ship-gate-ordering-docs` (found stale, corrected), plus
  `08-06-prism-rules-lane-divergence` and `08-06-sd-review-local-rebuttal-gap`
  (created wrong, corrected immediately), plus `08-07-review-py-local-fork`
  (created wrong, reached PR #166, corrected only after a paid review round).
- One of the vendored-artifact instances enumerated in the table in
  `.trellis/tasks/archive/2026-08/08-07-vendored-artifact-upstream-route/prd.md`
  (archived 2026-08-09 after shipping the consolidation guidance as PR #187),
  which is the canonical list. Do not restate a running count or a membership
  list here; both drifted once already. `08-06-work-loop-shipped-sha-after-branch-delete` was previously
  listed as a member and is not one — it carries no vendored-ownership
  constraint section, and it is ordinary unblocked planning work. (The recorded
  operator deferral belongs to `08-06-watch-coordinator-infra-classification`,
  not to it.)
- Lightweight enough to stay PRD-only unless the upstream route is chosen,
  which would warrant a `design.md` and an `implement.md` together — the
  contract at `.trellis/workflow.md:164` requires both for a complex task.

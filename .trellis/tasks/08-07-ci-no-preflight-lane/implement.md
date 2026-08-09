# Consumer CI review-preflight lane — Implementation Plan

Execute after `task.py start`. One coherent PR plus up to two throwaway
draft PRs used only as demonstrations (the absence proof may instead reuse
the first post-merge dependabot/docs PR), and one small post-merge
bookkeeping commit
that records the demonstrations' PR numbers in the task record — the task
is not archived until that evidence is recorded, since the absence
demonstration can only exist after the implementing PR merges. The
disposition and its reasoning live in `design.md`; this plan sequences the
enforce route.

## Execution Order

1. **Add the job.** In `.github/workflows/tests.yml`, add the
   `review-preflight` job exactly as specified in design.md ("The job"):
   `checkout@v7` with `fetch-depth: 0` + `persist-credentials: false`,
   `setup-node@v7` with `node-version: "22"`, the fail-closed base guards,
   and the bare
   `SD_AI_COMMAND_PACK_REVIEW_PREFLIGHT_BASE_REF="$EVENT_BASE_SHA" node
   scripts/sd-ai-command-pack-review-preflight.mjs` invocation. No flags, no
   wrapper, no mode argument.
2. **Join the aggregate.** Add `review-preflight` to `ci-result.needs`.
   Reconcile with `08-08-ci-gate-fail-softs` per design.md's ordering rule:
   if `.github/scripts/aggregate-ci-result.py` exists by now, also add
   `review-preflight` to its `REQUIRED_LANES` and extend its unit test's
   synthetic payloads; if not, the inline `not in ("success", "skipped")`
   aggregate needs no change (the job is unconditional, so it cannot skip).
3. **Local sanity.** `make check` (workflow files are not linted by it, but
   the tree must stay green) and
   `python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/tests.yml'))"`
   or an equivalent parse check to catch YAML mistakes before pushing.

## Validation Plan

Ordered; the demonstrations are PRD acceptance criteria and must be real,
not asserted:

1. **Implementing PR goes green:** its own run shows the new
   `review-preflight` job passing and `ci-result` green with the extended
   `needs`. (This PR changes `.trellis/` task records, so it also exercises
   the Trellis validators on a real changed set.)
2. **Fail demonstration:** push a scratch branch that breaks one
   documentation path reference in a `prd.md` (e.g. cite a nonexistent
   file), open a **draft** PR, and capture the required context `ci-result`
   failing on it. The branch must carry the new workflow: cut it from the
   implementing branch pre-merge (a `pull_request` run uses the workflow
   file at the event's merge ref, `refs/pull/<n>/merge`, whose synthetic
   merge includes the head branch's workflow changes), or from `main`
   post-merge. Close the draft unmerged,
   delete the branch, and record the PR number in the task record.
3. **Absence demonstration:** a PR with no `.trellis/` change passes
   `ci-result`. This is necessarily post-merge evidence: the implementing
   PR changes `.trellis/`, and a pre-merge branch cut from `main` lacks the
   new workflow. After the implementing PR merges, open a trivial
   no-`.trellis` draft PR (or cite the first post-merge dependabot/docs PR
   if one lands first); record which was used and its number in the task
   record via the post-merge bookkeeping commit named in this plan's
   preamble, before the task is archived.
4. **Workflow-content proof:** quote the merged `tests.yml` lines showing
   the pinned Node version and the unmodified script invocation.
5. **Branch-protection agreement:** read `main` branch protection via
   `gh api repos/platypeeps/se-ai-command-pack/branches/main/protection`
   and confirm the required contexts are still exactly `["ci-result"]`.

## Documentation And Spec Updates

- None outside the task record. The PRD explicitly forbids landing the
  reasoning in `.trellis/spec/backend/quality-guidelines.md`; the
  disposition lives in this task's `design.md`, and the demonstrations'
  PR numbers are recorded in the task directory at completion.

## Review Notes

- The reviewer should diff the job against the source pack repository's
  lane only for the parts this design claims to inherit (pinned Node 22,
  explicit event base, fail-closed guards) — the omitted classifier and
  coverage machinery are deliberate, per design.md Boundaries.
- The `pack.review-scope` check will demand a Tooling/generated scope
  section in the PR body (workflow + task files); the
  `--prepare-tooling-body` helper handles it.
- Do not let review "simplify" the explicit base into the script's own
  discovery chain — the last-resort arbitrary-remote-ref fallback is the
  fail-open this lane exists to avoid.

## Rollback Points

- The change is one workflow job plus one `needs` entry; full rollback is
  reverting the PR. The required-context list never changes, so rollback
  cannot strand branch protection.
- If the lane misbehaves on a runner (e.g. upstream syntax passes Node 22
  locally but not in CI), the bounded fix is the one-line `node-version`
  bump; removing the job entirely requires reopening this task's
  disposition, not a quiet deletion.

## Follow-Ups

Explicitly outside this PR:

- Any bookkeeping/full classifier split or preflight coverage measurement
  (source pack's cost machinery; out of scope per PRD).
- Fixing whatever pre-existing record defect the new lane might surface on
  an unrelated PR — that is ordinary ship-loop work, filed when it occurs.
- The `08-08-ci-gate-fail-softs` aggregator reconciliation if that task
  implements after this one (its own implement.md steps 1 and 3 cover the
  reverse order).

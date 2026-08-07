# Watch coordinator cannot distinguish an infrastructure CI failure from a real one

## Goal

Let a run tell "the change broke a check" apart from "GitHub could not run the
check" at the point where `sd-ship` Stage 3 decides to stop, instead of
collapsing both into one outcome that invites the wrong response.

## Problem

Stage 3's coordinator ends in exactly one of four outcomes
(`.claude/skills/sd-ship/references/watch-coordinator.md:58-65`):

- `settled-green`
- `settled-blocked` — "checks completed but the probe reports blocking"
- `timed-out`
- `probe-failed`

There is no infrastructure category. A lane that never acquired a runner and a
lane whose tests genuinely failed both arrive as `settled-blocked`, usually
carrying `merge_state_not_clean`. The two demand opposite responses — one is
cleared by waiting and retrying, the other is never cleared by retrying — and
the outcome that must drive the decision does not encode which one happened.

Observed on PR #155 (2026-08-06). Four lanes failed at an identical `15m2s`
while the single lane that obtained a runner passed at `8m51s`; every failure
was a `Set up job` step erroring with `Service Unavailable` or
`Failed to resolve action download info`, so zero test code executed. The
coordinator reported the same `settled-blocked` it would report for a real red
suite. Diagnosis took several retries plus manual
`gh api repos/<owner>/<repo>/actions/jobs/<id>` inspection.

The cost is asymmetric and falls on the wrong side. Reading a real failure as
infrastructure wastes retries; reading infrastructure as a real failure invites
a run to "fix" code that was never executed.

## Constraint: the coordinator is not owned by this repository

`.claude/skills/sd-ship/references/watch-coordinator.md` is installed from the
sd-ai-command-pack — `.sd-ai-command-pack/manifest.json` maps it from that
pack's `templates/.agents/skills/...` source. An edit here is overwritten by the
next pack refresh. Any change to the coordinator's outcome vocabulary is
therefore an **upstream** change to sd-ai-command-pack and needs explicit
approval for that pull request. Only operator-facing guidance in this
repository's own `.trellis/spec/` is editable locally.

This constraint shapes the requirements: the local-only option must be viable
on its own, because the upstream option may not be authorized.

## Requirements

- Decide between two dispositions and record the reasoning:
  - **Local-only.** Document the discrimination procedure in
    `.trellis/spec/backend/quality-guidelines.md`, extending the existing
    "Stop retrying on a repeated failure signature" subsection, and accept that
    the coordinator's report stays ambiguous.
  - **Upstream.** Propose an additional outcome or a classification field to
    sd-ai-command-pack so `settled-blocked` carries the distinction, with the
    local documentation as the interim measure.
- Any discrimination rule must rest on evidence the probe or a bounded read-only
  API call can actually obtain — job step conclusions, per-lane durations, the
  `Set up job` step's own status. It must not guess from the check name.
- Preserve the existing safety property: an unclear signal fails toward
  reporting a blocker, never toward merging. A misclassification must not be
  able to turn a real red suite into a merge.
- No change to the coordinator's read-only character or its poll cadence.

## Acceptance Criteria

- [ ] The disposition (local-only or upstream) is recorded with its reasoning,
      including whether upstream approval was sought.
- [ ] A run reading the resulting guidance can classify the PR #155 signature as
      infrastructure using only evidence available at the time, without the
      benefit of hindsight.
- [ ] The guidance names the concrete evidence to check and the exact command to
      obtain it.
- [ ] The fail-toward-blocking property is stated explicitly and holds under
      misclassification in both directions.
- [ ] If the upstream route is chosen, the interim local documentation lands
      first and does not depend on the upstream change merging.

## Out of scope

- Changing the coordinator's poll interval, attempt ceiling, or read-only
  character.
- Automatic retries on an infrastructure classification. Detecting the condition
  and acting on it are separable; this task covers detection and reporting only.
- Any change to `sd-fix-ci` or to the CI workflow definitions themselves.

## Notes

- Deferred once by the operator on 2026-08-06, when the sibling convention fixes
  shipped as PR #156. Tasked rather than dropped so the evidence survives.
- Lightweight enough to stay PRD-only unless the upstream route is chosen, which
  would warrant a `design.md` for the outcome-vocabulary change.

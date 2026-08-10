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

Observed on PR #155 (2026-08-06), in the first two of its workflow attempts. Attempt 1: four
lanes ended cancelled at an identical `15m2s` with `steps: []` — no step ever
ran — while the single lane that obtained a runner passed at `8m51s`.
Attempt 2: a mix of zero-step cancellations and `Set up job` step failures
whose logs read `Service Unavailable` or
`Failed to resolve action download info`. In every failing job zero test
code executed. The coordinator reported the same `settled-blocked` it would
report for a real red suite. Diagnosis took several retries plus manual
`gh api repos/<owner>/<repo>/actions/jobs/<id>` (and job-logs)
inspection.

The cost is asymmetric and falls on the wrong side. Reading a real failure as
infrastructure wastes retries; reading infrastructure as a real failure invites
a run to "fix" code that was never executed.

### The reason code is uninformative in a third way

`merge_state_not_clean` does not separate failed checks from unresolved review
threads either, so the ambiguity is broader than infrastructure-versus-real.

Observed on PR #157 (2026-08-06; historical — the current eligibility
script has since gained specific `merge_blocked_conversation` /
`merge_blocked_review` codes with thread evidence for exactly this case, so
this signature now marks a legacy or degraded result). Stage 3 returned
`settled-blocked` with
`reasonCodes: ['merge_state_not_clean']` while **every** check was green — six
`SUCCESS`, one `SKIPPED`. The actual blocker was five unresolved Copilot
threads, discoverable only by querying GitHub separately
(`mergeStateStatus: BLOCKED`, `mergeable: MERGEABLE`, `reviewDecision: ""`).
Nothing in the probe result pointed at threads.

The probe's own documented evidence limit compounds this: a merge-state-blocked
result short-circuits before thread listing, so `threads` was `null` — and per
`watch-coordinator.md`, consumers "must not treat an absent thread list in a
blocked report as 'no threads'". The one field that would have named the cause
is guaranteed absent in exactly the case where it is needed.

So a single `merge_state_not_clean` currently spans at least three distinct
conditions — infrastructure failure, genuine check failure, and unresolved
threads — each with a different correct response. Any classification this task
adds should be evaluated against all three, not only the first.

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

## Disposition (recorded 2026-08-09)

**Local-only, with an upstream relay issue.** The coordinator's outcome
vocabulary lives in the vendored sd-ai-command-pack reference, and this
run's authority excludes upstream pull requests without explicit per-PR
approval, which was not sought — so the upstream option is not exercisable
here. The local-only option is viable on its own (the PRD's stated
requirement for exactly this case): the discrimination procedure now lives
in `.trellis/spec/backend/quality-guidelines.md` as the subsection
"One `settled-blocked` spans three conditions: classify before responding",
extending the existing "Stop retrying on a repeated failure signature"
subsection. The procedure is scoped as post-coordinator diagnosis on a
delivered `settled-blocked` report, so it does not conflict with the
coordinator's own ban on supplementary thread queries inside the polling
loop; step 1 reads the probe's own `checks.items` evidence rather than
re-querying. An upstream relay issue proposing a classification field on
`settled-blocked` is filed against sd-ai-command-pack (issue link in the
completion evidence) so the vocabulary change stays discoverable upstream;
the local guidance does not depend on it merging.

The guidance covers all three conditions the PRD identifies under one
`merge_state_not_clean`:

- **PR #157 signature** (all checks green, `threads: null`) — classified as
  unresolved threads by the check-conclusions probe plus the exact GraphQL
  `reviewThreads` query and `gh pr view --json mergeStateStatus,mergeable,reviewDecision`.
- **PR #155 signature** — classified as infrastructure from the job-step
  evidence (`gh api repos/<owner>/<repo>/actions/jobs/<id>`: step
  conclusions, `steps: []`, timestamps for the identical-duration tell)
  with the quoted error text (`Service Unavailable` / `Failed to resolve
  action download info`) obtained from the separate logs endpoint
  (`.../actions/jobs/<id>/logs`); evidence available at the time, no
  hindsight required.
- **Real failure** — an executed test/lint step failed; retry is never the
  response.

Fail-toward-blocking is stated explicitly in the guidance: classification
selects the response, never the merge; both misclassification directions
still end blocked, and merge eligibility remains the housekeeping gate's own
atomic recomputation, which the classification does not feed.

## Acceptance Criteria

- [ ] The disposition (local-only or upstream) is recorded with its reasoning,
      including whether upstream approval was sought.
- [ ] A run reading the resulting guidance can classify the PR #155 signature as
      infrastructure using only evidence available at the time, without the
      benefit of hindsight.
- [ ] The same guidance separates the PR #157 signature — all checks green,
      `merge_state_not_clean`, `threads: null` — as unresolved threads rather
      than a check failure, and names the query that confirms it.
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
  would warrant a `design.md` and an `implement.md` for the outcome-vocabulary
  change.

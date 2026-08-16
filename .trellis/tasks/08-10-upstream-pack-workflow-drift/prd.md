# Upstream pack drift: finish-work placeholder guidance and the shared review round budget

**RELAYED 2026-08-16.** Both findings are filed upstream as
`platypeeps/sd-ai-command-pack#484` (Finding 1) and `#485` (Finding 2). They sit
in vendored pack files that a refresh reverts, so neither is fixable from this
repository.

The blocker changed shape rather than clearing. This task no longer waits on
approval to open an upstream PR from here; it waits on upstream triage of those
two issues. The acceptance criteria below are unchanged and are still verified
against this repository after a refresh, not against the issues.

## Goal

Record two defects observed while shipping
`07-25-audit-workflow-entrypoint-routing` (PR #211) so they survive the run
that found them, and state the fix each needs upstream.

## Finding 1 — stale placeholder guidance in `sd-finish-work`

`.agents/skills/sd-finish-work/SKILL.md:136` tells the caller to fall back to
`add_session.py` and "fill the `(Add details)`, `(Add test results)`, and
`(see git log)` placeholders manually". Two of those three no longer exist:
`.trellis/scripts/add_session.py:59-62` defines `DEFAULT_MAIN_CHANGES`
(`- Detailed change bullets were not supplied; see the summary above.`) and
`DEFAULT_TESTING` (`- Validation was not recorded for this session.`), which it
writes instead. Only `(see git log)` at `:222` still appears.

The guidance is therefore unactionable on the fallback path it governs: an
agent following it searches for two strings that are never written, and may
conclude the recorder failed. The fix is to name the two default sentences,
which are what actually need replacing.

Classification: `.agents/skills/sd-finish-work/SKILL.md` is `vendored-pack`
under `tests/test_repo_tooling_ownership.py::OwnershipLookup`.

## Finding 2 — Stage 2b re-entry spends the same review round budget

`sd-review`'s `remoteIntegration roundLimit` defaults to 5
(`scripts/sd-ai-command-pack-review.py:276`), and the coordinator rejects any
attempt above it (`:1754`) until a `review.round-extension` decision authorizes
it. `sd-ship` Stage 2b then re-enters Stage 2 for the head finalization
produced — a re-entry the chain performs on every completed task, not an
exceptional path.

Measured on PR #211: rounds 1–4 converged the work head, finalization moved the
head, and the mandated re-entry consumed rounds 5 and 6. Round 6 recorded three
rebuttals — no code change, no new head — and still required an operator
decision that the standing work-loop authority deliberately excludes. A chain
that predictably needs an over-limit round for bookkeeping is asking for a
decision that carries no information.

Options for upstream to weigh:

- give the successor-head re-entry its own small budget, since it reviews a
  different head than the rounds that preceded it;
- exempt an attempt that supplies only dispositions and runs no paid provider
  call, since the limit exists to bound provider spend; or
- raise the default limit, which is the weakest option — it moves the wall
  without changing the shape that hits it.

## Requirements

- Relayed upstream as issues (`#484`, `#485`) rather than a pull request, so no
  per-PR approval is needed and no session runs in that checkout. If upstream
  asks for a PR instead, that still requires explicit per-PR approval.
- Finding 2's fix must not weaken the round limit's purpose: bounding paid
  remote review calls. An exemption must be provably free of provider calls.
- Behavior for a single-round review with no finalization must not change.

## Acceptance Criteria

- [ ] `sd-finish-work` names the sentences `add_session.py` actually writes on
      the fallback path.
- [ ] A completed `sd-ship until=merge` chain whose review needed four rounds
      reaches merge without a `review.round-extension` decision.
- [ ] The round limit still stops an over-limit attempt that would make a
      provider call.

## Notes

- Observed during `07-25-audit-workflow-entrypoint-routing`, PR #211
  (https://github.com/platypeeps/se-ai-command-pack/pull/211): see the round-5
  and round-6 disposition comments for the full evidence.
- `blockedOn`: upstream PR approval in `platypeeps/sd-ai-command-pack`. The
  autonomous work loop must not select this task.

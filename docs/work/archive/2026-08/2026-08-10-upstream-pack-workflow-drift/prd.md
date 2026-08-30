---
title: "Upstream pack drift — stale finish-work placeholder guidance and shared review round budget (fixes in flight: PR #525)"
status: done
created: 2026-08-10
---
# Upstream pack drift: finish-work placeholder guidance and the shared review round budget

**RELAYED 2026-08-16.** Both findings are filed upstream as
`platypeeps/sd-ai-command-pack#484` (Finding 1) and `platypeeps/sd-ai-command-pack#485`
(Finding 2). They sit
in vendored pack files that a refresh reverts, so neither is fixable from this
repository.

**FIXES IN FLIGHT 2026-08-20.** With the maintainer's explicit approval
("Yes, fix both upstream", interactive selection against this task), both
fixes were implemented in the upstream `sd-ai-command-pack` checkout and filed
as **platypeeps/sd-ai-command-pack#525** (release 0.71.38, `Closes #484` /
`Closes #485`). Finding 1's guidance was updated to describe the current
recorder behavior — the vendored `add_session.py` at the pack's Trellis
≥ 0.6.16 floor omits sections it was given no content for rather than writing
the default sentences named below, so the fix tells agents to pass
`--summary`/`--change`/`--test` up front and treat a missing section as a
missing flag. Finding 2 took the first option below: an evidence-backed
`--successor bookkeeping` re-entry gets its own bounded budget of two rounds
past `roundLimit`, gated on the `--bookkeeping-evidence` payload that
`review-local.py` validates before any provider spend.

The task now waits on upstream merge of that PR and a subsequent pack refresh
here. The acceptance criteria below are unchanged and are still verified
against this repository after a refresh, not against the issues or the PR.

**COMPLETE 2026-08-20.** #525 merged upstream as release **0.71.39** (the
version moved past 0.71.38 when another release landed first; the PR was
re-versioned before merge; `Closes #484` / `Closes #485` both closed). This
repository refreshed: the thin pin and `.sd-ai-command-pack/manifest.json`
read 0.71.39, and the machine-scope install serving this thin consumer was
refreshed to 0.71.39 in the same session. Acceptance verified against the
refreshed install — evidence on the checked criteria below.

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
conclude the recorder failed. As observed, the fix was to name the two default
sentences; the fix actually shipped (see Status above) describes the current
recorder's omission behavior instead, because the recorder itself changed
again before the fix landed.

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

- Relayed upstream as issues (`platypeeps/sd-ai-command-pack#484`, `platypeeps/sd-ai-command-pack#485`)
  rather than a pull request, so no
  per-PR approval is needed and no session runs in that checkout. If upstream
  asks for a PR instead, that still requires explicit per-PR approval.
- Finding 2's fix must not weaken the round limit's purpose: bounding paid
  remote review calls. An exemption must be provably free of provider calls.
- Behavior for a single-round review with no finalization must not change.

## Acceptance Criteria

- [x] `sd-finish-work` names the sentences `add_session.py` actually writes on
      the fallback path. (Verified in the refreshed 0.71.39 machine install:
      the skill now says the recorder omits any section it was given no
      content for — no placeholder sentences — and directs
      `--summary`/`--change`/`--test` on the first invocation, matching the
      vendored recorder's actual behavior.)
- [x] A completed `sd-ship until=merge` chain whose review needed four rounds
      reaches merge without a `review.round-extension` decision.
      (Mechanism verified structurally, not by replaying a live four-round
      chain: the 0.71.39 review controller grants an evidence-backed
      `--successor bookkeeping` re-entry `BOOKKEEPING_REENTRY_ROUNDS = 2`
      rounds past `roundLimit`, gated on the validated
      `--bookkeeping-evidence` payload under automatic local provider
      selection. Present in the refreshed machine-scope
      `sd-ai-command-pack-review.py` this thin consumer resolves.)
- [x] The round limit still stops an over-limit attempt that would make a
      provider call. (Upstream regression tests pin this:
      `test_bookkeeping_reentry_has_its_own_bounded_round_budget` asserts a
      `ReviewError` naming `roundLimit` before any provider check runs, for
      the base limit, past the extended budget, and for every path that
      skips evidence validation — explicit `--local` overrides and
      `--family-evidence`.)

## Notes

- Observed during `07-25-audit-workflow-entrypoint-routing`, PR #211
  (https://github.com/platypeeps/se-ai-command-pack/pull/211): see the round-5
  and round-6 disposition comments for the full evidence.
- `blockedOn` (resolved): upstream merge of `platypeeps/sd-ai-command-pack#525`
  (implements both fixes, opened 2026-08-20 with explicit approval) and the
  pack refresh bringing the release into this repository. Both happened on
  2026-08-20 — #525 merged as release 0.71.39 and this repository's thin pin
  plus the serving machine install refreshed to it. Task archived.

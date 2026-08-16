# Close the `pack.review-scope` late-arrival gap for mixed diffs

> **Blocked on** explicit approval for a pull request against the separate
> `sd-ai-command-pack` repository, which this repository cannot grant itself.
> Every candidate design below lands in a vendored script, so there is no route
> that implements this locally. Planning can proceed; implementation cannot.

## Goal

Stop `pack.review-scope` from failing a PR whose body was correct when it was
authored. Today the requirement for a scope heading can appear *after* the body
is written and judged complete, and the automatic preparer declines to help in
exactly the case where it is most needed.

## Background

`.trellis/spec/backend/quality-guidelines.md`, section "The `pack.review-scope`
gate: three categories, three headings, late arrival", already documents the
mechanism and the manual workaround. This task is about closing it, not
re-describing it.

The gate requires a recognized heading (`Tooling/generated scope`,
`Generated/tooling scope`, `Copied/generated scope`) when the branch diff
contains a scoped file. Category 3 is
`.trellis/workspace/*/journal-*.md` and `.trellis/workspace/*/index.md`.

Those files do not exist when the PR is opened. `sd-ship` Stage 2b's
finalization commits them, so:

1. Stage 1 opens the PR. The diff has no journal files, so no heading is
   required. `--prepare-tooling-body` is invoked and exits `3` — the diff mixes
   tooling paths with authored prose (`.trellis/spec/**` matches no tooling
   pattern), and the preparer appends only when *every* changed path is
   tooling.
2. Stage 2b commits the journal and index.
3. The successor-head re-entry runs `pack.review-scope`, which now fails.

Observed on PR #203 (2026-08-10) exactly as written: the check passed at
`b8c6f98`, and failed at the finalization head `c43aae6` with
`error: tooling/generated files changed, but the PR body does not include a
recognized tooling/generated scope section`. The scope script named the trigger
precisely — `Trellis workspace journal/index files`,
`.trellis/workspace/sdelmas/index.md` and `journal-4.md`. Editing the PR body
cleared it; the deterministic gate then returned `passed`, 11/0.

The spec cites the same shape on PRs #156 and #172 (mixed diff, preparer exits
`3`) and #163 (two review rounds burned without a proactive section). #203 is
the fourth.

PR #208 (2026-08-10) is the fifth, and it exposes a second defect layered on the
first. The sequence was identical — passed at `f4d17ef`, failed at the
finalization head `ee0eb36` naming
`.trellis/workspace/sdelmas/index.md` and `journal-4.md` — but the fix did not
take effect. After `gh pr edit` added the section, the helper passed on its own
(`bash ~/.agents/bin/sd-ai-command-pack-review-scope.sh`, exit 0) and a direct
`sd-check` passed 11/0, while `sd-review` kept reporting
`pack.review-scope failed` with a byte-identical `durationMs: 940` across three
further attempts.

The cause is the review coordinator's private attempt state. `_artifact_root`
writes one file per attempt identity under `<cache-namespace>/review-controller`,
and that identity — `{repository, scope, base, head, prNumber, controls}` — does
not include the attempt number, so attempts 3 through 6 all resolved to the same
stored record and replayed its `check` block instead of re-running the gate. The
resume-idempotency rule in `sd-review`'s SKILL.md is what makes this correct for
a delayed receipt and wrong here: `pack.review-scope` reads the **PR body**, an
input that lives off-head, so the only way to re-verify after fixing it is to
change the head or delete the state file. Deleting
`review-853b0905b50c47b44655902a.json` (no dispatched remote request, so nothing
to reconcile) made the next run report `ready` with `check passed 11/0`.

Whichever remedy is chosen for the late arrival itself, an attempt identity that
ignores off-head deterministic inputs leaves a state where a correctly applied
fix cannot be proven at the same head.

## Requirements

- A PR that will acquire journal/index files at finalization must not fail
  `pack.review-scope` solely because those files did not exist when its body was
  authored.
- The remedy must not weaken the gate: a genuinely unexplained tooling/generated
  change must still fail.
- It must not require the operator to remember a proactive section. The current
  guidance already says to write one; the recurrence across five PRs is the
  evidence that guidance alone is not closing it.
- A `pack.review-scope` failure that is fixed off-head — by editing the PR body,
  the only input the gate reads that is not in the commit — must be re-provable
  at the same head through a sanctioned invocation, without deleting the
  coordinator's private attempt state.

## Design questions for the planning phase

- **Append for the tooling subset.** Let `--prepare-tooling-body` append a
  section describing only the tooling paths in a mixed diff, instead of exiting
  `3` and writing nothing. Smallest change to the observed failure; needs a
  decision about what the section says when the tooling paths are a minority of
  the diff.
- **Prepare at finalization instead of creation.** Have the stage that commits
  the journal also ensure the body carries the heading, so the preparer runs
  when the deciding diff actually exists. Correct by construction; puts a
  GitHub body edit inside a finalization step that is otherwise local.
- **Predict the category.** At PR creation, treat a Trellis task branch as one
  that *will* gain journal/index files and require the section up front. No new
  body edit late in the chain, but it asserts a future diff.

- **Bind the attempt identity to the PR body, or scope the reuse.** Either fold
  a digest of the resolved PR body into the attempt identity, so an edited body
  is a new attempt rather than a replay, or narrow what the stored record
  replays: the durable remote receipt is what resume-idempotency exists to
  protect, and the deterministic `check` block could re-run every time at a cost
  of one gate execution. `~/.agents/bin/sd-ai-command-pack-review.py` is vendored too,
  so this shares the upstream-approval constraint below.

Note the ownership constraint before choosing: both
`~/.agents/bin/sd-ai-command-pack-review-scope.sh` and
`~/.agents/bin/sd-ai-command-pack-pr-body-scope.py` are vendored (Registry B,
`install: "always"`), so any code change is an upstream pull request against
platypeeps/sd-ai-command-pack and needs explicit per-PR approval. See
`.trellis/tasks/archive/2026-08/08-10-review-check-cache-pr-body/disposition.md`
for the routing precedent.

## Acceptance criteria

- [ ] A test reproduces the sequence at the layer that owns the defect: a body
      valid for the creation-time diff, a finalization commit adding
      journal/index files, and a `pack.review-scope` run that does not fail for
      that reason alone. It must fail against today's code.
- [ ] The chosen mechanism is documented in the existing "late arrival"
      section of `.trellis/spec/backend/quality-guidelines.md`, replacing the
      manual-workaround guidance rather than sitting beside it.
- [ ] An unexplained copied/generated change with no heading still fails, with
      its own test.
- [ ] A test covers the replay defect: a stored attempt whose `check` failed,
      an off-head input change that would now pass, and a same-head rerun that
      reports the current verdict rather than the stored one — failing against
      today's code.

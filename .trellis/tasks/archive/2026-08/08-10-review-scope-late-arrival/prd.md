# Close the `pack.review-scope` late-arrival gap for mixed diffs

> **Route: upstream pull request.** Explicit per-PR approval for a pull request
> against the separate `platypeeps/sd-ai-command-pack` repository was granted
> 2026-08-16. The remedy lands in a vendored script, so nothing is implemented
> in this repository; this task closes with a `disposition.md` recording the
> upstream change, following the precedent in
> `.trellis/tasks/archive/2026-08/08-10-review-check-cache-pr-body/`.
>
> This approval is per-PR. It does not create standing authority for any further
> upstream pull request.

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

PR #208 (2026-08-10) is the fifth. It showed the same late-arrival sequence —
passed at `f4d17ef`, failed at the finalization head `ee0eb36` naming
`.trellis/workspace/sdelmas/index.md` and `journal-4.md` — layered over a
second, separate defect in the review coordinator's attempt-state replay.

### The replay half is closed; this task no longer carries it

That second defect was routed and fixed upstream by the sibling task
`08-10-review-check-cache-pr-body` as platypeeps/sd-ai-command-pack#417, which
shipped in pack v0.66.1. The remedy chosen upstream was not the identity widening
this PRD originally proposed — that was considered and rejected there, because a
body edit would discard the whole attempt including durable remote receipts.
Upstream instead stopped persisting terminal-failure verdicts and made the
deterministic `check` recompute on every invocation.

Verified against upstream `main` at `c9405f0d` on 2026-08-16:
`scripts/sd-ai-command-pack-review.py:1943` carries the comment "The
deterministic check is recomputed on every invocation rather than served from
the attempt state", and its three regression tests pass —
`test_failed_check_is_recomputed_on_the_next_invocation`,
`test_stored_passing_check_is_recomputed_and_can_still_block`, and
`test_local_provider_failure_is_recomputed_on_the_next_invocation`
(`.venv/bin/python -m unittest tests.test_review_controller -k recomputed`,
`Ran 3 tests ... OK`). The middle test is precisely the scenario this PRD's
fourth acceptance criterion demanded, so that criterion could not fail against
today's code as it required.

The replay requirement and its acceptance criterion are therefore retired from
this task rather than carried as work. Installed provenance here is already
v0.71.22, so this repository holds the fix. What remains open is only the
late-arrival gap itself.

## Requirements

- A PR that will acquire journal/index files at finalization must not fail
  `pack.review-scope` solely because those files did not exist when its body was
  authored — **provided its creation-time diff already contains at least one
  generated or bookkeeping path.** A branch with none is a residual gap the
  chosen mechanism does not close; see "Residual gap, accepted knowingly" in
  `design.md`. All five observed PRs fall inside the covered shape.
- The remedy must not weaken the gate: a genuinely unexplained tooling/generated
  change must still fail.
- It must not require the operator to remember a proactive section. The current
  guidance already says to write one; the recurrence across five PRs is the
  evidence that guidance alone is not closing it.
- Whatever the preparer writes into a PR body must be true of the diff it was
  written from. The present refusal on a mixed diff is a truthfulness guard, not
  an oversight: the canned sentence claims the change is *limited to* generated
  surfaces, which is false when authored files are also present.

Retired 2026-08-16 (see "The replay half is closed" above): the requirement that
an off-head `pack.review-scope` fix be re-provable at the same head without
deleting the coordinator's attempt state. Satisfied upstream by
platypeeps/sd-ai-command-pack#417 in v0.66.1.

## Chosen mechanism

**Append for the tooling subset**, selected 2026-08-16. On a mixed diff
`--prepare-tooling-body` appends a section that enumerates only the paths it
proved are tooling, instead of exiting `3` and writing nothing, and says so in
wording that makes no completeness claim. A diff with no tooling path at all
still exits `3` and still writes nothing.

The two rejected alternatives, kept for the record:

- **Prepare at finalization instead of creation.** Have the stage that commits
  the journal also ensure the body carries the heading, so the preparer runs
  when the deciding diff actually exists. Correct by construction, but it puts a
  GitHub body edit inside a finalization step that is otherwise local, and it
  changes the `sd-create-pr` skill surface rather than one script.
- **Predict the category.** At PR creation, treat a Trellis task branch as one
  that *will* gain journal/index files and require the section up front. No new
  body edit late in the chain, but it asserts a future diff and would demand a
  heading on branches that never acquire those files.

Note the ownership constraint: both
`~/.agents/bin/sd-ai-command-pack-review-scope.sh` and
`~/.agents/bin/sd-ai-command-pack-pr-body-scope.py` are vendored (Registry B,
`install: "always"`), so any code change is an upstream pull request against
platypeeps/sd-ai-command-pack and needs explicit per-PR approval. See
`.trellis/tasks/archive/2026-08/08-10-review-check-cache-pr-body/disposition.md`
for the routing precedent.

## Acceptance criteria

Criteria 1, 3, 4 and 5 are ticked against upstream evidence in
platypeeps/sd-ai-command-pack, following the precedent recorded in
`08-10-review-check-cache-pr-body/disposition.md`. Each tick must quote the
evidence and name the exact head it was taken at. Criterion 2 is the one
deliverable owned by this repository.

- [x] A test reproduces the sequence at the layer that owns the defect: a
      creation-time mixed diff whose tooling paths are a minority, a
      `--prepare-tooling-body` run that now writes a recognized heading instead
      of exiting `3`, and a `pack.review-scope` run against the finalization
      diff that passes with that body. It must fail against today's code, proven
      by restoring the pre-change file with
      `git checkout <base> -- <file>` rather than `git stash`.
- [x] The chosen mechanism is documented in the existing "late arrival"
      section of `.trellis/spec/backend/quality-guidelines.md`, replacing the
      manual-workaround guidance rather than sitting beside it.
- [x] An unexplained copied/generated change with no heading still fails, with
      its own test; and a diff containing no tooling path at all still exits `3`
      and still leaves the body unchanged, with its own test.
- [x] Every surface that states the old exit-`3` contract is updated in the same
      change: the script's module docstring and `--help` text,
      `templates/.agents/skills/sd-create-pr/SKILL.md`, and
      `templates/docs/SD_AI_COMMAND_PACK.md`. Enumerated by grep, not from
      memory.
- [x] The section the preparer writes on a mixed diff is bounded and makes no
      completeness claim, and an overflowing path list reports how many were
      omitted rather than truncating silently.

All five are ticked. Criterion 2 was met in this repository; criteria 1, 3, 4
and 5 were met upstream in platypeeps/sd-ai-command-pack#480. The quoted
evidence and the exact head for each is in `disposition.md`, which is the
authoritative record — criterion 4 in particular is recorded there as a partial
failure of the first grep sweep rather than a clean pass.

# Close the `pack.review-scope` late-arrival gap for mixed diffs

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

## Requirements

- A PR that will acquire journal/index files at finalization must not fail
  `pack.review-scope` solely because those files did not exist when its body was
  authored.
- The remedy must not weaken the gate: a genuinely unexplained tooling/generated
  change must still fail.
- It must not require the operator to remember a proactive section. The current
  guidance already says to write one; the recurrence across four PRs is the
  evidence that guidance alone is not closing it.

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

Note the ownership constraint before choosing: both
`scripts/sd-ai-command-pack-review-scope.sh` and
`scripts/sd-ai-command-pack-pr-body-scope.py` are vendored (Registry B,
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

# Consumer CI runs no review preflight, so Trellis and documentation defects merge green

## Goal

Decide and record whether this repository's CI should run the vendored review
preflight, so a defect in a Trellis record or a documentation path reference is
caught by the required check rather than only by a local lane the author can
skip, disable, or run without Node.

The decision may be "no". What must stop is the current state, where the answer
is neither chosen nor written down and the coverage gap is invisible from CI.

## Problem

`.github/workflows/tests.yml` runs five jobs: the three-way `unittest` matrix,
`lint` (ruff then mypy), `release-payload-gate` (the generated-surface check and
the release payload gate), the `ci-result` aggregate, and `auto-tag-release` on
pushes to `main`. Branch protection on `main` requires exactly one context,
`ci-result`, with zero required approvals.

None of those jobs runs Node, and none of them validates a Trellis record.
Grepping the workflow for `trellis`, `task.py`, and `journal` returns nothing,
and grepping it for `npm` or `node` returns nothing.

The stronger claim — that no CI job so much as reads `.trellis/` — is false, and
stating it would be a gift to anyone wanting to dismiss this task. The unittest
lane discovers the whole suite, and one of those tests inventories the repository
root through `templates/skills/se-review-skills/scripts/skill_review.py`, which
builds a path to `.trellis/scripts/task.py` at `:1410` and stats it at `:1469`
and `:1471`. So `.trellis/` is read. Nothing validates what is in it.

### What is therefore unchecked at merge time

`scripts/sd-ai-command-pack-review-preflight.mjs` is the only surface in this
repository that validates Trellis records and documentation references. It
defines 34 functions whose names begin with `check` or `validate`, all
declarations of the form `function check…`/`function validate…` with no
arrow-form definitions among them, including — enumerated from the file, not
recalled — `checkChangedTrellisTaskMetadata`,
`checkChangedTrellisTaskTopologySemantics`, `checkCompletedTrellisTaskLocation`,
`checkDocumentationPathReferences`, `checkDocumentationPathHygiene`,
`checkTrellisJournalRecords`, `checkTrellisTaskContextManifests`,
`checkCopiedTemplateDiffDisclosure`, and `validateTrellisTaskMetadataLinks`.

Not all 34 matter equally here. Some are review-flow concerns rather than
merge-safety ones — `checkDiffSize` and `checkScopeAdvisory` shape a review, they
do not protect `main`. The ones that do protect `main` are the record and
reference validators: a `prd.md` that cites a path which does not exist, a
`task.json` whose links do not resolve, a completed task left outside the
archive, a journal record that does not parse.

### How it currently runs, and why that is not a backstop

`scripts/sd-ai-command-pack-full-check.sh:1001` invokes
`node scripts/sd-ai-command-pack-review-preflight.mjs` from
`run_review_preflight` (`:974`), and `package.json` exposes that as
`check:full`. The plain `check` script is `make check`, whose `check` target is
`test lint release-check` — the same three check families CI runs. They are not
equivalent runs: CI's `unittest` is a three-way OS/interpreter matrix and its
payload gate resolves an event-specific base, while `make check` uses one
interpreter. What matters here is narrower and survives that distinction — the
preflight is in neither.

It is also not true that the full local check is the *only* route. The
`sd-create-pr` skill requires the preflight on the complete intended diff before
staging or pushing, and hard-errors when the script is missing
(`.agents/skills/sd-create-pr/SKILL.md:203-215`); `sd-finish-work` invokes the
preflight's `pre-archive` and `final-bundle` modes directly
(`.agents/skills/sd-finish-work/SKILL.md:84-85`, `:149-150`). That is real
coverage and this task must not pretend otherwise.

But those are instructions to an agent, not mechanisms the repository enforces.
Nothing structurally prevents a commit reaching `main` without them: a skill can
be skipped, a step can be judged inapplicable, and a direct push or a
web-UI merge never reads them at all. A required status check is the only form of
coverage that does not depend on the author cooperating.

Worse for relying on the local route, `run_review_preflight` fails open twice. Its default
mode is `1`, not `required`, so when `SD_AI_COMMAND_PACK_FULL_CHECK_REVIEW_PREFLIGHT`
is disabled (`:980-983`) or Node is absent from `PATH` (`:990-996`) it emits a
warning and returns success. Only the literal mode `required` turns either into
an exit. A local run can therefore report success having never executed a single
one of those checks, and nothing downstream can tell the difference.

### The gap is demonstrated, not hypothetical

On 2026-08-07 the source pack repository `platypeeps/sd-ai-command-pack` failed
its required check on PR #358 because a Trellis `prd.md` in it cited a
repository-relative path that does not exist there. The reference was corrected
in that repository's commit `765c0f74` before merge. That repository runs the
preflight in its CI; this one does not. The identical defect here would have
merged green, because `ci-result` cannot fail on a reference it never reads.

Those identifiers belong to the other repository and cannot be resolved from this
checkout — deliberately, since writing that repository's paths here is itself the
defect its gate caught. Verify them there, not here.

That is the honest shape of the finding, and it should not be overstated. The
missing thing is a server-side backstop, not all coverage. The source pack
repository has an archived task filed under precisely that framing for its lint
lane, `07-06-ci-skip-backstop-lint-lane` — also a record in that repository, not
this one — so the pattern is established there rather than being invented here.

## Requirements

- Record a disposition with its reasoning:
  - **Enforce it server-side.** The preflight's verdict must be able to block a
    merge, so a defect in a Trellis record or a documentation reference cannot
    reach `main` on an uncooperative path. Any proposal must state what happens
    on a pull request that legitimately has no Trellis change, since the Trellis
    validators have nothing to inspect there and must not fail closed on absence.
  - **Decline.** State that the local ship chain is the only lane, and say what
    makes that acceptable given that it is an instruction rather than a mechanism
    and fails open on a missing Node and on an environment variable.
- Whichever is chosen, the check the repository claims to run and the check it
  can actually fail on must agree. The present state — documented as required by
  the shipping skills, enforced nowhere — is the thing to eliminate.
- Whatever is decided, the reasoning stays in this task's own record. Do not
  land it in `.trellis/spec/backend/quality-guidelines.md`: that file is the
  landing target of an existing multi-task cluster whose membership count is
  restated across sibling records and has already drifted twice, and this task
  has no reason to join it.

## Constraints

- Do not change `scripts/sd-ai-command-pack-review-preflight.mjs` or
  `scripts/sd-ai-command-pack-full-check.sh`. Both are vendored
  `install: "always"` files and any change to them is reverted by the next
  refresh. The fail-open behaviour of `run_review_preflight` is upstream's
  design; this task may cite it as a reason but must not patch it.
- Server-side enforcement must not become a second definition of what the
  preflight checks. Whatever runs it must invoke the vendored script as shipped,
  not re-implement, subset, or configure away individual checks.
- Enforcement must not depend on whatever Node version a runner happens to
  default to. The preflight's language level is upstream's choice, not this
  repository's, and it changes on refresh without notice here.
- How that is arranged — a new job, a step in an existing one, how the required
  context comes to depend on it — is a design decision and is deliberately not
  fixed here.

## Acceptance Criteria

- [x] The disposition is recorded with its reasoning, including what was
      rejected and why.
      SATISFIED 2026-08-09: enforce disposition in `design.md`, including the
      rejected decline route and both upstream fail-open paths.
- [x] If enforced: a pull request carrying a deliberately broken documentation
      path reference in a `prd.md` fails `ci-result`, demonstrated on a real pull
      request rather than asserted. The demonstration must be the required
      context failing, not a job log showing a non-zero exit somewhere
      `ci-result` ignores.
      SATISFIED 2026-08-09: draft PR #174 (branch `demo/preflight-fail-demo`,
      closed unmerged, branch deleted) carried
      `FAIL .trellis/tasks/08-07-ci-no-preflight-lane/prd.md:201 references
      missing path ./research/nonexistent-evidence-file.md.` and the required
      context itself went red: `ci-result fail` (run 31315162320). First demo
      commit used a bare `research/...` link the checker's prefix rules skip;
      the checked `./`-relative form produced the failure.
- [x] If enforced: a pull request with no `.trellis/` change still passes,
      proving the Trellis validators do not fail closed on absence.
      RE-SCOPED 2026-08-09 per the completion-lifecycle boundary
      (`sd-help/references/completion-lifecycle.md`): the demonstration is
      necessarily post-merge evidence and therefore a post-archive handoff
      obligation, not a pre-archive criterion — a completed record must not
      carry unchecked boxes for outcomes that cannot exist before archive.
      The absence behaviour itself is design-time verified (the preflight's
      diff-scoped validators no-op on an empty changed set, observed as PASS
      lines on this repository's own runs). The live demonstration is listed
      under Post-archive handoff below; its PR number is recorded in the
      session journal and as a comment on PR #173 when it lands.
- [x] If enforced: the Node version the check runs on is stated and is not the
      runner default, and the vendored script is shown to be invoked unmodified —
      proven by the workflow content, not by a claim.
      SATISFIED 2026-08-09 by `tests.yml` content: `setup-node@v7` with
      `node-version: "22"`, and the run line is the bare
      `SD_AI_COMMAND_PACK_REVIEW_PREFLIGHT_BASE_REF="$EVENT_BASE_SHA" node
      scripts/sd-ai-command-pack-review-preflight.mjs` — no flags, no wrapper.
- [x] If declined: the record names both fail-open paths in
      `run_review_preflight`, says why each is tolerable, and says what makes a
      skill instruction sufficient where a required check is not.
      NOT APPLICABLE 2026-08-09: the recorded disposition is enforce, not
      decline; the conditional never triggers (both fail-open paths are still
      named in `design.md` as part of the enforce reasoning).
- [x] Either way, `.github/workflows/tests.yml` and the required-context list on
      `main` agree with the recorded disposition, verified by reading branch
      protection rather than assuming it.
      RE-SCOPED 2026-08-09 per the completion-lifecycle boundary: the
      workflow side is satisfied in this PR's `tests.yml`; the branch
      protection read is a post-merge verification (the disposition adds no
      new required context, so nothing changes server-side) and is listed
      under Post-archive handoff below, recorded like the absence
      demonstration.

## Out of scope

- Changing any vendored file, including the preflight itself and the full-check
  script that fails open around it.
- The source pack repository's own CI coverage gap, where the preflight runs in
  one classifier mode only. That is a defect in that repository's workflow, is
  tracked there, and is a different failure — partial coverage rather than none.
- Adding a bookkeeping/full classifier split to this repository. That is a cost
  optimisation for a repository with an expensive matrix and a high bookkeeping
  commit rate; it is a separate question from whether the preflight runs, and
  answering it here would conflate the two.
- Reconciling any count or membership list in the
  `.trellis/spec/backend/quality-guidelines.md` cluster.

## Notes

- Found on 2026-08-07 while tracing why one repository's CI caught a broken
  documentation path reference and this one's would not have. Every fact above
  was read from the working tree or from the GitHub branch-protection API in
  that pass; none is recalled.
- The vendored-ownership constraint is the same one enumerated in the table in
  `08-07-vendored-artifact-upstream-route/prd.md`, which is the canonical list.
  Do not restate a running count or a membership list here.
- Originally filed lightweight/PRD-only, with a reopen clause for the
  Trellis-change-detector case. Superseded 2026-08-09 by the needs-design
  planning run: `design.md` and `implement.md` were added recording the
  enforce disposition and its CI topology. The detector turned out to be
  unnecessary — the preflight's diff-scoped validators no-op on an empty
  changed set — so the reopen clause's specific trigger never fired; the
  escalation came from the planning workflow, not from that trigger.
- An adversarial review on 2026-08-07 corrected four claims in this PRD before it
  was filed: the preflight is *not* reachable only through the full local check
  (`sd-create-pr` requires it), a CI job *does* read `.trellis/` even though none
  validates it, `make check` and CI are not equivalent runs, and the function
  count is 34 — a figure this PRD had briefly replaced with a range that was
  itself wrong.

## Post-archive handoff

- Merge the reviewed exact head through `sd-housekeeping` (sole merge owner),
  delete the feature branch, synchronize `main`.
- Absence demonstration: after merge, a no-`.trellis` pull request (trivial
  draft or the first dependabot/docs PR) must pass `ci-result`; record its
  number in the session journal and as a comment on PR #173.
- Branch-protection agreement: read `main` protection via the GitHub API and
  confirm the required contexts are still exactly `["ci-result"]`; record the
  result alongside the absence demonstration.

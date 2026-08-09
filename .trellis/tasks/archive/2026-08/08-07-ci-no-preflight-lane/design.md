# Consumer CI review-preflight lane — Design

## Overview

The PRD demands a recorded disposition: either the vendored review preflight
can block a merge server-side, or the decline is written down with both
fail-open paths named. This design records the disposition — **enforce** — and
specifies the lane. The reasoning stays in this task's record per the PRD's
requirement; nothing lands in `.trellis/spec/backend/quality-guidelines.md`.

## Proposal

### Disposition: enforce server-side

A new `review-preflight` job in the existing `.github/workflows/tests.yml`
(a job, not a new workflow file) runs the vendored
`scripts/sd-ai-command-pack-review-preflight.mjs` unmodified on every
`pull_request` and push-to-`main` event, and joins the `ci-result` aggregate
so the one required context can fail on it.

**Why enforce, and what was rejected.** The decline route was rejected
because every local lane depends on author cooperation, and the full-check
wrapper lane fails open along two paths by upstream design
(`sd-ai-command-pack-full-check.sh` `run_review_preflight`: mode defaults to
`1`, so a disabled `SD_AI_COMMAND_PACK_FULL_CHECK_REVIEW_PREFLIGHT` at
`:980-983` or a missing Node at `:990-996` warns and returns success). The skill-mandated preflight
in `sd-create-pr` is real coverage but is an instruction, not a mechanism: a
direct push or web-UI merge never reads it. The defect class is demonstrated,
not hypothetical — the source pack repository's required check caught exactly
this (its PR #358, a `prd.md` citing a nonexistent path) because it runs the
preflight in CI; this repository would have merged the same defect green. The
cost is small: the preflight itself ran in ~1.5 s on this tree, plus
checkout and a tool-cache Node setup.

### The job

Following the proven shape of the source pack repository's CI lane
(verified 2026-08-09 by reading `platypeeps/sd-ai-command-pack`'s
`.github/workflows/tests.yml` via the GitHub API), reduced to this
repository's needs — no scope classifier, no coverage instrumentation, no
final-bundle validation, which are that repository's cost optimisations and
out of scope here per the PRD:

```yaml
review-preflight:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v7
      with:
        fetch-depth: 0
        persist-credentials: false
        ref: ${{ github.event.pull_request.head.sha || github.sha }}
    - uses: actions/setup-node@v7
      with:
        node-version: "22"
    - name: Run vendored review preflight
      env:
        EVENT_BASE_SHA: ${{ github.event.pull_request.base.sha || github.event.before }}
        EVENT_NAME: ${{ github.event_name }}
        AFTER_SHA: ${{ github.event.pull_request.head.sha || github.sha }}
      run: |
        set -euo pipefail
        if ! git rev-parse --verify --quiet "${EVENT_BASE_SHA}^{commit}" >/dev/null; then
          echo "error: event base ${EVENT_BASE_SHA:-<empty>} does not resolve; failing closed." >&2
          exit 1
        fi
        if [ "$EVENT_NAME" = "push" ] && ! git merge-base --is-ancestor "$EVENT_BASE_SHA" "$AFTER_SHA"; then
          echo "error: push base is not an ancestor of the head (force push?); failing closed." >&2
          exit 1
        fi
        SD_AI_COMMAND_PACK_REVIEW_PREFLIGHT_BASE_REF="$EVENT_BASE_SHA" \
          node scripts/sd-ai-command-pack-review-preflight.mjs
```

Design points, each tied to a PRD requirement or constraint:

- **Vendored script invoked unmodified** (constraint): the run line is the
  bare script with no flags; configuration is limited to the base-ref
  environment variable the script itself defines
  (`defaultReviewBaseRef`, `review-preflight.mjs:4648-4650`, reading
  `SD_AI_COMMAND_PACK_REVIEW_PREFLIGHT_BASE_REF`). No check is subset,
  re-implemented, or configured away.
- **Node version is stated, not runner-default** (constraint):
  `actions/setup-node` pins major 22 — present in the runner image tool
  cache, so no download — matching the source pack repository's stated
  choice for the same script. Action references use this repository's
  existing tag-pin style (`@v7`, like `checkout@v7`/`setup-python@v6`), not
  the source pack's SHA-pin style; consistency with the surrounding file
  wins.
- **Explicit base and exact head, failing closed** (PRD: the check claimed
  must be the check that can fail): the base is stated from the event
  payload (`pull_request.base.sha`, or `event.before` on push), and the
  checkout pins the exact event head (`pull_request.head.sha`, or
  `github.sha` on push) rather than the default merge-preview ref — with
  the merge preview, a base-SHA three-dot diff would widen to include
  main-side changes since the PR's base, validating (and potentially
  failing on) content the PR never touched. An unresolvable base fails the
  job rather than falling back — the script's own discovery chain ends in
  an arbitrary sorted remote ref, and validating an empty or wrong diff
  window would be a new fail-open. `fetch-depth: 0` makes the base commit
  reachable in the checkout.
- **No fail-closed-on-absence** (PRD requirement on the enforce route): the
  preflight's diff-scoped Trellis validators no-op on an empty changed set —
  observed on this repository's own runs ("no changed Trellis task metadata
  records require integrity checks" PASS lines) and stated in the source
  pack's workflow comments. A PR with no `.trellis/` change passes without
  any Trellis-change detector, so the complex-task reopen clause in the PRD
  Notes is not triggered.

### Joining the aggregate

`ci-result.needs` gains `review-preflight`. The job is unconditional (no
`if:`), so under the current inline aggregate (`not in ("success",
"skipped")`) a failure blocks and a skip cannot occur.

Coordination with `08-08-ci-gate-fail-softs` (designed, not yet
implemented), which replaces that inline aggregate with
`.github/scripts/aggregate-ci-result.py` and explicit lane sets: whichever
task implements second reconciles. If the aggregator exists when this lands,
`review-preflight` joins its `REQUIRED_LANES`; if this lands first, the
aggregator's author declares the lane when extracting (its fail-closed
lane-set mismatch — exit 2 on an undeclared lane in `NEEDS_JSON` — makes
forgetting loud, not silent). Neither task blocks the other.

## Boundaries And Non-Goals

- No change to any vendored file: the preflight, the full-check script, and
  their fail-open behaviour stay as shipped (upstream's design; cited as
  reasoning above, not patched).
- No bookkeeping/full classifier split, no coverage instrumentation of the
  preflight, no second preflight invocation mode — the source pack's
  machinery solves cost problems this repository does not have.
- The source pack repository's own coverage gap stays its own tracked
  concern.
- Branch protection's required-context list is untouched: `ci-result`
  remains the single required context; this lane feeds it.
- `.trellis/spec/backend/quality-guidelines.md` is not touched.

## Affected Files

| Path | Change | Ownership |
|------|--------|-----------|
| `.github/workflows/tests.yml` | new `review-preflight` job; `ci-result.needs` gains it | repo-own |
| `.trellis/tasks/08-07-ci-no-preflight-lane/*` | planning artifacts | task |

One file of real change. `tests.yml` is repo-own (not in
`.sd-ai-command-pack/provenance.json`).

## Data And Command Contracts

- Job contract: exit nonzero iff the base is unresolvable, a push base is
  not an ancestor of the head, or the vendored preflight itself fails; exit
  zero otherwise. No outputs consumed by other jobs; visibility is via
  `ci-result`.
- The preflight's own report format (PASS lines, failure/warning counts) is
  upstream's contract and is consumed by humans reading the job log only.
- Environment contract into the script: exactly one variable,
  `SD_AI_COMMAND_PACK_REVIEW_PREFLIGHT_BASE_REF`, set to the event base SHA.

## Risks And Edge Cases

- **Upstream language-level drift** (constraint): the script's syntax level
  changes on pack refresh without notice here. Pinning Node 22 — the same
  major upstream pins for the same script — keeps the lane from breaking on
  a runner-image Node bump; if upstream moves past Node 22 features, the
  lane fails loudly and the pin is updated in one line.
- **Preflight strictness on historical records:** the preflight validates
  repo-wide surfaces (journal history, completed-task location) that a PR
  did not touch. A pre-existing defect could block an unrelated PR. That is
  the gate working as designed — the same behaviour the local lane already
  has — and the fix is fixing the record, as this repository has done
  repeatedly in its ship loop.
- **Dependabot PRs:** carry no `.trellis/` change; pass by the absence
  behaviour above. `fetch-depth: 0` and Node setup add seconds, within the
  existing lane budget.
- **Fork PRs:** `persist-credentials: false` and no secrets in the job; the
  preflight is read-only over the checkout. Separately, GitHub's Actions
  policy holds first-time fork contributors' runs pending until a
  maintainer approves the workflow run — in that state `ci-result` stays
  pending, which blocks the merge exactly as any other unfinished required
  check does. That is platform behaviour, not this lane's; the lane adds no
  new exposure to it.
- **Initial ref creation:** on a push that creates the ref,
  `github.event.before` is the all-zeros SHA and does not resolve, so the
  base guard fails the job. That is intentional fail-closed behaviour, not
  a defect: the workflow's only push trigger is `main`, whose creation push
  predates this lane, so the case is effectively unreachable — and if it
  ever occurs, a loud failure beats validating an undefined diff window.
- **Double-edit collision with `08-08-ci-gate-fail-softs`:** both tasks edit
  `tests.yml`'s `ci-result`. Ordering rule recorded above; the second
  implementer reconciles, and the aggregator's fail-closed lane check
  backstops the miss.

## Validation

- Workflow-content proof (PRD): the merged `tests.yml` shows `setup-node`
  with `node-version: "22"` and the bare unmodified script invocation —
  read from the file, not claimed.
- Live fail demonstration (PRD): a draft PR carrying a deliberately broken
  documentation path reference in a `prd.md` shows the **required context
  `ci-result` failing**, not merely a red job log. The draft PR is closed
  unmerged and its branch deleted afterwards.
- Live absence demonstration (PRD): a PR with no `.trellis/` change passes
  `ci-result` — the implementing PR itself cannot serve (it changes task
  records), and a pre-merge scratch branch cut from `main` would not carry
  the new workflow yet, so the evidence is necessarily **post-merge**: a
  trivial no-`.trellis` draft PR opened after the implementing PR merges,
  or the first post-merge dependabot/docs PR, whichever lands first. Which
  one was used, and its number, is recorded in the task record as a
  post-merge follow-up — the one piece of acceptance evidence that cannot
  ride inside the implementing PR itself.
- Branch-protection agreement (PRD): after merge, read the `main`
  protection via the GitHub API and confirm the required-context list is
  still exactly `ci-result` — the disposition's claim that no new required
  context is added, verified rather than assumed.

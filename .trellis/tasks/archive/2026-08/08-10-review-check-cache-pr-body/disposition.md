# Disposition: terminal-failure caching in the review controller

Recorded 2026-08-10. Route: **upstream pull request** (filed and linked below).
This file is the authoritative record of the routing decision, the fix that was
written, and what this repository is left holding.

## Why this task cannot be implemented here

`scripts/sd-ai-command-pack-review.py` — the file the PRD names, and the only
file that carries the defect — is vendored. The classification table under
"Vendored-Artifact Ownership And Upstream Route" in
`.trellis/spec/backend/quality-guidelines.md` gives it the row `Registry B,
install: "always" — vendored`, and the "Disposition rule for a defect in a
vendored file" section immediately below is explicit: a local edit is silently
reverted by the next pack refresh, and the correct route is upstream. The
precedent is on record: commit `bc01bc2` edited a vendored file and the
v0.64.32 refresh reverted it.

(Cited by section rather than line number on purpose. The first draft of this
file cited `quality-guidelines.md:824`, and the spec correction recorded below
pushed that table down nine lines — line 824 now holds an unrelated rule. A
citation that a same-run edit can invalidate is not a citation.)

That classification was discovered during this task's design phase, after the
PRD had already been written with code-and-test acceptance criteria. The
criteria were not wrong — they were pointed at the wrong repository.

## Route taken

Explicit per-PR approval was granted for an upstream pull request against
`platypeeps/sd-ai-command-pack` (the autonomous run-level authority excludes
upstream PRs). The work was done in an isolated `git worktree` off
`origin/main` so the shared clone at `~/repos/platypeeps/sd-ai-command-pack`,
in use by another session, was never touched.

This goes one step further than the existing relay precedent. Issues #397,
#398, and #399 reported defects for upstream to fix; this relay carries the fix
itself, with its regression tests and the release-payload bookkeeping the
upstream repository requires.

- Filed: **platypeeps/sd-ai-command-pack#417**
  (https://github.com/platypeeps/sd-ai-command-pack/pull/417), 2026-08-10,
  branch `fix/review-terminal-failure-cache`, base `d7913054`, head `7892ea79`
  (opened at `47d5dfbb`; `04b6f0cc` and `7892ea79` are the review rounds
  below).

## The fix

The PRD's three design options — widen the identity, scope the cache to the
check, add a `--recheck` control — were all rejected in favour of the narrower
root cause the PRD itself had already identified: the controller caches
**terminal-failure verdicts**.

Resume caching is keyed by `_state_identity`: repository, scope, base, head,
worktree bytes, pull-request number, and the typed controls. It does not cover
every input a stage reads. A verdict that turns on an input outside that key is
not completed work to resume from, and storing it pins the attempt to the
verdict, escapable only by supplying a disposition set that happens to match a
current finding or by starting a fresh `--attempt-id` and losing the
coordinator's remote evidence with it.

Upstream now separates *persisting* a result from *reporting* one
(`_record_stage`). A non-resumable outcome still lands in the in-memory state,
so the report shows exactly what the run computed, but the private state file is
not written. Two consequences, and they are different consequences rather than
one restated: nothing durable is left for the next invocation to replay, and
whatever an earlier invocation *did* persist survives untouched. So the next
invocation recomputes when the withheld verdict was all there was, and falls
back to the stored result when one exists — never replaying the verdict either
way. Round 1 of the adversarial review caught this being stated as an
unconditional recompute; both arms now carry a test.

Three live traps close under that one mechanism:

1. **The check** (PR #199, this task's originating observation). `pack.review-scope`
   reads the pull-request body. Only a pass is now persisted.
2. **The local report** (PR #201, the PRD's "Second observation"). An `invalid`
   outcome rejects the caller's `--local-disposition` argv, which the key does
   not cover, and was being written over the good report.
3. **Local provider failure** (found while designing the fix, not previously
   observed as a trap). `unavailable`, `failed`, and `cancelled` turn on whether
   a provider was reachable, which is environmental.

`blocked` stays cached deliberately: local policy is decided by the
configuration digest, which the attempt key *does* cover, so replaying it is
correct. That is why the non-resumable set is enumerated rather than expressed
as "anything that is not clean", and it has its own test.

Manifestation 2 was predicted in this repository the day before it was fixed:
the unfiled-candidate entry dated 2026-08-09 in
`.trellis/tasks/archive/2026-08/08-07-vendored-artifact-upstream-route/prd.md`
names "treat a cached `invalid` local outcome as re-runnable" as an upstream fix
candidate and asks for it to be routed with the next relay batch. This is that
batch.

## Evidence

Upstream, in the worktree at `7892ea79`:

- `.venv/bin/python -m unittest tests.test_review_controller` — `Ran 40 tests`,
  `OK`. Six tests added; the module was 34.
- All four regression tests were proven falsifiable by restoring the controller
  from the base commit (`git checkout d7913054 -- templates/scripts/sd-ai-command-pack-review.py`)
  and re-running. Each fails with exactly the trap it describes — the second
  invocation replays the stale verdict — and the file was restored afterwards
  (`3` `_record_stage` hits, verified):
  - `test_failed_check_is_recomputed_on_the_next_invocation` —
    `AssertionError: Tuples differ: (1, 'blocked') != (0, 'ready')`
  - `test_rejected_disposition_neither_replays_nor_evicts_the_report` —
    `AssertionError: Tuples differ: (2, 'invalid') != (0, 'ready')`
  - `test_rejected_disposition_without_a_stored_report_recomputes` —
    `AssertionError: Tuples differ: (2, 'invalid') != (0, 'ready')`
  - `test_local_provider_failure_is_recomputed_on_the_next_invocation` —
    `AssertionError: Tuples differ: (3, 'failed') != (0, 'ready')`
- The two guarantee tests — `test_unchanged_passing_stages_still_replay_from_the_cache`
  and `test_policy_blocked_local_report_stays_cached` — pass both before and
  after. They are the no-regression guards for the PRD's third requirement, not
  new behavior.
- `make release-prep` (which runs `make check`) — exit 0. 64 module totals
  summing to `1999` tests with zero `FAILED`; `release version gate: shipped
  payload changed; manifest version 0.66.0 -> 0.66.1`; `release changelog gate:
  manifest version bump has matching top heading '## 0.66.1 - 2026-08-10'`;
  `candidate ledger: valid for the current pack payload and fleet`;
  `template twin pairs compared: 193`.
- Upstream CI at `7892ea79` (run 31402572195), the exact head: `CI scope`,
  `lint`, `security`, `Release payload gate`, `Shell coverage`, the `unittest`
  matrix (ubuntu 3.10, ubuntu 3.13, macos 3.13), and the aggregate `CI Result`
  all pass; `mergeable=MERGEABLE`, `mergeStateStatus=CLEAN`, zero non-passing
  checks. Each unittest lane reports 64 modules summing to `1999`, matching the
  local run exactly.

## Review round (upstream, `04b6f0cc`)

Copilot raised one finding: `_record_stage` withholds the phase along with the
state write, so a non-resumable verdict reports the phase of the stage *before*
it — the report reads `phase: capability` after a check failure that would
previously have read `phase: check`.

Rebutted, with the code as evidence. `phase` is the resume marker, not a trace
of how far a run got: `_advance` writes it only when a stage completes, later
stages branch on it (`state.get("phase") == "route-intent"`,
`== "reconciliation-required"`), and `exactHeadReady` requires `== "ready"`. A
verdict this run declined to store completed nothing, so the resume point
genuinely is the stage before it; naming the failed stage there would assert a
completion that did not happen and disagree with the state file a resume reads.
The run is not left unexplained — the report carries the computed stage payload
(`report["check"]` is the `failed` row) beside the `diagnostic` and
`limitations`.

The rebuttal was not free: `04b6f0cc` states the contract in the `_record_stage`
docstring and pins it with assertions, so the choice is falsifiable rather than
incidental. No behavior change. Writing that assertion is what showed the
reported phase is `capability` rather than `resolve` — the capability stage
completes before the check stage — which is a sharper statement of the same
contract than the first draft made.

## Planning adversarial review

Two lanes, per `.claude/rules/sd-planning-adversarial-review.md`: the host
review, and a `codex exec --sandbox read-only` lane. Two rounds, both lanes
each round; Codex completed in ~12 minutes both times. Eleven concerns, merged
and deduplicated — ten addressed, one rebutted, none unresolved.

Round 1 raised seven:

- **C-1** *(host, blocking)* — `quality-guidelines.md` told operators that an
  unchanged-head rebuttal "never forwards the disposition" and needs a fresh
  `--attempt-id`. **Addressed.** False against the installed v0.64.33
  coordinator, which has `state.get("local") is None or args.local_disposition`.
  Dated precisely rather than asserted: `git log -S'or args.local_disposition'`
  upstream returns `7beccf32` ("apply local-disposition reruns and gate on
  outstanding findings", 2026-08-09), and `git tag --contains` puts it first in
  **v0.64.33** — the exact version installed here. Issue #397 closed the same
  day. The bullet now describes actual behaviour and names the trap that did
  survive. This is the guidance that sent two runs in this session to a fresh
  `--attempt-id` — the action that discards review evidence — so it was worth
  finding.
- **C-2** *(host, non-blocking)* — the filed-relay list in
  `quality-guidelines.md` enumerated #397/#398/#399 and would have silently
  omitted #417. **Addressed**, with the fix-carrying relay form documented as
  distinct from the issue form.
- **C-3** *(Codex, blocking)* — the first acceptance criterion demanded a test
  that "changes only the body input", which no controller-level test can do.
  **Addressed** by rewording the criterion to the layer the fix lives in;
  reasoning recorded inline in `prd.md`. The test was not weakened.
- **C-4** *(Codex, blocking)* — the `state["local"]` criterion asserted a
  recompute unconditionally, while its test asserts the stored report is
  *reused*. **Addressed** twice over: the criterion now states both arms, and
  the missing arm got its own upstream test
  (`test_rejected_disposition_without_a_stored_report_recomputes`, commit
  `7892ea79`), which also fails against `d7913054`. Codex was right that the
  criterion and the test disagreed; the honest fix was to cover the arm the
  criterion described rather than only to reword it.
- **C-5** *(Codex, blocking)* — this file's head reference had gone stale
  against the PR. **Addressed** before the lane reported, and again after
  `7892ea79`.
- **C-6** *(Codex, blocking)* — this file cited `quality-guidelines.md:824`,
  which C-1's edit had pushed nine lines down. **Addressed**: cited by section
  name, and the failure noted where the citation now sits.
- **C-7** *(Codex, non-blocking)* — the observation-specific measurements are
  not recoverable from PRs #199/#201. **Addressed** by a provenance note in
  `prd.md` rather than by removing them: they are the report of the run that
  saw them, and the regression tests are the reproducible part.

Round 2 ran both lanes again against the remediated set. Four more concerns:

- **C-8** *(Codex, blocking)* — "a fresh `--attempt-id` is the only escape, and
  it discards the attempt's local and remote review evidence" is wrong twice.
  **Addressed.** A corrected disposition set re-enters the stage in the same
  attempt (`or args.local_disposition` does not consult the cached verdict), so
  it is not the only escape; and a fresh attempt id does not cost the local
  provider evidence, because `execute` derives `receipt_path` from
  `_receipt_identity(target, plan)` with no attempt id in it — verified in
  `scripts/sd-ai-command-pack-review-local.py`. What a fresh attempt actually
  costs is the coordinator's remote state. Both the spec bullet and this file
  now say so.
- **C-9** *(Codex, blocking)* — the spec still said "from v0.66.1 the stage
  recomputes instead", the same unconditional claim C-4 corrected in `prd.md`.
  **Addressed.** A correction applied to two of three stores is not a
  correction; the spec now carries both arms.
- **C-10** *(Codex, non-blocking)* — **rebutted.** Codex read the exact-head CI
  as 65 module totals summing to 2000 and called `1999` stale. Per-job
  attribution shows otherwise: each of the three `unittest` lanes reports 64
  modules summing to **1999**, and the `2000` is the single `Ran 2000 tests`
  line emitted by the separate **Shell coverage** job. 64 + 1 = the 65 that were
  merged. `1999` stands and matches the local run exactly.
- **C-11** *(Codex, blocking)* — this file claimed the full matrix passed at
  `04b6f0cc`. **Addressed**, and it was my error, not a stale value: I reported
  passes from live monitor events for a run that `7892ea79` then superseded and
  cancelled. GitHub's final record for run 31401780532 is `conclusion:
  cancelled`, `unittest (macos-latest, 3.13): cancelled`, `CI Result: failure`.
  The evidence now cites only run 31402572195 at the exact head. Watching a
  check go green is not the same as the run finishing green.

Codex also flagged, correctly, that ticking a task's acceptance criteria
against another repository's evidence has no matching archived precedent — the
closest one ticks the *filing* of an upstream issue, not upstream behavior.
That is accepted as novel rather than precedented, which is why every tick
above carries the quoted evidence and the exact head it was taken at.

One process correction worth recording: the falsifiability probe used earlier
in this run (`git stash push -- <file>`) silently does nothing once the change
is committed, and a test that never ran against the old code reported `OK`.
Re-run against the base commit (`git checkout d7913054 -- <file>`), all four
regression tests fail. The earlier three-test evidence was collected while the
change was still uncommitted and was valid then; the probe, not the result, was
what needed replacing.

No blocking concern is unresolved.

## What this repository is left holding

Nothing to implement, and no vendored file edited: the local
`scripts/sd-ai-command-pack-review.py` is byte-identical to the upstream copy
this fix replaces, and it stays that way until a pack refresh brings v0.66.1 or
later. Until then the trap is live, with two workarounds rather than the one
this file first claimed: re-invoking with a disposition set that *does* match a
finding at the current head re-enters the stage and replaces the rejection in
the same attempt, and a fresh `--attempt-id` is the fallback when no valid id
exists to supply. The fallback costs the coordinator's attempt state — remote
request, receipt, observation, recorded dispositions — but not the local
provider evidence, whose receipt is keyed by `_receipt_identity(target, plan)`
and survives a new attempt id.

Two repo-owned edits this run *did* make, both in
`.trellis/spec/backend/quality-guidelines.md` and both from C-1 and C-2 above:
the local-disposition guidance now matches the installed coordinator, and the
filed-relay list includes #417. Neither is provenance-tracked; both are
reviewed as part of this task's pull request.

The pack refresh itself is ordinary maintenance and is not tracked as a
follow-up task here: this repository is in the fleet manifest and the existing
`sd-fleet-refresh` surfaces already own it.

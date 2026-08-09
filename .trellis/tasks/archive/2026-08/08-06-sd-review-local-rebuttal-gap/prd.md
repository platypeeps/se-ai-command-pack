# sd-review cannot record a rebutted local finding

## Goal

Give a run a sanctioned way to close a local provider finding it has verified
to be wrong — or state plainly that no such way exists and what to do instead —
so a false finding stops being able to hold a chain open indefinitely.

## Problem

Every local provider finding enters the receipt already dispositioned:

```python
"disposition": "outstanding",
```

at `scripts/sd-ai-command-pack-review-local.py:1632` and again at `:1809`. That
value is never revisited within a run. The remote gate then keys directly off
it (`_remote_gate`, `:1857-1858`):

```python
if outstanding or outcome == "findings":
    return {"state": "blocked", "reason": "actionable-local-findings"}
```

The receipt schema itself is not the constraint. `FINDING_DISPOSITIONS` already
admits `outstanding`, `fix`, `fixed`, `rebutted`, and `resolved`, and the
coordinator's summariser counts `rebutted` as a terminal non-fix bucket
alongside `fixed`. The vocabulary exists. Nothing reachable from the command
line can write it for a local finding.

Neither existing control fills the gap:

- **`--remote-disposition '<stable-id>=rebutted'`** validates against
  `REMOTE_DISPOSITION_VALUES` and is applied only to remote receipt rows. Its
  own documentation scopes it to a conversation finding or changes-requested
  review with no resolvable thread. It never reaches the local receipt.
- **`--finding-family` / `--family-evidence`** does accept findings carrying a
  `rebutted` disposition, but `_family_gate` admits the evidence only when
  `audit["localOutcome"] == "clean"` with no local limitations. A local finding
  is by definition the reason the outcome is not clean, so the one route that
  can express a rebuttal is closed exactly when a rebuttal is needed. It is a
  repeated-family round-extension gate, not a disposition mechanism.

So the only way to clear a local finding is to change the code it points at.
When the finding is correct that is the right outcome. When it is wrong, the
run must choose between making an unwanted change and leaving the chain
stopped.

### Observed

PR #158 (2026-08-06). Prism reported the generated `_example` scaffold row in a
planning task's `implement.jsonl` and `check.jsonl` — exactly what
`.prism/rules.json`'s `trellis-scaffold-convention` rule forbids reporting, and
exactly what the review preflight exempts on purpose. Both findings were `low`,
both verified wrong against the checkout.

The chain stopped at Stage 2 with `remoteGate: blocked
(actionable-local-findings)`. The router was `absent`, so under sd-review's
fail-closed rule a non-clean local receipt could not complete locally either.
The round was eventually resolved by curating the manifests with real entries —
legitimate work, and the transition the scaffold's own text prescribes — but
that was a way around the gate, not a disposition of the findings.

### Why this is worth a control rather than a habit

The failure mode is asymmetric. A missing rebuttal path does not cause wrong
code to ship; it causes correct code to be changed to satisfy a wrong finding.
That pressure is invisible in the receipt afterwards: the resulting commit looks
like an ordinary review fix, and nothing records that the finding was rejected.

It also interacts badly with the local providers being non-deterministic. A
finding that appears in one round and not the next leaves no trace either way,
so recurrence cannot be distinguished from a first occurrence.

## Disposition (2026-08-09): adopt via pack refresh — upstream already shipped the control

Investigation on 2026-08-09 found the upstream route already complete without
any proposal from this repository:

- Upstream `sd-ai-command-pack` shipped `--local-disposition` in **v0.64.26**.
  The sibling checkout (`../sd-ai-command-pack`, currently v0.64.32) carries it
  in both `scripts/sd-ai-command-pack-review.py` (parser + coordinator
  forwarding) and `scripts/sd-ai-command-pack-review-local.py`
  (`_parse_local_dispositions`, `_apply_local_dispositions`,
  `_redispose_receipt`).
- This repository's installed pack is **v0.64.3**
  (`.sd-ai-command-pack/manifest.json`), which predates the control. That is
  the entire gap.
- The upstream implementation satisfies this PRD's requirements as written:
  per-finding `<stable-id>=rebutted` syntax, duplicate and malformed ids
  rejected, an id matching no finding at the current head **fails the
  invocation** rather than no-op ("silently accepting it would open the gate
  for a finding nobody actually reviewed"), the rebuttal is recorded in the
  receipt's `localDispositions` block with the finding retained, and the
  `outstanding` count that drives `_remote_gate` is recomputed from remaining
  `outstanding` rows only.

Chosen disposition: **refresh the installed pack to ≥ v0.64.26**, from a
clean, pinned upstream state chosen per the Requirements below (not simply
whatever the sibling worktree holds at run time), verify the control is
present in the installed scripts, and
land the local guidance in `.trellis/spec/backend/quality-guidelines.md`
describing when and how a run may use it. No upstream PR is needed; no local
fork of the vendored scripts is permitted.

## Constraint: all three surfaces are vendored

`scripts/sd-ai-command-pack-review.py`,
`scripts/sd-ai-command-pack-review-local.py`, and
`.claude/skills/sd-review/SKILL.md` are installed from the sd-ai-command-pack
(`.sd-ai-command-pack/manifest.json`), and all three are provenance-tracked.
They must never be edited locally — the sanctioned way to change them is to
refresh the installed pack from upstream. Only this repository's
`.trellis/spec/` guidance is directly editable. When this PRD was written the
upstream control did not yet exist, which forced a choice between a local-only
documentation route and an upstream proposal; the Disposition section above
supersedes that framing, since upstream shipped the control in v0.64.26 and
adoption is now a refresh.

## Requirements

- Refresh the installed sd-ai-command-pack from the upstream source to a
  version ≥ v0.64.26, using the pack's own sanctioned install/refresh
  mechanism — never by hand-copying or locally editing the vendored scripts.
  After the refresh, `.sd-ai-command-pack/manifest.json` must record the new
  version and provenance tracking must report the surfaces undrifted.
- The refresh source must be a **clean, identified upstream state**: a tagged
  release, or an exact recorded commit whose worktree is clean for the
  installable payload. Provenance that says "undrifted" only proves the
  consumer matches the source checkout, so a dirty source would launder
  uncommitted upstream edits into vouched provenance. At review time the
  sibling checkout was at `v0.64.32-16-g39473e09` with modified installable
  templates — that state, as-is, is not an acceptable source. Record the
  chosen source commit/tag in the task.
- Before any forced refresh, run the installer's dry run and capture its
  report. Review the reported conflicts and confirm each is an
  upstream-version difference, not unexplained local drift; record that
  review's conclusion in the task before proceeding. Keep the installer's
  backups; do not bypass its conflict handling.
- Verify the control **behaves**, not merely that its string is present:
  - `--local-disposition` accepted by `scripts/sd-ai-command-pack-review.py`
    and applied by `scripts/sd-ai-command-pack-review-local.py`.
  - A fail-closed probe against the installed scripts: a malformed value and
    an id matching no finding must each fail the invocation with the
    documented error, not be ignored.
  - The refreshed version's upstream behavioral tests (e.g.
    `../sd-ai-command-pack/tests/test_review_stage.py` local-disposition cases) pass in the upstream
    checkout at the version being installed, cited as evidence.
- Document in `.trellis/spec/backend/quality-guidelines.md` when and how a run
  may use the control:
  - Only for a finding **verified wrong against the checkout**, with the
    verification evidence stated in the run's report.
  - Per-finding stable id, `<stable-id>=rebutted`; the flag fails closed on
    malformed, duplicate, and unmatched ids (an id matching no finding at the
    current head fails the invocation). State the contract precisely: finding
    ids are stable across heads and dispositions are **not** inherited — a
    rebuttal applies to one head only, and re-supplying an id on a new head is
    permitted but obliges the caller to re-verify the finding is still wrong
    at that head.
  - The rebuttal is auditable: the receipt retains the finding with its
    `rebutted` disposition in `localDispositions`; the guidance must tell the
    run to state its grounds in the report, not silently clear the gate.
  - Contriving a code change purely to clear the gate remains unacceptable;
    stopping with a report remains the fallback when verification is not
    conclusive.
- State the interaction with the existing family-evidence gate explicitly: the
  rebuttal control is not a second way to satisfy the repeated-family
  round-extension requirement.
- Do not **locally** change what makes a finding actionable, the local
  provider set, its severity mapping, or the deterministic `sd-check` gate.
  Upstream changes to those surfaces arriving as part of the sanctioned
  refresh are in scope of the refresh, not violations of this constraint.
- Review the refresh diff **as a unit** and record that review in the task:
  every behavioral change the diff shows to `sd-check`, the local provider
  set, severity mapping, remote disposition handling, or thread resolution
  must be named in the task's report, not passed silently. A refresh whose
  diff was not reviewed end to end does not satisfy this requirement.

## Acceptance Criteria

- [ ] The disposition (adopt via pack refresh) is recorded with its reasoning,
      including the upstream version that shipped the control and the installed
      version that lacked it.
- [ ] The installed pack version is ≥ v0.64.26 and provenance-tracked as
      undrifted; `grep local-disposition scripts/sd-ai-command-pack-review.py`
      matches in the installed checkout.
- [ ] The refresh source is recorded as a clean tagged release or exact clean
      commit; the recorded source state contains no uncommitted installable
      payload.
- [ ] The pre-force dry-run report is captured in the task, its conflicts are
      dispositioned as upstream-version differences (or any real local drift
      is escalated before forcing), and installer backups exist.
- [ ] The refresh-diff unit review is recorded, naming every behavioral change
      to `sd-check`, the local provider set, severity mapping, remote
      disposition handling, or thread resolution — or stating none was found.
- [ ] The fail-closed probe ran against the installed scripts: a malformed
      `--local-disposition` value and an unmatched stable id each failed the
      invocation with the documented error. Upstream behavioral tests for the
      control pass at the installed version, with the run cited.
- [ ] Any behavioral change the refresh introduces to `sd-check` or the local
      provider set is named in the task's report.
- [ ] The written guidance names the control and the two pre-existing controls,
      and states precisely why the pre-existing two never reached a local
      finding — including that the family-evidence route requires
      `localOutcome == "clean"`.
- [ ] A run holding a verified-wrong local finding can determine the sanctioned
      response from the guidance alone, without re-deriving it from the
      coordinator's source.
- [ ] The guidance states that contriving a change purely to clear the gate is
      not an acceptable response, and requires the rebuttal grounds to be
      stated in the run's report.
- [ ] The guidance states the family-gate interaction explicitly: a local
      rebuttal does not satisfy the repeated-family round-extension
      requirement, and `_remote_gate` still blocks on the family gate after
      outstanding findings are cleared.
- [ ] The guidance states the per-head contract: dispositions are not
      inherited across heads, unmatched ids fail the invocation, and
      re-supplying a still-matching id on a new head obliges re-verification.

## Out of scope

- Fixing why a specific provider produces a wrong finding. That is
  `08-06-prism-rules-lane-divergence`'s subject; this task is about what a run
  can do once a wrong finding exists, whatever its cause.
- Changing `_remote_gate`'s blocking behaviour for genuinely outstanding
  findings, or the router-absent fail-closed rule.
- Adding a bulk suppression, allow-list, or per-path exclusion for local
  providers.
- Any **local** change to remote disposition handling, thread resolution, or
  the deterministic `sd-check` gate. Upstream changes to these surfaces that
  arrive with the sanctioned refresh are governed by the refresh requirement
  above (named in the report, reviewed as part of the refresh diff), not by
  this exclusion.

## Notes

- Observed on PR #158 (2026-08-06). Deliberately excluded from
  `08-06-prism-rules-lane-divergence`'s scope: folding a rebuttal control into
  the task whose own findings needed rebutting would have let that task wave
  them through.
- One of the vendored-artifact instances enumerated in the table in
  `08-07-vendored-artifact-upstream-route/prd.md`, which is the canonical list
  and the task that consolidates the pattern. Do not restate a count or a
  membership list here. `08-06-work-loop-shipped-sha-after-branch-delete` was
  previously listed as a member and is not one — it carries no
  vendored-ownership constraint section.
- Remains PRD-only: the chosen disposition needs no upstream proposal and no
  design work — the id-stability and receipt-schema contract already exists
  upstream. Execution is a sanctioned pack refresh plus a guidance edit.
- The refresh will pull every pack change between v0.64.3 and the refreshed
  version, not just the rebuttal control. That is the normal shape of a pack
  refresh, not scope creep; review the refresh diff as a unit and do not
  cherry-pick vendored files.

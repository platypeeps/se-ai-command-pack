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

## Constraint: all three surfaces are vendored

`scripts/sd-ai-command-pack-review.py`,
`scripts/sd-ai-command-pack-review-local.py`, and
`.claude/skills/sd-review/SKILL.md` are installed from the sd-ai-command-pack
(`.sd-ai-command-pack/manifest.json`), and all three are provenance-tracked and
currently undrifted. Adding a control is an **upstream** pull request needing
its own approval. Only this repository's `.trellis/spec/` guidance is editable
locally, so the local-only route must stand on its own.

## Requirements

- Decide and record a disposition:
  - **Local-only.** Document in `.trellis/spec/backend/quality-guidelines.md`
    that a verified-wrong local finding has no rebuttal control, name the two
    controls that do not apply and why, and state the sanctioned responses in
    preference order: make the change if it is independently correct work;
    otherwise stop the chain and report, never contrive a change to clear the
    gate.
  - **Upstream.** Propose a local-disposition control symmetrical to
    `--remote-disposition` — a stable local finding id moved to `rebutted`,
    recorded in the receipt with its evidence, and excluded from the
    `outstanding` count that drives `_remote_gate`.
- Any upstream proposal must make a rebuttal auditable, not silent. The receipt
  must retain the finding, its `rebutted` disposition, and the supplied
  evidence, so a later reader can see what was rejected and on what grounds. A
  control that simply suppresses the finding is not acceptable.
- Preserve the fail-closed property. A rebuttal must require an explicit,
  per-finding argument naming a stable id — never a bulk flag, a severity
  threshold, a family-wide waiver, or a default. An unrecognised or stale id
  must fail the invocation rather than be ignored.
- Do not change what makes a finding actionable in the first place, and do not
  alter the local provider set, its severity mapping, or the deterministic
  `sd-check` gate.
- State the interaction with the existing family-evidence gate explicitly. A
  new control must not become a second way to satisfy the repeated-family
  round-extension requirement.

## Acceptance Criteria

- [ ] The disposition (local-only or upstream) is recorded with its reasoning,
      including whether upstream approval was sought.
- [ ] The written guidance names both existing controls and states precisely
      why neither reaches a local finding — including that the family-evidence
      route requires `localOutcome == "clean"`.
- [ ] A run holding a verified-wrong local finding can determine the sanctioned
      response from the guidance alone, without re-deriving it from the
      coordinator's source.
- [ ] The guidance states that contriving a change purely to clear the gate is
      not an acceptable response, and names stopping with a report as the
      alternative.
- [ ] If the upstream route is chosen, the auditability and per-finding
      explicitness requirements are both expressed in the proposal, and the
      local documentation lands first without depending on the upstream change
      merging.

## Out of scope

- Fixing why a specific provider produces a wrong finding. That is
  `08-06-prism-rules-lane-divergence`'s subject; this task is about what a run
  can do once a wrong finding exists, whatever its cause.
- Changing `_remote_gate`'s blocking behaviour for genuinely outstanding
  findings, or the router-absent fail-closed rule.
- Adding a bulk suppression, allow-list, or per-path exclusion for local
  providers.
- Any change to remote disposition handling, thread resolution, or the
  deterministic `sd-check` gate.

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
- Lightweight enough to stay PRD-only unless the upstream route is chosen,
  which would warrant a `design.md` and an `implement.md` for the id-stability and receipt-schema
  contract.

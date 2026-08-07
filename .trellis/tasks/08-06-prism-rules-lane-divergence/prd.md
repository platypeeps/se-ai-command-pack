# Repository prism rules never reach the sd-review lane

## Goal

Make a repository-owned prism rule apply in the review lane that actually
gates shipping, or record plainly that it does not — instead of leaving a
config file whose failure mode is silence.

## Problem

Two code paths invoke prism, and only one passes the repository's rules file.

**Shell lane** — `scripts/sd-ai-command-pack-review-local.sh:337-355`. It falls
back to `.prism/rules.json` when no environment override is set, and passes
`--rules`, `--fail-on high`, and `--exclude`:

```bash
if [ -z "$rules" ]; then
  if [ -f ".prism/rules.json" ]; then
    rules=".prism/rules.json"
```

**sd-review lane** — `scripts/sd-ai-command-pack-review.py:34` invokes
`scripts/sd-ai-command-pack-review-local.py`, whose built-in prism adapter
(`_expand_argv`, lines 1375-1400) builds the entire command as:

```
prism review range <base>..<head> --format json
```

No `--rules`. No `--exclude`. No `--fail-on`. The three controls the shell lane
sets are all absent, and nothing else in that file references `.prism/`.

Prism does not compensate by discovering the file itself: `prism config show`
reports an effective configuration with no rules entry. The shell lane's
explicit fallback exists precisely because there is no auto-discovery.

The consequence is that `sd-review` — the lane `sd-ship` Stage 2 runs, and
therefore the lane that decides whether a branch can ship — is the one lane
where every repository-owned prism rule is inert.

### How it surfaced

PR #156 added a `trellis-scaffold-convention` rule to `.prism/rules.json`
telling reviewers not to report the lone generated `_example` row in a planning
task's `implement.jsonl` or `check.jsonl`. On PR #158, prism reported exactly
that, twice:

```json
{"path": ".trellis/tasks/08-06-finalization-ordering-trap/check.jsonl",
 "summary": "Example JSON entries left in check.jsonl and implement.jsonl",
 "severity": "low", "providers": ["prism"], "disposition": "outstanding"}
```

The rule was not wrong and not malformed. It was never delivered.

Two secondary effects follow from the same omission and should be evaluated
together, not separately:

- **`--fail-on` is unset**, so prism applies its own threshold rather than the
  shell lane's `high`. Two `low` findings were enough to return a `findings`
  outcome and set `remoteGate: blocked (actionable-local-findings)`.
- **`--exclude` is unset**, so the sd-review lane scans paths the shell lane's
  standard review-scan exclusions remove. The two lanes review different file
  sets for the same branch.

### Why the silence is the defect

A rules file that is ignored produces no error, no warning, and no limitation
entry in the sd-review report. The only symptom is a finding the rule was
written to prevent — which reads as an ordinary review finding. On PR #158 the
first hypothesis was that the rule was malformed, the second that the config
path was unwired in `review.py`; both were wrong, and locating the real cause
took a read through three scripts and the prism CLI's own effective config.

There is also no way to dispose of the resulting finding without changing code.
`sd-review` exposes `--remote-disposition '<stable-id>=rebutted'` for remote
findings only; `--finding-family`/`--family-evidence` is the repeated-family
round-extension gate and requires `localOutcome == "clean"`. A local finding
that is verifiably wrong has no rebuttal path, so an inert rule converts
directly into blocked shipping.

## Constraint: the adapter is not owned by this repository

`scripts/sd-ai-command-pack-review-local.py` is installed from the
sd-ai-command-pack (`.sd-ai-command-pack/manifest.json`) and is
provenance-tracked and currently undrifted. Editing it here is overwritten by
the next pack refresh, so changing the built-in prism adapter is an **upstream**
pull request needing its own approval.

`.prism/rules.json` is different: its manifest entry is `install: "if-not-exists"`,
so after first install it is repository-owned and edits to it are durable. The
PR #156 rule is not at risk of being clobbered — it is only undelivered.

This asymmetry shapes the requirements: the local-only route must stand alone,
because the upstream route may not be authorized.

## Requirements

- Decide between two dispositions and record the reasoning:
  - **Local-only.** Document in `.trellis/spec/backend/quality-guidelines.md`
    that `.prism/rules.json` governs the shell review lane only, that
    `sd-review` findings are unfiltered by it, and that a finding contradicting
    a repository rule is therefore expected rather than evidence the rule is
    broken. Name the two lanes and the exact command each builds.
  - **Upstream.** Propose that the built-in prism adapter pass `--rules` when a
    repository rules file exists, and decide explicitly whether `--exclude` and
    `--fail-on` travel with it or stay lane-specific.
- Any upstream proposal must keep the adapter's argv construction deterministic
  and injection-safe. The existing code refuses argv overrides for built-in
  adapters on purpose; a rules path must be validated as a repository-relative
  regular file, not interpolated from configuration text.
- Preserve the fail-closed property. A missing, unreadable, or malformed rules
  file must not silently widen what prism reports, and must not turn a findings
  outcome into a clean one.
- State what happens to the two lanes' divergent `--fail-on` and `--exclude`
  behaviour under whichever route is chosen. Leaving them different is an
  acceptable answer; leaving them undocumented is not.
- Do not resolve this by weakening the sd-review gate — not by disabling the
  prism provider, not by adding a blanket path exclusion for
  `.trellis/tasks/**`, and not by introducing a local-finding rebuttal control
  as a side effect of this task.

## Acceptance Criteria

- [ ] The disposition (local-only or upstream) is recorded with its reasoning,
      including whether upstream approval was sought.
- [ ] The written guidance names both lanes, the exact prism command each
      builds, and which of `--rules`, `--exclude`, and `--fail-on` each passes.
- [ ] A run that sees a prism finding contradicting a rule in
      `.prism/rules.json` can determine from the guidance alone whether the rule
      applies to the lane that produced the finding.
- [ ] The `install: "if-not-exists"` ownership of `.prism/rules.json` is stated,
      so a future run does not assume a pack refresh will discard its edits.
- [ ] The fail-closed property is stated explicitly and holds when the rules
      file is absent or unreadable.
- [ ] If the upstream route is chosen, the local documentation lands first and
      does not depend on the upstream change merging.

## Out of scope

- Adding a local-finding rebuttal control to `sd-review`. Real gap, separate
  decision, and adding it here would let this task's own findings be waved
  through.
- Changing prism's default severity threshold, its rule schema, or the contents
  of the `trellis-scaffold-convention` rule itself.
- Reconciling the shell lane's `--exclude` set with the sd-review lane's scan
  scope beyond documenting that they differ.
- Any change to the `gito` provider or to `sd-check`.

## Notes

- Observed on PR #158 (2026-08-06). The findings were dispositioned by curating
  the two manifests with real spec entries — the transition the scaffold's own
  text prescribes — rather than by emptying them, which the convention in
  `quality-guidelines.md` forbids. That resolved the round without settling the
  underlying delivery gap.
- Fourth instance of the vendored-artifact pattern, alongside
  `08-06-watch-coordinator-infra-classification`,
  `08-06-finalization-ordering-trap`, and
  `08-06-work-loop-shipped-sha-after-branch-delete`. If a fifth appears, the
  pattern itself is worth a task.
- Lightweight enough to stay PRD-only unless the upstream route is chosen,
  which would warrant a `design.md` for the argv-validation contract.

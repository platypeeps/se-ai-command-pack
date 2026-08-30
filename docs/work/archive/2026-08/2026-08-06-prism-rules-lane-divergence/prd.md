---
title: Repository prism rules never reach the sd-review lane
status: done
created: 2026-08-06
branch: task/08-06-prism-rules-lane-divergence
---
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

- **`--fail-on` is unset** — but that flag governs prism's *exit status*, not
  the coordinator's gate. The sd-review adapter parses prism's JSON and maps
  any non-empty findings list to a `findings` outcome over the non-terminal
  exit codes 0 and 1 (`scripts/sd-ai-command-pack-review-local.py:1525`,
  `:1752-1756`; terminal exits stay `unavailable` for 3/4 and `failed` for
  unmapped codes), so the two `low` findings on PR #158 blocked shipping
  (`remoteGate: blocked (actionable-local-findings)`) independently of any
  threshold. The lanes' `--fail-on` divergence is an exit-semantics
  difference, not a finding filter.
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

When this PRD was written (2026-08-06) there was no way to dispose of the
resulting finding without changing code, so an inert rule converted directly
into blocked shipping. Since pack v0.64.26 (installed v0.64.32),
`--local-disposition '<stable-id>=rebutted'` on the review coordinator can
close a local finding the run has verified to be wrong — see "Rebutting a
verified-wrong local finding" in `quality-guidelines.md`. That softens the
consequence, not the defect: every run that trips an undelivered rule still
pays a verify-and-rebut cycle, per finding, per round, and the rule stays
undelivered.

## Constraint: the adapter is not owned by this repository

Under the ownership lookup in `.trellis/spec/backend/quality-guidelines.md`
("Vendored-Artifact Ownership And Upstream Route"), Registry B
(`.sd-ai-command-pack/manifest.json`):

- `scripts/sd-ai-command-pack-review-local.py` and
  `scripts/sd-ai-command-pack-review-local.sh` — `kind: script`,
  `install: "always"`: vendored, not editable locally. Changing the built-in
  prism adapter is an **upstream** pull request needing explicit per-PR
  approval (excluded from run-level authority).
- `.prism/rules.json` — `kind: config`, `install: "if-not-exists"`:
  repository-owned after first install, edits durable. The PR #156 rule is not
  at risk of being clobbered — it is only undelivered.

That section's disposition rule applies: local-only is a legitimate terminal
record carrying the four-field record format defined there. The asymmetry
shapes the requirements: the local-only route must stand alone, because the
upstream route may not be authorized.

## Disposition

**Local-only, with an upstream relay issue.** Chosen at planning, executed by
this task's implementation:

- Document in `.trellis/spec/backend/quality-guidelines.md`:
  `.prism/rules.json` governs the shell review lane only; for the shipping
  path (branch delta), the sd-review lane's built-in adapter builds
  `prism review range <base>..<head> --format json` with none of `--rules`,
  `--exclude`, `--fail-on` — both lanes also build other scope templates
  (worktree/codebase/paths variants), which the guidance names as existing
  without enumerating each argv; a prism finding that contradicts a
  repository rule is therefore expected in the sd-review lane, not evidence
  the rule is broken; the two lanes' `--fail-on`/`--exclude` divergence stays
  as-is and documented, with `--fail-on` identified as exit-status semantics
  (the adapter maps any non-empty findings list to a `findings` outcome for
  the non-terminal exit codes 0/1); the rules file's actual degradation
  behaviour as
  stated in Requirements, per case and per lane (shell lane: fail-open
  omission for missing/non-regular, pass-through with a prism-side runtime
  error for unreadable-but-regular or malformed; sd-review lane: file never
  read; no case converting findings to clean); and the
  `install: "if-not-exists"` ownership of `.prism/rules.json`.
- Record the complete four-field local-only record — all four fields, not
  scattered facts — in **both** this PRD's Disposition and the guidance
  section. The fourth field is the explicit statement that **no upstream PR
  was opened**, with the relay issue URL appended to it.
- File one upstream relay **issue** (not a PR) on platypeeps/sd-ai-command-pack
  whose body contains each contract element by name: pass `--rules` only for
  a rules path validated as a repository-relative regular file that is not a
  symlink (resolved containment inside the checkout), deterministic
  injection-safe argv construction (no interpolation from configuration
  text), the configured-but-missing/invalid versus not-configured
  distinction, never converting a findings outcome to clean, and an explicit
  decision left to upstream on whether `--exclude`/`--fail-on` travel with
  `--rules`. Relay issues are precedented (#397–#399, #404, #405, #408); the
  upstream PR itself is not sought. **Filed:**
  <https://github.com/platypeeps/sd-ai-command-pack/issues/409>.

**Four-field record** (duplicated in the guidance section, as the format
requires):

- Owning pack: sd-ai-command-pack.
- Files: `scripts/sd-ai-command-pack-review-local.py` and
  `scripts/sd-ai-command-pack-review-local.sh` (Registry B, `kind: script`,
  `install: "always"`).
- Behaviour: the built-in prism adapter builds its argv with no `--rules`,
  `--exclude`, or `--fail-on` and never reads `.prism/rules.json`, so
  repository-owned prism rules are inert in the review lane that gates
  shipping, with silence as the only symptom.
- No upstream PR was opened; relay issue:
  <https://github.com/platypeeps/sd-ai-command-pack/issues/409>.

## Requirements

- Decide between two dispositions and record the reasoning:
  - **Local-only (guidance).** Document in
    `.trellis/spec/backend/quality-guidelines.md` that `.prism/rules.json`
    governs the shell review lane only, that `sd-review` findings are
    unfiltered by it, and that a finding contradicting a repository rule is
    therefore expected rather than evidence the rule is broken. Name the two
    lanes and, for the shipping path, the exact command each builds. Filing an
    upstream relay **issue** is part of this route's standard record, not the
    upstream route.
  - **Upstream implementation.** Open a pack pull request making the built-in
    prism adapter pass `--rules` when a repository rules file exists, deciding
    explicitly whether `--exclude` and `--fail-on` travel with it. Requires
    explicit per-PR approval; this — and only this — is "the upstream route"
    wherever these criteria mention it.
- Any upstream proposal must keep the adapter's argv construction deterministic
  and injection-safe. The existing code refuses argv overrides for built-in
  adapters on purpose; a rules path must be validated as a repository-relative
  regular file that is not a symlink (resolved containment inside the
  checkout), not interpolated from configuration text.
- State the failure behaviour of the rules file accurately, per degradation
  case and per lane. **Shell lane** (`scripts/sd-ai-command-pack-review-local.sh:337-346`):
  a missing or non-regular file fails `[ -f "$rules" ]` and the flag is
  silently omitted — **fail-open by omission**, prism runs on its defaults,
  which can *report findings a rule would have suppressed* but never silently
  suppresses findings the defaults would report. An unreadable-but-regular
  file passes `-f` (which does not test readability) and a malformed file
  passes it too: both are handed to prism and surface as prism's own runtime
  error, not as omission. **sd-review lane**: the adapter never reads the
  file, so every degradation case is indistinguishable from the healthy one.
  No case in either lane converts a findings outcome into a clean one.
  Documentation must describe this as it is, not assert a fail-closed
  property the code does not have. An upstream implementation proposal must
  additionally distinguish "not configured" from "configured but
  missing/invalid" and must not turn a findings outcome into a clean one.
- State what happens to the two lanes' divergent `--fail-on` and `--exclude`
  behaviour under whichever route is chosen. Leaving them different is an
  acceptable answer; leaving them undocumented is not.
- Do not resolve this by weakening the sd-review gate — not by disabling the
  prism provider, not by adding a blanket path exclusion for
  `.trellis/tasks/**`, and not by introducing a local-finding rebuttal control
  as a side effect of this task.

## Acceptance Criteria

- [x] The disposition (local-only or upstream) is recorded with its reasoning,
      including whether upstream approval was sought.
- [x] The written guidance names both lanes, the exact prism command each
      builds for the shipping path's branch delta, which of `--rules`,
      `--exclude`, and `--fail-on` each passes, and notes that further scope
      templates (worktree/codebase/paths variants) exist in both lanes.
- [x] A run that sees a prism finding contradicting a rule in
      `.prism/rules.json` can determine from the guidance alone whether the rule
      applies to the lane that produced the finding.
- [x] The `install: "if-not-exists"` ownership of `.prism/rules.json` is stated,
      so a future run does not assume a pack refresh will discard its edits.
- [x] The rules file's degradation behaviour is stated accurately per case
      and per lane, matching the Requirements bullet: shell lane — fail-open
      omission for a missing or non-regular file, pass-through with a
      prism-side runtime error for an unreadable-but-regular or malformed
      file; sd-review lane — the file is never read. The guidance asserts no
      fail-closed property the code does not have, and states that no
      degradation converts a findings outcome into a clean one.
- [x] The upstream relay issue exists on platypeeps/sd-ai-command-pack, its
      body contains each contract element named in the Disposition (non-symlink
      repository-relative regular file with resolved containment, injection-safe
      deterministic argv, configured-vs-not-configured distinction, no
      findings-to-clean conversion, explicit `--exclude`/`--fail-on` decision
      left to upstream), verified by reading the issue at its URL, and the URL
      is recorded in the complete four-field record in **both** this PRD's
      Disposition and the guidance section.
- [x] If the upstream **implementation** route (an adapter-behaviour PR,
      distinct from the relay issue) were chosen, the local documentation lands
      first and does not depend on the upstream change merging. Not chosen
      here; the relay issue does not trigger this criterion or the complex-task
      artifact requirement at `.trellis/workflow.md:164`.

## Out of scope

- Changing the local-finding rebuttal control (`--local-disposition`, shipped
  upstream in pack v0.64.26 after this PRD was written). Its existence is
  acknowledged in the Problem section; its behaviour is not this task's to
  alter.
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
- One of the vendored-artifact instances enumerated in the table in
  `.trellis/tasks/archive/2026-08/08-07-vendored-artifact-upstream-route/prd.md`
  (archived 2026-08-09 after shipping the consolidation guidance as PR #187),
  which is the canonical list. Do not restate a count or a membership list
  here. `08-06-work-loop-shipped-sha-after-branch-delete` was previously
  listed as a member and is not one — it carries no vendored-ownership
  constraint section.
- Lightweight enough to stay PRD-only unless the upstream route is chosen,
  which would warrant a `design.md` and an `implement.md` for the argv-validation contract.

## Completion evidence (2026-08-09, PR #190)

- Guidance landed as "Repository prism rules govern the shell review lane
  only" in `.trellis/spec/backend/quality-guidelines.md` (Review And Retry
  Conventions): both lanes' shipping branch-delta commands and flag
  asymmetry, gate mechanics with exit-code mapping, per-case per-lane
  degradation behaviour, `install: "if-not-exists"` ownership, and the
  four-field record.
- Upstream relay filed and verified at its URL to contain each named
  contract element:
  <https://github.com/platypeeps/sd-ai-command-pack/issues/409>. URL
  recorded in the complete four-field record in both this PRD's Disposition
  and the guidance section (`grep -c "issues/409"`: 2 in PRD, 1 in
  guidance). No upstream pull request was opened.
- Adversarial planning review: three Codex rounds. Round 1: six blocking,
  two non-blocking (false fail-closed invariant, --fail-on misattribution,
  disposition taxonomy, malformed-case coverage, hollow relay AC,
  incomplete four-field requirement, command-scope ambiguity, symlink
  wording). Round 2 verified six resolved, kept two open and added two
  (unreadable-vs-non-regular grouping, stale check.jsonl). Round 3 verified
  all resolved except one residual phrase, fixed and grep-verified
  ("regardless of exit code": no occurrences).
- Validation: `make check` — `Ran 640 tests ... OK (skipped=1)`,
  `All checks passed!`. Copilot round 1 raised one finding (env-overridable
  shell-lane defaults and second rules fallback), verified against
  `review-local.sh:327-346` and fixed in d498910; round 2 returned no new
  findings.

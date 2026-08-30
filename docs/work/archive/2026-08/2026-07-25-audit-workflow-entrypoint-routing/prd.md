---
title: Canonical workflow entry points per platform
status: done
created: 2026-07-25
branch: task/07-25-audit-workflow-entrypoint-routing
---
# Canonical workflow entry points per platform

## Goal

An agent that follows this repository's **repo-own** routing documentation is
told which entry point is canonical for every workflow the SD pack wraps, and
what invoking the wrapped `trellis:*` command or skill instead actually costs.

The stronger goal — that no agent on any surface can reach the wrapped path —
is not achievable from this repository. Routing to `/trellis:finish-work` is
also injected at runtime by vendored Trellis files (see "The half this
repository cannot fix"), so this task delivers the repo-own half and hands the
rest to an upstream deliverable rather than claiming a coverage it does not
have.

## Background: the divergence, measured

Four SD skills wrap a Trellis skill of the same workflow. The relation holds
on two independent signals — a same-name sibling under `.agents/skills/`, and
the wrapper's own body naming `trellis-<workflow>`:

| workflow | `sd-*` wrapper | same-name `trellis-*` sibling | wrapper body names it |
| --- | --- | --- | --- |
| `continue` | yes | yes | yes |
| `finish-work` | yes | yes | yes |
| `start` | yes | yes | yes |
| `update-spec` | yes | yes | yes |
| `check` | yes | yes | **no** — `sd-check` is not a wrapper |

`check` is the discriminating case: a same-name pair that is not a wrapper
relation. Any rule built on names alone would wrongly include it.

Duplicated *command* surface for those workflows:

| surface | `continue` | `finish-work` | `start` | tracked? |
| --- | --- | --- | --- | --- |
| `.gemini/commands/trellis/` | yes | yes | no | tracked |
| `.opencode/commands/trellis/` | yes | yes | yes | tracked |
| `.github/prompts/` | `continue.prompt.md` | `finish-work.prompt.md` | no | tracked |
| `.claude/commands/trellis/` | yes | yes | no | **gitignored** (`.gitignore:44`; CONTRIBUTING "`.claude/` tracking policy") |

For `finish-work` the divergence is concrete, not stylistic. Taking the
Trellis path instead of the SD wrapper costs three things:

1. **Commit subjects are never resolved.** `add_session.py` writes
   `` | `<hash>` | (see git log) | `` for every commit
   (`.trellis/scripts/add_session.py:222`). The SD wrapper's recorder resolves
   each subject from Git and fails fast on an unknown hash.
2. **Main Changes and Testing fall back to generic text** — "Detailed change
   bullets were not supplied; see the summary above." and "Validation was not
   recorded for this session." (`.trellis/scripts/add_session.py:59-62`).
   Main Changes takes that default at `:575`; Testing takes it through the
   default parameter at `:214`, which the call at `:606` never overrides. The
   SD wrapper passes caller-supplied `--change`/`--test` content
   (`.agents/skills/sd-finish-work/SKILL.md:113-114`) and refuses to leave an
   entry containing template placeholders (`:119-123`).
3. **No exact-head final-bundle gate.** `.agents/skills/sd-finish-work/SKILL.md:143`
   opens Step 7, the mode-specific final gate across the local bookkeeping
   range; `.agents/skills/trellis-finish-work/SKILL.md` has no equivalent step.

`AGENTS.md:13` currently routes to `/trellis:finish-work` and
`/trellis:continue` by name and never mentions the `sd:*` wrappers, so the one
routing document this repository owns points at the bypassing path.

## The half this repository cannot fix

Routing to the wrapped path is *also* injected at runtime, from files that all
classify `vendored-trellis` under the ownership lookup:

- `.trellis/workflow.md:227` and `:238` — `Flow: ... -> /trellis:finish-work`,
  once per workflow state; `:260` — `[workflow-state:completed] Code
  committed. Run /trellis:finish-work`.
- `.gemini/hooks/session-start.py:368` — `Next-Action: Run /trellis:finish-work`.
- `.opencode/lib/session-utils.js:68` — the same next action.
- `.github/copilot/hooks/inject-workflow-state.py:69`,
  `.codex/hooks/inject-workflow-state.py:69`, and
  `.gemini/hooks/inject-workflow-state.py:69` — the same bootstrap notice,
  pointing the session at the `trellis-start` skill.
- `.trellis/scripts/common/task_store.py:422` — the Trellis CLI itself prints
  "Use /trellis:continue or phase context to decide the next step".
- `.trellis/workflow.md:581` — Phase 3.3 routes directly to
  `trellis-update-spec`, and `.agents/skills/trellis-start/SKILL.md:62` and
  `.agents/skills/trellis-session-insight/SKILL.md:45` route there too. Those
  three reach the wrapped `update-spec` workflow by skill name rather than by
  a `/trellis:` command literal, so a search for the literals alone misses
  them.

These are active instructions, emitted per session or per command, not static
files an agent might happen to read. Alongside them sit the static vendored
mentions — the `trellis:*` command files themselves and the `trellis-meta`
customization references under `.agents/`, `.github/`, and `.opencode/` — which
are equally unfixable here for the same reason.

No edit inside this repository can retire any of them: each is vendored, and a
local fork is reverted by the next refresh. They are enumerated so the residual
bypass is documented rather than implied, and they are carried by the upstream
follow-up (Requirement 4).

## Ownership: what this repository may change

Decided from the two-registry lookup in
`.trellis/spec/backend/quality-guidelines.md`, as implemented by
`tests/test_repo_tooling_ownership.py::OwnershipLookup`:

- `AGENTS.md` classifies **repo-own**: it appears in neither
  `.github/trellis-provenance.json` (which covers only the platform
  directories plus `.gitignore`) nor `.sd-ai-command-pack/manifest.json`.
  Its body is a Trellis-generated block whose own closing line states
  "Edits outside this block are preserved; edits inside may be overwritten by
  a future `trellis update`." Repo-own by the registries, upstream-authored in
  fact — the section goes outside the markers for that reason, not because the
  lookup demands it.
- The tracked duplicated command files (`.gemini`, `.opencode`,
  `.github/prompts`) classify **vendored-trellis**; every `sd-*` skill and
  command classifies **vendored-pack**. Neither is a valid local modification
  target. `.claude/commands/trellis/*` is the exception: gitignored and in
  neither registry, the lookup returns **repo-own** for it, but it is local
  untracked state that `trellis init` rewrites — not a durable fix site, and
  not readable by a guard that must run in the tracked-files-only hermetic
  lane.
- `.github/copilot-instructions.md` classifies **dual-owned** — the sole
  `kind: managed-block` row in `.sd-ai-command-pack/manifest.json` — and is
  the existing precedent for the SD pack amending a routing document it does
  not own, via an appended `SD-AI-COMMAND-PACK:*:START/END` block.

Consequence: the installer-side mechanism (an `AGENTS.md` managed-block row
mirroring `copilot-instructions.md`, or suppressing the duplicated
`trellis:*` surface) lives in the upstream `sd-ai-command-pack` repository, and
the injected-routing half lives upstream in Trellis. Both are out of scope
here.

## Requirements

1. Add a repo-own routing section to `AGENTS.md` **below the
   `<!-- TRELLIS:END -->` marker**, naming the canonical `sd:*` entry point
   for every wrapped workflow, and stating that invoking the wrapped
   `trellis:*` command or skill directly bypasses the wrapper's added steps.
   Nothing inside the Trellis-managed block is edited.
2. Name the `finish-work` cost concretely — unresolved commit subjects,
   generic fallback Main Changes/Testing, and no exact-head final-bundle gate
   — with the file evidence above, rather than asserting a generic preference.
3. Add a deterministic guard that derives the wrapped-workflow set from the
   filesystem at run time and asserts the `AGENTS.md` section matches it. The
   derivation is fail-closed on both signals:
   - a candidate workflow needs a same-name pair of `sd-` and `trellis-`
     prefixed skill directories under `.agents/skills/` **and** a reference to
     the `trellis-` twin's name in the `sd-` skill's body;
   - a same-name pair whose body does not reference its twin is not wrapped
     (`check` today), and must not appear in the section;
   - the comparison is set equality, so both a missing workflow and a stale
     extra one fail; and
   - a floor rejects a derived set smaller than the four wrapped workflows, so
     an upstream prose change that breaks the reference signal fails loudly
     instead of degrading to an empty set that trivially passes. A genuine
     upstream removal trips the same floor; that is intended, and the floor is
     lowered deliberately in the same commit that records the removal.
   Beyond the set, the guard asserts the section's shape: each wrapped
   workflow appears on exactly one canonical-route line, no workflow appears
   twice, and the bypass sentence naming the residual injected routing is
   present. Set equality alone cannot prove "exactly one route" or that the
   bypass is stated.
   The guard reads only tracked files, so it runs unchanged in
   `make test-hermetic`.
4. Record the two upstream mechanisms as one follow-up Trellis task, marked
   blocked on upstream PR approval: the `sd-ai-command-pack` installer-side
   `AGENTS.md` managed block (or surface suppression), and the Trellis-side
   injected routing enumerated above.

## Acceptance Criteria

- [x] `AGENTS.md` names exactly one canonical entry point per wrapped
      workflow, and the non-canonical `trellis:*` path is explicitly marked as
      bypassing the wrapper — verified by the new guard's set, duplicate, and
      bypass-sentence assertions, not by inspection.
      Evidence: `tests/test_agent_routing.py`, 8 tests `OK`.
- [x] The new section sits entirely below the `<!-- TRELLIS:END -->` marker,
      and the bytes above that marker are unchanged — asserted by the guard
      and visible as an append-only hunk in `git diff AGENTS.md`.
      Evidence: `RoutingSectionPlacementTest`; the diff is `+30 -0` with the
      first added line after `<!-- TRELLIS:END -->`.
- [x] The `finish-work` cost is documented with its three concrete effects,
      each traceable to the cited file and line, and each re-checked against
      the current `add_session.py` rather than copied from the wrapper's own
      prose.
      Evidence: all 20 `path:line` citations in this PRD re-read
      mechanically against their files; the stale wrapper prose at
      `.agents/skills/sd-finish-work/SKILL.md:136` is recorded as an upstream
      note rather than repeated.
- [x] The guard derives its workflow set from the filesystem, proven by four
      bite probes, not by inspection: adding a fifth wrapper fails; deleting a
      section entry fails; adding a duplicate route line for one workflow
      fails; and adding a `trellis-` reference to `sd-check` pulls `check`
      into the derived set and fails until the section names it.
      Evidence, each probe reverted afterwards:
      P1 synthetic `sd-probe`/`trellis-probe` pair →
      `FAIL: test_the_section_names_exactly_the_derived_workflows`;
      P2 deleted `start` route line → same test fails;
      P3 duplicated `start` route line →
      `FAIL: test_each_workflow_has_exactly_one_route_line`;
      P4 `trellis-check` reference appended to `sd-check` → set test fails.
- [x] The floor has its own probe. The `sd-check` probe cannot reach it: it
      moves the derived set 4→5, and reversing it only restores 5→4. The floor
      probe instead strips a wrapped skill's reference to its twin **and**
      removes that workflow's routing line, so set equality passes at three and
      the run fails on the floor alone, naming it.
      Evidence: P5 renamed `trellis-continue` inside `sd-continue` and removed
      the `continue` route line → `FAIL: test_derivation_meets_its_floor`,
      with the set test passing at three. Baseline restored: `OK`.
- [x] The residual bypass is stated in `AGENTS.md`, not just in this PRD: a
      reader learns that hooks and `.trellis/workflow.md` still emit
      `/trellis:finish-work` and that following that injected next action
      skips the wrapper.
      Evidence: the section's closing paragraph, pinned by
      `test_the_residual_bypass_is_stated`.
- [x] `make gate-test`, `make gate-lint`, and `make trellis-provenance` pass;
      `make test-hermetic` passes with the new guard included.
      Evidence: `gate-test` `Ran 730 tests ... OK`; `gate-lint`
      `All checks passed!` + `Success: no issues found in 10 source files`;
      `trellis-provenance check: ok (54 hashed, 354 tracked platform files
      covered)`; `test-hermetic` `Ran 730 tests ... OK (skipped=2)`; full
      `make check` exit 0 at 89.1% coverage.
- [x] A follow-up task exists for both upstream mechanisms, carrying the
      blocked marker the backlog ranker reads.
      Evidence: `.trellis/tasks/08-10-upstream-entrypoint-routing-mechanisms/`,
      title prefixed `PARKED:`, `blocked: true`, `blockedOn` naming both
      upstream repositories.

**Not met by this task, deliberately:** the original criterion "session-record
behavior no longer diverges by entry point". Both entry points still behave
differently; only the routing and its cost are now documented and guarded.
Unifying the behavior means editing vendored Trellis skill text and is the
upstream follow-up's deliverable, not this one's.

## Non-Goals

- Editing any `trellis:*` command, prompt, skill, hook, or `.trellis/workflow.md`,
  or the Trellis-managed block inside `AGENTS.md`. All are vendored.
- Unifying the two code paths so `/trellis:finish-work` itself produces the SD
  session record.
- Removing or shadowing the duplicated `trellis:*` command files. Deleting
  vendored files that a refresh rewrites is churn, not a fix.
- Changing `.github/copilot-instructions.md`, which is dual-owned and refreshed
  by the pack installer.

## Decisions

- **Mechanism: routing documentation, not surface suppression.** Suppression
  needs installer support in the upstream repository; the routing-doc section
  is the half this repository owns and is where the audit's evidence points
  (`AGENTS.md:13`).
- **Placement: below `<!-- TRELLIS:END -->`.** The block's own contract
  preserves edits outside it; edits inside are overwritten by `trellis update`.
- **Scope stated as partial, not restated as complete.** The injected-routing
  surfaces are enumerated and handed upstream rather than folded into a
  weakened criterion.
- **Guard derivation uses two signals with a floor.** Names alone admit
  `check`; prose alone couples the guard to vendored wording. Requiring both,
  with a floor, makes a prose change fail loudly instead of silently emptying
  the set.

## Risks

- The guard reads vendored `.agents/skills/sd-*/SKILL.md` content, so a pack
  refresh that adds or renames a wrapped workflow fails CI until `AGENTS.md` is
  updated. That alarm is the point — it is the only signal that the routing doc
  has drifted from the shipped wrapper set — but a reviewer seeing it on a
  refresh PR should update the section, not weaken the guard.
- `scripts/sd-ai-command-pack-install-audit.py:232` puts `AGENTS.md` in the scan bases (tuple opens at `:231`) that are searched for
  legacy pack references. The new section must not contain the retired tokens
  in `LEGACY_PACK_REFERENCES` (`trellis-full-check`, `trellis-housekeeping`,
  `trellis-review-pr`, `sd-refresh-specs`, `TRELLIS_REVIEW_PR_PACK.md`); the
  wrapped-workflow names it does use are not among them.
- `docs/SD_AI_COMMAND_PACK.md:1045-1046` gives `sd-update-spec` a documented-command
  lookup keyed on `Repospec`, `Repomix`, or `Repository map` headings in
  `AGENTS.md`. The new heading must avoid those three words.
- `scripts/sd-ai-command-pack-update-spec-kb.py:1174` treats `AGENTS.md` as a
  preferred KB source, so the KB refresh must run after the edit. The work
  loop already requires it after documentation-shaped mutations.

## Notes

- Audit finding: A-005 (P3/S) — `.trellis/audit/report-2026-07-25.md:46`.
- Planning depth: PRD-only. One documentation section plus one guard test in an
  existing test style; no new module boundaries or contracts.
- Upstream note for the follow-up: `.agents/skills/sd-finish-work/SKILL.md:136`
  still describes the `add_session.py` fallback as leaving `(Add details)` and
  `(Add test results)` placeholders. Current `add_session.py` writes generic
  sentences instead (`:59-62`); only `(see git log)` survives (`:222`). The
  wrapper's own prose is stale relative to the script it wraps.

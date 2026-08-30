---
title: Vendored-artifact defects have no recorded route to upstream
status: done
created: 2026-08-07
branch: task/08-07-vendored-artifact-upstream-route
---
# Vendored-artifact defects have no recorded route to upstream

## Goal

Record once — the ownership lookup, the upstream route, and the local-only
fallback — so a run that finds a defect in an installed file can determine what
it is allowed to do without re-deriving the answer from registries each time.

## Problem

Eight tasks hit the same wall and each wrote its own version of it — all were
active when they did; three have since completed and archived. The
first six reached it independently, before this consolidation task existed; the
seventh and eighth were written after it and still needed their own constraint
sections, because the shared guidance this task proposes does not exist yet:

| Task | Its constraint heading |
| --- | --- |
| `08-06-finalization-ordering-trap` | the stages are not owned by this repository |
| `08-06-prism-rules-lane-divergence` | the adapter is not owned by this repository |
| `08-06-sd-review-local-rebuttal-gap` | all three surfaces are vendored |
| `08-06-watch-coordinator-infra-classification` | the coordinator is not owned by this repository |
| `08-06-task-create-base-branch-default` | the file is vendored |
| `08-06-task-json-trailing-newline` | the file is vendored |
| `08-07-status-collector-pack-drift` | the collector is vendored |
| `08-07-review-py-local-fork` | the fix has no route to durability |

Eight headings, seven phrasings, one fact — two tasks reached the identical
wording independently. Each task spent its own investigation
establishing ownership, and each arrived at the same two-option ending —
document locally, or propose upstream — with no shared statement of what either
option actually requires.

### There are three registries, and which one applies is not obvious

Ownership is decided by a different registry depending on where the file came
from:

| Registry | Governs | Notable behaviour |
| --- | --- | --- |
| `.sd-ai-command-pack/manifest.json` | files installed from sd-ai-command-pack | entry kinds: `install: "always"`, `install: "if-not-exists"`, and `kind: "managed-block"` with an `anchor` |
| `.sd-ai-command-pack/provenance.json` | per-file hashes for the same pack | detects local drift against the installed version |
| `.trellis/.template-hashes.json` | files installed from upstream Trellis | 148 entries, including 28 under `.trellis/scripts/` |

A run holding a file path has no single lookup that answers "who owns this".
Getting it wrong in either direction is costly: treating a repo-owned file as
vendored abandons a fix that was always allowed, and treating a vendored file as
repo-owned produces an edit the next pack refresh silently reverts.

Two behaviours in particular are not obvious from the file alone:

- **`install: "if-not-exists"` means repo-owned after first install.** This is
  how `.prism/rules.json` is classified, and it is why
  `08-06-prism-rules-lane-divergence` concluded the PR #156 rule was
  *undelivered* rather than clobbered. That distinction changed the task's
  entire remedy.
- **A file can be dual-owned.** `.github/copilot-instructions.md` is recorded as
  a whole-file hash by Trellis while the sd-pack legitimately appends its own
  managed block, so the Trellis hash reports permanent drift that is not drift.
  A run comparing hashes will see a false positive with no way to know it is
  expected.

### The boundary is real, not merely undocumented

`sd-work-backlog`'s run-level authority explicitly excludes "an upstream Trellis
pull request without explicit approval for that PR". So the block is genuine.
What is missing is what happens next: whether the local-only fallback is a
lesser outcome or a legitimate terminal one, what a run should write down so the
upstream proposal survives the session, and how a later reader learns the
proposal was never made.

Five of the eight are still in planning; three —
`08-06-sd-review-local-rebuttal-gap`, `08-07-status-collector-pack-drift`, and
`08-07-review-py-local-fork` — completed and archived on 2026-08-09, each after
writing its own constraint section from scratch. What converged is the framing: every one independently reduced the problem to
the same two options — document locally, or propose upstream — and read the
authority boundary the same way, that an upstream pull request is approval-gated
and local documentation is available without it. Eight independent derivations
of one framing is evidence the rule exists; it just is not written anywhere.

The seventh and eighth are the sharpest evidence, in two different ways. Both
were authored on 2026-08-07 with this consolidation task already filed, and both
still had to restate the whole constraint from scratch, because a filed task is
not recorded guidance.

The eighth goes further and raises the stakes of the local-only route.
`08-07-review-py-local-fork` is the one case where the fix already **exists** —
committed locally into an `install: "always"` file — so the local-only outcome is
not a lesser-but-stable ending. It is a liability with an expiry date set by the
next pack refresh, which reverts it silently apart from one test suite. Any
guidance this task records must say that much: local-only is terminal for a
*record*, but for a *code change* it survives only until the next refresh.

## Requirements

- Record the ownership lookup as a procedure: given a repository-relative path,
  which registry to consult in which order, and what each possible result means
  for editability. It must resolve `install: "always"`,
  `install: "if-not-exists"`, `kind: "managed-block"`, a `.template-hashes.json`
  entry, and "in no registry" — including which of those are repo-owned.
  It must also resolve the manifest's **default** mode: an entry with no
  `install` key is `install: "if-anchor-exists"`
  (`installer/manifest.py:87`, `IF_ANCHOR_EXISTS` in
  `installer/registry.py:590`) — 694 of the 776 entries in the installed
  `0.64.33` manifest, so it is the majority case, not an edge case. Anchor
  gating affects only whether the file is installed; on refresh it is
  overwritten exactly like `install: "always"` (only `if-not-exists` targets
  are preserved, `installer/fileops.py:300`), so for editability it is
  vendored.
- Name the dual-ownership case explicitly, with `.github/copilot-instructions.md`
  as the worked example, so a run that sees its permanent hash drift can
  classify it as expected rather than investigating it again.
- State the disposition rule for a vendored defect: that local documentation is
  a legitimate terminal outcome and not a partial failure, that an upstream
  proposal requires explicit per-PR approval, and that a run must not edit a
  vendored file in place as a workaround.
- Specify what a task records when it takes the local-only route, so the
  unproposed upstream change stays discoverable: the owning pack, the file, the
  behaviour, and the fact that no upstream PR was opened.
- Do not weaken the authority boundary. This task documents the route; it does
  not grant, presume, or create a standing approval for upstream pull requests.
- Do not edit any vendored file as part of this task, whether it sits inside
  `.trellis/` or outside it. The deliverable is guidance recorded in
  `.trellis/spec/backend/quality-guidelines.md`, which is repo-owned and is the
  file the rest of this ordering cluster also writes.

## Acceptance Criteria

- [x] A run holding an arbitrary repository-relative path can determine
      ownership from the recorded procedure alone, without opening the three
      registries to work out which applies.
- [x] The procedure is verified against at least five real files with known and
      differing classifications — one `install: "always"`, one
      default-mode entry (no `install` key, i.e. `if-anchor-exists`), one
      `install: "if-not-exists"`, one `.template-hashes.json` entry, and one
      repo-owned file in no registry — and each yields the correct answer.
- [x] `.github/copilot-instructions.md` is classified as dual-owned with its
      drift named as expected.
- [x] The disposition rule states all four parts, verified present
      individually: local-only is terminal for a *record*; a local code change
      to a vendored file survives only until the next pack refresh; editing a
      vendored file in place as a workaround is forbidden; and an upstream PR
      needs explicit per-PR approval. The unqualified headline "local-only is
      terminal" alone does not satisfy this criterion.
- [x] At least two of the member tasks still in planning can have their bespoke
      constraint section replaced by a reference to the recorded guidance
      without losing information. Demonstrated, not asserted. (Archived members
      are not edited.)
- [x] The local-only record format names all four required fields — owning pack,
      file, behaviour, and the explicit statement that no upstream PR was opened
      — and a worked example shows each one filled in.
- [x] No file outside `.trellis/` is modified, and no file inside `.trellis/`
      that appears in `.trellis/.template-hashes.json` is modified. Verified by
      checking each changed path against that registry, since the vendored files
      this task is about live inside `.trellis/`.

## Out of scope

- Fixing any of the eight underlying defects. Each keeps its own task.
- Opening an upstream pull request against `sd-ai-command-pack` or Trellis.
- Building a tool or check that computes ownership. If the procedure turns out
  to want automating, that is a separate task with its own justification.
- Changing `sd-work-backlog`'s authority contract, which is itself a vendored
  file.

## Notes

- The table above is the canonical membership list for the vendored-artifact
  pattern. This task consolidates those eight; it is not itself a member of the
  pattern it describes. Earlier drafts of two member PRDs each carried their
  own running ordinal and both arrived at "seventh" — those ordinals have been
  removed in favour of pointing here.
- Membership has one source of truth: the table. The count does not — "eight"
  also appears in this PRD's prose, in this task's `task.json` description and
  notes, and in its `implement.jsonl`, and every one of those is derived. Adding
  a member means appending the row **and** reconciling each derived copy in the
  same edit; a member task must not carry its own ordinal at all. This is the
  weakness of the arrangement, stated rather than hidden: the table is
  authoritative, but nothing enforces that the derived copies agree with it.
- The status-collector row (added 2026-08-07; second-to-last in the table —
  the last row is `08-07-review-py-local-fork`) is the strongest argument that
  the pattern is worth writing down: the status collector cannot resolve a target
  pack version in a consumer repository (`collect_versions`,
  `scripts/sd-ai-command-pack-status.py:393-398` as of installed pack `0.64.3`;
  the file is `install: "always"`, so re-locate by symbol on any other version),
  so an installed pack behind the source checkout reports
  `packState: "installed"` with a null `targetPack` and emits no anomaly,
  follow-up, or recommendation about pack freshness. The top-line `SD status`
  verdict is not part of this — it comes from anomalies, working-tree state, and
  sync state (`render_local`,
  `scripts/sd-ai-command-pack-status.py:2095-2100`) — so do not restate this
  defect as "reports healthy". The collector is itself installed from the
  sd-pack, so the defect that hides vendored drift is vendored. It carries its
  own task, `08-07-status-collector-pack-drift`; this one still does not fix it.
- Planning depth: PRD-only. The deliverable is recorded guidance; the ownership
  procedure is a lookup, not a design.

## Relay log (2026-08-09)

First concrete upstream relays, filed from the PR #180 review cycle while this
task remains in planning; whatever route this task ultimately records should
absorb them as precedent:

- platypeeps/sd-ai-command-pack#397 — coordinator never forwards
  `--local-disposition` at an unchanged head with the default attempt id
  (verified against v0.64.32; consumer-side workaround documented in
  quality-guidelines).
- platypeeps/sd-ai-command-pack#398 — cache-env consumers export any all-caps
  pair; restore allowlist membership derived from `CACHE_ENV_KEYS` at runtime
  (A-080 follow-up, defense-in-depth).

Member update: 08-07-review-py-local-fork closed overtaken-by-events on
2026-08-09 (fork retired deliberately by the v0.64.32 refresh; its residual
upstream concern is #397's related note).

- Unfiled candidate (2026-08-09, run 548ccf3e iteration 3, PR #186, pack
  v0.64.33): a stale `--local-disposition` id fails the local stage *after*
  providers run but *before* the durable receipt persists
  (`sd-ai-command-pack-review-local.py`: `_apply_local_dispositions` at the
  merge step precedes `_atomic_json(receipt_path, ...)`), leaving a run dir
  that blocks retry ("attempt ... already exists without a reusable exact
  receipt") while the coordinator caches the `invalid` local outcome and
  replays it on every disposition-less rerun
  (`sd-ai-command-pack-review.py:1876` re-runs local only when dispositions
  are supplied). Recovery required deleting the incomplete run dir plus the
  coordinator's private state file. Upstream fix candidates: persist the
  receipt before applying dispositions, or treat a cached `invalid` local
  outcome as re-runnable. Route with the next relay batch.
- platypeeps/sd-ai-command-pack#399 — superseded review commands
  (`sd-review-local`, `sd-review-pr`) carry no supersession signal at the
  command choice point; catalog's "transitional until 0.62.0" horizon expired
  thirty-plus releases ago. Filed 2026-08-09 from
  `08-08-review-command-supersession-signal` (routing decision recorded in
  that task's `disposition.md`; not an instance-table enrollment).

## Completion evidence (2026-08-09, PR #187)

- Guidance recorded as "Vendored-Artifact Ownership And Upstream Route" in
  `.trellis/spec/backend/quality-guidelines.md` (commits 50e27e0, 60ca753).
- Procedure verified against six real files (both registry lookups match the
  recorded table): `scripts/sd-ai-command-pack-review.py` (always),
  `.claude/rules/sd-planning-adversarial-review.md` (default/if-anchor-exists),
  `.prism/rules.json` (if-not-exists), `.github/copilot-instructions.md`
  (dual-owned managed-block), `.trellis/scripts/common/task_store.py`
  (template-hashes), `.trellis/spec/backend/quality-guidelines.md`
  (no registry).
- Constraint sections replaced with references in
  `08-06-task-create-base-branch-default` and
  `08-06-task-json-trailing-newline` (both still in planning).
- AC "no file outside `.trellis/` modified": every changed path is under
  `.trellis/` and absent from `.trellis/.template-hashes.json` (verified by
  per-path jq lookup).
- Copilot review round 1: one finding (Registry A file is gitignored and
  machine-local) — verified true and fixed in 60ca753 (guarded snippet,
  prerequisite stated); round 2 clean.

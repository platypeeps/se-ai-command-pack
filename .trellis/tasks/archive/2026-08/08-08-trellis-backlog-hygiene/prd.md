# Trellis backlog hygiene: stale unmarked tasks, order collisions, committed detritus

## Goal

Bring the task tree back to a state where its metadata can be trusted: every
stale task carries a machine-readable reason or is archived, the `order` field
actually serializes the tasks that write the same spec file, and orphan
workspace artifacts are resolved without losing recorded history.

## Re-measurement (2026-08-09, execution session)

Re-enumerated from every active `task.json` before acting, as the Notes
require. Deltas from the 2026-08-08 measurement:

- **22 active tasks** (was 25), still all `planning`. The unmarked-stale set
  is unchanged: the seven `07-25-audit-*` tasks (createdAt 2026-07-25, no
  PARKED prefix, no `blocked`, no `order`).
- **`07-25-agent-artifacts` is already archived**
  (`archive/2026-08/07-25-agent-artifacts`), so the parent-closure
  requirement is satisfied by prior work; recorded here, no action.
- **Collision 10 self-resolved** (`08-06-ship-gate-ordering-docs` archived;
  `watch-coordinator-infra-classification` holds 10 alone). Collisions
  20 (`finalization-ordering-trap`, `task-json-trailing-newline`) and
  30 (`audit-registry-snapshot-ast-removal`, `prism-rules-lane-divergence`)
  remain.
- **Write-set enumerated** (tasks whose PRD requirements/acceptance criteria
  or `task.json` declare `quality-guidelines.md` as a deliverable) — seven
  writers: `vendored-artifact-upstream-route` (P2, order 5),
  `finalization-ordering-trap` (P2, 20 — its PRD acceptance criterion requires
  local documentation and its `task.json` declares cluster membership, so it
  is a writer, not a reader as an earlier draft of this section claimed),
  `prism-rules-lane-divergence` (P2, 30),
  `task-create-base-branch-default` (P2, 50),
  `watch-coordinator-infra-classification` (P3, 10),
  `task-json-trailing-newline` (P3, 20),
  `audit-registry-snapshot-ast-removal` (P3, 30, blocked).
  Readers (cite without writing) — all three of them:
  `audit-registry-snapshot-sd-twin`,
  `audit-registry-snapshot-layout-assumptions`, and this PRD itself.
  Ten citing PRDs total; classification evidence in `record.md`.
- **Order semantics constraint.** The ranker applies priority band before
  `order` (`sd-ai-command-pack-work-loop.py`, rank tie-breakers), so `order`
  serializes only within a band; a single 5..50 sequence cannot serialize
  writers that span P2 and P3. The effective landing sequence is therefore
  band-aware: P2 writers by order (5, 20, 30, 50), then P3 writers by order
  (10, 25, 40). `record.md` documents this sequence explicitly; unique order
  values across the whole write-set are still assigned so a human reading the
  numbers is not misled by cross-band duplicates.

Decided dispositions (rationale in `record.md`):

- Stale sweep: **schedule** the seven `07-25-audit-*` tasks (orders 110–170,
  lexical) — they are real, unblocked audit follow-ups; scheduling marks them
  deliberately deferred while keeping them actionable, where parking would
  silently remove them from the autonomous backlog and archiving would
  discard recorded intent.
- Order repair: `finalization-ordering-trap` keeps 20 (writer);
  `task-json-trailing-newline` 20 → 25 (resolves the cross-band 20/20
  duplicate; P3 band stays internally ordered 10 < 25 < 40);
  `audit-registry-snapshot-ast-removal` 30 → 40 (resolves the cross-band
  30/30 duplicate; blocked, lands last of its band anyway). Final
  assignments: P2 5/20/30/50, P3 10/25/40 — unique within each band and
  across the whole write-set.
- Metadata reconciliation: seven live `task.json` notes still carry the
  boilerplate claim "eleven active tasks edit
  .trellis/spec/backend/quality-guidelines.md" (measured before archives
  shrank the cluster). Replace that stale sequencing sentence in each with a
  pointer to this task's `record.md`, which becomes the single documented
  sequence source the Requirements demand. Parenthesized span claims are the
  same defect in another spelling — three exist ("landing cluster (5-70)" in
  the `toctou` and `work-loop-shipped-sha` notes, "cluster (10-70)" in the
  `vendored-artifact-upstream-route` note) — and each is replaced by a
  pointer to `record.md`, never by a restated span, so the numbers cannot
  drift stale again.
- Orphan workspace: **retain and annotate** (revised during execution). The
  originally decided migrate-then-remove disposition is unimplementable
  without weakening a deterministic gate: the vendored review preflight
  (`checkTrellisJournalRecords` in
  `scripts/sd-ai-command-pack-review-preflight.mjs`) enforces per-directory
  append-only journal history against the review base and offers no
  migration path, so any removal of `Sven Delmas/` reads as deleting
  historical Session 1 and fails the gate — demonstrated on this branch
  before this revision. The gate-compliant resolution keeps the journal
  byte-identical and appends an identity annotation to its scaffold
  `index.md` naming `sdelmas` as the sole active workspace. The missing
  migration path is a vendored-gate limitation routed as an upstream
  follow-up, not worked around locally.
- Index: replace the `(none yet)` Active Developers row with the current
  sdelmas snapshot plus a maintained-manually annotation.

## Problem

Measured 2026-08-08 (before this session filed new tasks):

- **25 active tasks, all `planning`, zero `in_progress`.** Eight are 14 days
  old (the `07-25-*` set). Only `07-25-agent-artifacts` (PARKED title prefix)
  carries a machine-readable reason for sitting still; the other seven
  14-day-old tasks have no marker distinguishing "deliberately deferred" from
  "forgotten". (The two `blocked: true` tasks in the backlog are the younger
  `08-04-audit-registry-snapshot-*` pair.)
- **The `order` field is unreliable exactly where it matters.** 14 of 25
  active PRDs reference `.trellis/spec/backend/quality-guidelines.md`; the
  subset that *writes* it (names it in requirements or acceptance criteria as
  a deliverable — smaller than 14, to be enumerated, since at least
  `08-04-audit-registry-snapshot-layout-assumptions` and
  `08-07-ci-no-preflight-lane` read it and deliberately opt out of ordering)
  is where landing sequence matters. But 12 of 25 tasks
  have no `order` at all (sorting as 0, ahead of everything ordered), and the
  values that exist collide in pairs: 10 twice (`08-06-ship-gate-ordering-docs`,
  `08-06-watch-coordinator-infra-classification`), 20 twice
  (`08-06-finalization-ordering-trap`, `08-06-task-json-trailing-newline`),
  30 twice (`08-04-audit-registry-snapshot-ast-removal`,
  `08-06-prism-rules-lane-divergence`).
- **Orphan workspace identity.** `.trellis/workspace/Sven Delmas/` (space in
  name) holds a non-empty 44-line journal and 40-line index from init day
  2026-07-17; `.trellis/.developer` says `name=sdelmas` and the string
  "Sven Delmas" appears nowhere else in the repo.
- **A PARKED parent outlived its children.** `07-25-agent-artifacts` lists
  five children — all archived as completed. The unpark condition was never
  re-evaluated after the subtree shipped.
- **The workspace index lies.** `.trellis/workspace/index.md` "Active
  Developers" still reads `| (none yet) |` after 139 recorded sessions.

## Requirements

- **Stale sweep.** For each unmarked stale task (definition below): park
  (title prefix), block (with `blockedOn`/`blockedReason`), archive as
  abandoned, or schedule (give it a real `order`). "Still want it, no marker"
  is not an outcome. Stale means `createdAt` on or before 2026-07-25
  (inclusive), read from `task.json` — the authoritative source, since dir
  date prefixes are demonstrably unreliable. As of filing this selects the
  seven unmarked `07-25-audit-*` tasks.
- **Order repair.** First enumerate the write-set: active tasks whose
  requirements or acceptance criteria name `quality-guidelines.md` (or another
  shared spec file) as a deliverable. Assign unique `order` values across that
  write-set only; read-only consumers stay unordered. Document the resulting
  sequence in one place rather than implying it.
- **Empty archive manifests: no action.** The 96 zero-byte jsonl files under
  `archive/` are a sanctioned resting state —
  `.trellis/spec/backend/quality-guidelines.md` ("Empty and scaffold-bearing
  are both acceptable resting states, and neither is a finding") — and mass
  deletion is exactly the churn that spec forbids. Recorded here so the
  observation is not re-filed.
- **Orphan workspace resolution.** The `Sven Delmas/` directory holds a
  non-empty journal; resolve the duplicate identity without losing recorded
  history. Straight deletion of recorded history is not an acceptable
  outcome, and neither is weakening the vendored append-only journal gate
  that (as discovered during execution) forbids removing the directory at
  all: the acceptable outcome is a retained, byte-identical journal plus an
  explicit identity annotation marking `sdelmas/` as the sole active
  workspace.
- **Parent closure.** Re-evaluate `07-25-agent-artifacts`: archive it, or
  re-scope it with a written reason it stays open despite all children being
  archived.
- **Index.** Either update the Active Developers table or annotate it as
  not-maintained; do not leave a table asserting "(none yet)" against 139
  sessions. (The wiring that should update it is vendored Trellis — fixing
  the automation is upstream and out of scope; correcting the data is not.)

## Acceptance Criteria

- [x] Zero active tasks with `createdAt` on or before 2026-07-25 lack all of:
      a PARKED prefix, a `blocked` marker, an `order` value — enumerated by
      reading `createdAt` from every active `task.json`, not by checking the
      ones named here.
- [x] The `quality-guidelines.md` write-set is enumerated in the task record
      (which tasks, by what criterion); within it, no two tasks share an
      `order` value and none lacks one; and the documented sequence in
      `record.md` is band-aware — it states that priority is applied before
      `order` and lists the effective landing sequence per priority band,
      not one flat cross-band number line.
- [x] Zero active `task.json` files still carry a stale cluster claim in
      either spelling — the "eleven active tasks" count or any parenthesized
      span — verified by
      `grep -lE "eleven active tasks|cluster \([0-9]+-[0-9]+\)" .trellis/tasks/*/task.json`
      returning nothing (task.json files only, so this PRD's own quotations
      do not self-match; the pattern form catches span variants such as
      "(5-70)" and "(10-70)" without enumerating them) — and each
      formerly-claiming note instead points to this task's `record.md`.
- [x] `.trellis/workspace/index.md` no longer asserts `(none yet)` under
      Active Developers: the row names the current developer identity from
      `.trellis/.developer` with a maintained-manually annotation.
- [x] `.trellis/workspace/Sven Delmas/` journal history is byte-identical to
      the review base (`git diff origin/main -- ".trellis/workspace/Sven
      Delmas/journal-1.md"` is empty), its `index.md` carries the identity
      annotation naming `sdelmas/` as the sole active workspace, and the
      vendored preflight's journal check passes.
- [x] `07-25-agent-artifacts` is archived or carries a written re-scope
      reason.
- [x] Archive integrity: nothing under `archive/` was modified or deleted
      (verified from the diff stat).

## Out of scope

- Executing any of the stale tasks — this is metadata hygiene, not delivery.
- Fixing Trellis's own index-update or journal automation (vendored;
  upstream).
- The `write_json` trailing-newline defect (`08-06-task-json-trailing-newline`)
  — expect its diff noise when touching `task.json` files and do not "fix" it
  here.
- Journal content or rotation (working as designed; 3 journals, max-2000-line
  policy honored).

## Notes

- Sourced from the 2026-08-08 deep review (Trellis hygiene lane). Counts
  (25 active / 112 archived, order collisions) were enumerated from the
  filesystem that day; re-enumerate before acting, since this session has
  since filed additional `08-08-*` tasks.
- Adversarial review (2026-08-08) removed two originally-planned deliverables:
  zero-byte archive manifest deletion (contradicts the sanctioned resting
  state in `quality-guidelines.md`) and unconditional orphan-dir deletion
  (would destroy a non-empty journal).
- Date prefixes are not reliable ages: two `08-06-*` tasks first reached git
  on 08-07. Use git history where age matters.
- Lightweight; PRD-only planning depth (no design.md/implement.md needed).
  All mutations are data edits inside `.trellis/`.

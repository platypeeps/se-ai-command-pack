# Trellis backlog hygiene: stale unmarked tasks, order collisions, committed detritus

## Goal

Bring the task tree back to a state where its metadata can be trusted: every
stale task carries a machine-readable reason or is archived, the `order` field
actually serializes the tasks that write the same spec file, and orphan
workspace artifacts are resolved without losing recorded history.

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
  non-empty journal; migrate or archive its content (fold into the `sdelmas/`
  journal or the archive) before removing the duplicate directory. Straight
  deletion of recorded history is not an acceptable outcome.
- **Parent closure.** Re-evaluate `07-25-agent-artifacts`: archive it, or
  re-scope it with a written reason it stays open despite all children being
  archived.
- **Index.** Either update the Active Developers table or annotate it as
  not-maintained; do not leave a table asserting "(none yet)" against 139
  sessions. (The wiring that should update it is vendored Trellis — fixing
  the automation is upstream and out of scope; correcting the data is not.)

## Acceptance Criteria

- [ ] Zero active tasks with `createdAt` on or before 2026-07-25 lack all of:
      a PARKED prefix, a `blocked` marker, an `order` value — enumerated by
      reading `createdAt` from every active `task.json`, not by checking the
      ones named here.
- [ ] The `quality-guidelines.md` write-set is enumerated in the task record
      (which tasks, by what criterion); within it, no two tasks share an
      `order` value and none lacks one.
- [ ] `.trellis/workspace/Sven Delmas/` no longer exists, and its journal
      content is demonstrably preserved (named location, verifiable by
      reading it).
- [ ] `07-25-agent-artifacts` is archived or carries a written re-scope
      reason.
- [ ] Archive integrity: nothing under `archive/` was modified or deleted
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
- Lightweight; PRD-only. All mutations are data edits inside `.trellis/`.

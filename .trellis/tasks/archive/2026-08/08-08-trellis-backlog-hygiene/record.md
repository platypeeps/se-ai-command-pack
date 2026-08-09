# Backlog hygiene record (2026-08-09)

Evidence record for `08-08-trellis-backlog-hygiene`. This file is the single
documented source for the `quality-guidelines.md` write-set and its landing
sequence; live `task.json` notes point here instead of restating counts or
spans.

## Write-set classification

Criterion (literal): an active task is a **writer** when its PRD requirements
or acceptance criteria, or its `task.json`, declare
`.trellis/spec/backend/quality-guidelines.md` as a deliverable; a **reader**
cites the file without delivering changes to it. Ten active PRDs cite the
file (enumerated by `grep -l quality-guidelines .trellis/tasks/*/prd.md`).

Writers (seven):

| Task | Priority | Order | Note |
| --- | --- | --- | --- |
| `08-07-vendored-artifact-upstream-route` | P2 | 5 | defines the shared ownership section others extend |
| `08-06-finalization-ordering-trap` | P2 | 20 | writer per its own AC + task.json (an earlier draft misclassified it as a reader) |
| `08-06-prism-rules-lane-divergence` | P2 | 30 | |
| `08-06-task-create-base-branch-default` | P2 | 50 | |
| `08-06-watch-coordinator-infra-classification` | P3 | 10 | |
| `08-06-task-json-trailing-newline` | P3 | 25 | was 20; moved to clear the cross-band 20/20 duplicate |
| `08-04-audit-registry-snapshot-ast-removal` | P3 | 40 | was 30; blocked on `-sd-twin`, lands last of its band regardless |

Readers (three, citation-only): `08-04-audit-registry-snapshot-sd-twin`,
`08-04-audit-registry-snapshot-layout-assumptions`, and the
`08-08-trellis-backlog-hygiene` PRD itself.

## Landing sequence (band-aware)

The work-loop ranker applies the priority band **before** `order`
(`scripts/sd-ai-command-pack-work-loop.py`, rank tie-breakers), so `order`
serializes only within a band. One flat number line across the write-set
cannot serialize P2 and P3 writers against each other. The effective
sequence is:

1. **P2 band, by order**: vendored-artifact-upstream-route (5) →
   finalization-ordering-trap (20) → prism-rules-lane-divergence (30) →
   task-create-base-branch-default (50). The non-member P2 tasks
   `08-05-audit-update-source-trust-toctou` (1) and
   `08-06-work-loop-shipped-sha-after-branch-delete` (2) precede the band's
   writers by explicit choice.
2. **P3 band, by order**: watch-coordinator-infra-classification (10) →
   task-json-trailing-newline (25) → audit-registry-snapshot-ast-removal
   (40, blocked; enters only when its blocker clears).

Order values are nevertheless unique across the whole write-set (5, 10, 20,
25, 30, 40, 50) so a human reading the raw numbers is not misled by
cross-band duplicates.

## Stale-claim reconciliation

Nine live `task.json` notes carried stale cluster claims — seven with the
"eleven active tasks edit" count and three parenthesized spans ("(5-70)"
twice, "(10-70)" once; `vendored-artifact-upstream-route` had both
spellings). Each stale sentence was replaced with a pointer to this record;
none restates a count or span, so the numbers cannot drift stale again.
Verification: `grep -lE "eleven active tasks|cluster \([0-9]+-[0-9]+\)"
.trellis/tasks/*/task.json` returns nothing.

## Stale sweep disposition

The seven unmarked stale tasks (`createdAt` 2026-07-25, no PARKED prefix, no
`blocked`, no `order`) were **scheduled** — real, unblocked audit follow-ups
given orders 110–170 in lexical task-ID order, marking them deliberately
deferred while keeping them in the autonomous backlog. Parking would have
removed them silently; archiving would have discarded recorded intent.

| Task | Order |
| --- | --- |
| `07-25-audit-dependency-hygiene` | 110 |
| `07-25-audit-generated-catalog-location` | 120 |
| `07-25-audit-release-versioning-policy` | 130 |
| `07-25-audit-repo-tooling-ownership` | 140 |
| `07-25-audit-skill-review-internals` | 150 |
| `07-25-audit-test-hermeticity` | 160 |
| `07-25-audit-workflow-entrypoint-routing` | 170 |

## Other dispositions

- **Parent closure**: `07-25-agent-artifacts` was already archived
  (`archive/2026-08/07-25-agent-artifacts`) before execution; requirement
  satisfied by prior work, no action.
- **Orphan workspace**: retained and annotated, not removed. The vendored
  review preflight (`checkTrellisJournalRecords`) enforces per-directory
  append-only journal history and offers no migration path — a
  migrate-then-remove attempt on this branch failed the gate (removal of
  `Sven Delmas/` read as deleting historical Session 1). The journal is
  kept byte-identical to the review base and the scaffold `index.md` now
  carries an identity annotation naming `sdelmas/` as the sole active
  workspace. The missing migration path is routed as an upstream follow-up
  rather than worked around.
- **Active Developers index**: `(none yet)` row replaced with the current
  `sdelmas` snapshot (150 sessions, journal-3.md, from `sdelmas/index.md`)
  plus a maintained-manually annotation.
- **Zero-byte archive manifests**: no action — sanctioned resting state per
  `quality-guidelines.md`; nothing under `archive/` was touched.

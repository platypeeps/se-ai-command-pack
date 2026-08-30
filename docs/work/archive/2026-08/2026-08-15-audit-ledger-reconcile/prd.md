---
title: Reconcile the stale sd-audit-repo ledger against current HEAD
status: done
created: 2026-08-15
branch: task/audit-ledger-reconcile
---
# Reconcile the stale sd-audit-repo ledger against current HEAD

## Goal

Make `.trellis/audit/ledger.md` describe the repository as it is, so its open
set is a backlog a human or the autonomous work loop can act on without
re-deriving every finding first.

## Problem

Every one of the 44 findings in the ledger carries `status: open`. A sample of
27, re-checked against their own recorded evidence at HEAD `564d4a2`, found 20
already fixed, 3 still present, and 4 that a grep cannot settle. Examples of
the fixed group, each verified rather than inferred:

- A-020 claims no coverage floor; `Makefile:106` runs
  `coverage report --fail-under=80`.
- A-026 claims the unreferenced repo-root skill-review wrapper under `scripts/`
  is dead code; that file no longer exists.
- A-039 claims no concurrency group; `.github/workflows/tests.yml:13` has one.
- A-001 claims `git ls-files .claude` returns 0; it returns 107.

The status field was never written back when the fixing pull request merged.
`sd-audit-repo` owns this file and is documented as maintaining it across
sessions, but nothing in the merge path updates it.

The cost is not cosmetic. The ledger is the repository's only durable record of
audit findings, and a consumer cannot distinguish a finding that was fixed six
merges ago from one nobody has touched. Full detail in
`research/ledger-drift-sample.md`.

## Requirements

1. Every finding in the ledger is re-checked against the evidence bullets it
   records, at the current HEAD.
2. Each finding's `status` is rewritten using the vocabulary the owning skill
   declares — `open`, `fixed`, `regressed` — and no other value.
   `.claude/skills/sd-audit-repo/SKILL.md:246` fixes this set, so the
   "real, but the remaining work is upstream" case cannot be a status and is
   expressed in `notes:` instead.
3. Each finding carries a dated verification note on its `notes:` line
   recording what was observed and how, so the next reader does not repeat
   this work. `notes:` is the schema's human-editable field.
4. Existing unknown or human-authored lines inside an entry are preserved, per
   the skill's update rule.
5. A finding is marked `fixed` only on inverted evidence — the cited construct
   is gone, moved, or reversed. An archived task with a matching name is
   corroboration, never proof, because tasks are also archived as won't-do.
6. Findings that cannot be settled by a mechanical check stay `open` and say so
   in `notes:`, rather than being guessed in either direction.
7. Findings whose remaining work is upstream-only stay `open` and name the
   blocked Trellis task that owns them, so the two records agree.
8. The rewrite is confined to `.trellis/audit/ledger.md` and this task's own
   artifacts, and lands as **two separate commits**: the ledger alone, and the
   task artifacts alone. `.claude/skills/sd-audit-repo/SKILL.md:253-259`
   states a commit mixing `.trellis/audit/**` with `.trellis/tasks/**` cannot
   be journaled or finalized and cannot be undone once published.

## Acceptance criteria

- [x] Every one of the 44 findings has a status in `{open, fixed, regressed}`
      and a dated `notes:` verification line; no finding retains an unexamined
      `open`.
- [x] A re-check script, committed under this task, re-runs the inverted-evidence
      assertion for every finding marked `fixed` and exits non-zero on any
      contradiction. It reports zero contradictions.
- [x] Every finding left `open` names either the construct still present at a
      current `file:line`, the blocked task that owns it, or the reason it
      needs a human read.
- [x] Findings whose remaining work is upstream cross-reference the blocked
      task that owns them, and those tasks' `blockedOn` text is unchanged.
- [x] No entry loses a pre-existing line the reconciliation did not
      deliberately rewrite.
- [x] `make check` passes.
- [x] The ledger commit's `git show --stat` lists `.trellis/audit/ledger.md`
      and nothing else; the task-artifact commit lists no `.trellis/audit/`
      path.

## Non-goals

- Fixing any finding. This task changes bookkeeping only. Findings confirmed
  still-present stay open and become the next selectable work.
- Running a fresh `sd-audit-repo` pass or discovering new findings. The set
  stays at A-001..A-044.
- Changing the ledger's schema beyond the status vocabulary and the
  verification note. No reformatting, no re-ordering, no severity re-scoring.
- Unarchiving or re-opening any Trellis task.

## Open question

The status write-back gap will recur on the next merge unless something closes
it. That is a separate change to the merge path and is deliberately out of
scope here; if the reconciliation confirms the gap is systemic, it becomes a
follow-up task rather than scope creep into this one.

## References

Research notes that lived beside this item's Trellis record and were not carried
into docs/work. Recover the bodies from git history under `.trellis/tasks/archive/2026-08/08-15-audit-ledger-reconcile`:

- research/ledger-drift-sample.md
- scripts/apply_reconciliation.py
- scripts/recheck.py

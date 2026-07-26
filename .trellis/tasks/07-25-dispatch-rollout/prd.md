# Roll out dispatch protocols to remaining fan-out skills

Parent: `.trellis/tasks/07-25-agent-artifacts` (Tier 1 rollout). Settled inputs: parent
`design.md` section 1 and `research/cross-platform-agent-support.md`.

## Goal

Extend the validated pilot dispatch pattern to the remaining high-fan-out skills:
se-digest (per document/thread), se-feedback (per review), se-scan (per player/vendor),
se-video-notes (per video), se-red-team (per attack lens: assumptions, incentives,
security, privacy, misuse).

## Requirements

- R1: Apply the exact pattern validated in 07-25-dispatch-pilot (capability-first prose,
  inline fallback, orchestrator-owned IDs/dedup/verification, runtime-routing.md
  governance). Divergences from the pilot pattern require a recorded reason.
- R2: se-red-team dispatch must compose with its `fresh-session` isolation semantics from
  07-25-runtime-profile-gaps (workers must not inherit the parent's conclusions).
- R3: Per-skill unit definitions and result contracts are explicit in each dispatch
  section; final-report contracts unchanged.
- R4: Skills NOT in scope stay untouched; anti-parallel-by-design skills (se-socratic-review)
  are explicitly out of scope.

## Acceptance Criteria

- [ ] All five skills carry dispatch sections; neutrality lint + section validation pass.
- [ ] Generator `--check` clean; version bump + changelog.
- [ ] A short pattern-conformance note (what matched the pilot, what diverged and why) is
      recorded in this task before archive.

## Dependencies / order

- BLOCKED until 07-25-dispatch-pilot is completed and its pattern reviewed.
- Composes with 07-25-runtime-profile-gaps for se-red-team (that task should land first).

## Notes

- Mechanical rollout; lightweight per-skill, but review each skill's unit boundaries.

## Cross-program coordination (2026-07-25 review)

- Body-churn sequencing (A-006): `07-25-audit-skill-arg-vocabulary` renames arguments
  across all 53 skill bodies, including this task's targets. Preferred order: vocabulary
  first, then write dispatch sections in the canonical vocabulary. If this task lands
  first, expect a rename rebase.
- Gates first (A-035/A-040, A-036, A-020, A-007): the audit gate tasks are cheap and
  directly protect this payload wave; land them before the wave where practical.

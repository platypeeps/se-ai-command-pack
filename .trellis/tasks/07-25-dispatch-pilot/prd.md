# Add sub-agent dispatch to se-research and se-fact-check

Parent: `.trellis/tasks/07-25-agent-artifacts` (Tier 1 pilot). Settled inputs: parent
`design.md` section 1 and `research/cross-platform-agent-support.md`.

## Goal

Pilot the capability-first dispatch pattern in the two highest-value fan-out skills:
se-research (per search lane / per claim verification / per disconfirmation query) and
se-fact-check (per claim), so sub-agent-dispatch platforms parallelize while inline
platforms keep today's sequential outcome.

## Requirements

- R1: Each skill gains a dispatch section modeled on the sd-audit-repo protocol: "on
  sub-agent dispatch platforms, run these units in parallel; on inline platforms, work
  sequentially in one context." No host product names in canonical bodies (neutrality
  lint must pass).
- R2: The parent/orchestrator context owns unit IDs, deduplication, verification, and the
  final report; workers receive the smallest complete input set with explicit exclusions
  (runtime-routing.md doctrine: concurrency cap, no recursive spawning, bounded authority).
- R3: Inline fallback preserves the current workflow steps and final-report contract
  exactly; dispatch is an execution strategy, not a scope change.
- R4: Works with host BUILT-IN sub-agents only; must not depend on named SE worker agents
  (that enhancement lands in 07-25-worker-agents).
- R5: Section structure keeps passing REQUIRED_SECTIONS ordering validation.

## Acceptance Criteria

- [ ] se-research and se-fact-check canonical bodies contain the dispatch section with
      inline fallback; `BANNED_PHRASE_PATTERN` lint and section validation pass.
- [ ] Generator `--check` clean; regenerated Claude overlays byte-stable otherwise.
- [ ] Final-report contracts unchanged (same sections, same evidence rules).
- [ ] Version bump + dated changelog entry.

## Dependencies / order

- Independent of 07-25-agent-artifact-kind and 07-25-worker-agents (prose-only).
- 07-25-dispatch-rollout MUST wait for this pilot to be validated.

## Notes

- Lightweight-to-medium task; PRD + brief design note likely sufficient.

## Cross-program coordination (2026-07-25 review)

- Body-churn sequencing (A-006): `07-25-audit-skill-arg-vocabulary` renames arguments
  across all 53 skill bodies, including this task's targets. Preferred order: vocabulary
  first, then write dispatch sections in the canonical vocabulary. If this task lands
  first, expect a rename rebase.
- Gates first (A-035/A-040, A-036, A-020, A-007): the audit gate tasks are cheap and
  directly protect this payload wave; land them before the wave where practical.

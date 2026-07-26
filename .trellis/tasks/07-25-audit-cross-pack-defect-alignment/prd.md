# Cross-pack defect-class alignment

## Goal

The se- and sd-ai-command-pack audits independently found the same defect classes. Make
that convergence systematic: when a class is fixed in one pack, the twin gets swept, and
the classes live in shared spec guidance so new code stops reintroducing them.

## Background (evidence of convergence)

- Subprocess timeout bounds: SE ledger A-013 ↔ SD ledger A-003.
- Per-run recomputation / missing memoization: SE A-029 ↔ SD A-024.
- Per-target process spawns: SE A-030 ↔ SD A-014.
- .opencode npm ecosystem unmonitored / drifting pins: SE A-031/A-032/A-033 ↔ SD A-018/A-019.
- Shared-helper gaps in shipped scripts: SE skill_review duplication (A-009) ↔ SD A-013.

## Requirements

- R1: Produce the class-pair mapping table (seed above; verify against both ledgers) and
  commit it where both packs' audits can cite it.
- R2: Add a spec entry per class to this repo's .trellis/spec (e.g. quality-guidelines):
  the rule, the canonical safe pattern, and the ledger IDs it retires.
- R3: File the SD-side spec counterpart as a companion task in sd-ai-command-pack when
  this task starts (cross-repo edits do not happen from this task directly).
- R4: Twin-sweep rule: fixing a classed finding in either pack requires checking the twin
  ledger entry and updating its notes — write this into both packs' audit skill guidance
  only if the skill owners agree; otherwise record it in spec.

## Acceptance Criteria

- [ ] Mapping table committed and referenced from the audit ledger preamble or spec.
- [ ] Spec entries exist for each class with the safe pattern.
- [ ] SD companion task filed; both ledgers' affected entries cross-note their twin.

## Notes

- Opportunity task from the 2026-07-25 cross-plan review (parallel-analysis reconciliation).
- Lightweight: PRD-only is acceptable.

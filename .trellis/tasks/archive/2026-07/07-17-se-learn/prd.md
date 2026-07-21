# Implement se-learn

## Goal

Build and adapt a mastery-oriented learning path from a stated capability goal
and an honestly assessed baseline.

## Requirements

- Resolve learning goal, baseline, constraints, available time, preferred modes,
  and observable mastery signals.
- Diagnose rather than assume prior knowledge; label self-report versus demonstrated ability.
- Sequence concepts, worked examples, retrieval practice, exercises, projects,
  checkpoints, and spaced review.
- Adapt the path from errors and misconceptions without lowering the outcome silently.
- Reuse `se-explain`, `se-study-guide`, and `se-socratic-review` as optional capabilities.

## Acceptance Criteria

- [ ] Every stage has a measurable learning outcome and checkpoint.
- [ ] The path changes when demonstrated evidence contradicts the baseline.
- [ ] Tests cover beginners, experienced learners with gaps, time limits, and inaccessible materials.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Credentialing, grading authority, or guaranteeing mastery on a schedule.

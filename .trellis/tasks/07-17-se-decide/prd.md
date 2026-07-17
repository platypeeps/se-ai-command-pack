# Implement se-decide

## Goal

Add a decision workflow that turns known options, constraints, criteria, and evidence into a recommendation with tradeoffs, confidence, reversibility, missing evidence, and next actions.

## Background

The existing skills gather, compare, and synthesize information but do not own
the next step of making a bounded decision from already-known alternatives.

## Requirements

- Trigger on consequential choices where the user wants a defensible
  recommendation rather than more open-ended research.
- Accept the decision question, known options, criteria, constraints, deadline,
  and available evidence; expose assumptions when inputs are incomplete.
- Evaluate every option on consistent criteria and separate sourced facts from
  inference and judgment.
- Identify the preferred option, meaningful tradeoffs, confidence,
  reversibility, missing evidence, and the smallest useful next step.
- Route broad candidate discovery to `se-scan`, evidence gathering to
  `se-research`, and supplied-document synthesis to `se-digest` instead of
  reproducing those workflows.
- Remain read-only and never execute the selected option without a separate
  user request.
- Follow the canonical skill structure, framework-neutrality rules, shared
  source standards when evidence is used, and release workflow.

## Acceptance Criteria

- [ ] The skill has a precise trigger and explicit non-trigger boundaries for
      `se-scan`, `se-research`, and `se-digest`.
- [ ] Its final report contains decision, option comparison, tradeoffs,
      confidence, reversibility, missing evidence, and next action.
- [ ] Unknown or weak evidence is visible and cannot be silently upgraded into
      fact.
- [ ] Tests cover structure, registry/manifest generation, shared references,
      and framework-neutral wording.
- [ ] README/operator documentation, manifest, version, and changelog are
      updated through the normal release process.

## Out of Scope

- Discovering an entire market from scratch.
- Building a detailed execution plan.
- Acting on the recommendation.

# Implement se-evaluate

## Goal

Evaluate a defined subject against an explicit, justified rubric and produce an
evidence-backed judgment with uncertainty.

## Requirements

- Resolve subject, purpose, audience, rubric, weights, thresholds, evidence, and comparator.
- Validate criteria for relevance, independence, and measurable interpretation.
- Record evidence, score/judgment, confidence, strengths, deficiencies, missing
  evidence, and highest-value improvements per criterion.
- Avoid numeric scores when evidence or rubric is qualitative; run sensitivity
  analysis when weights materially control the outcome.
- Keep evaluation separate from adversarial `se-red-team` and choice-making `se-decide`.

## Acceptance Criteria

- [ ] Every judgment maps to criterion and evidence.
- [ ] Missing evidence and failed criteria remain distinct.
- [ ] Tests cover biased rubrics, dependent criteria, qualitative evidence, and weight sensitivity.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Certification, personnel scoring, or making the final decision.

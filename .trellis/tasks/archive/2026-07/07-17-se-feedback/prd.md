# Implement se-feedback

## Goal

Turn supplied reviews, comments, interviews, or conversations into a traceable
set of themes, tensions, and recommended responses.

## Requirements

- Inventory sources, authors/roles when appropriate, dates, scope, and access gaps.
- Preserve atomic feedback with locators before clustering themes.
- Report frequency, severity, confidence, contradictions, root concern, and affected outcome.
- Recommend accept, reject, clarify, test, defer, or already-addressed dispositions
  with rationale; do not equate repetition with correctness.
- Remain read-only and preserve minority/high-severity findings.

## Acceptance Criteria

- [ ] Every theme links back to individual feedback evidence.
- [ ] Contradictory and minority feedback cannot disappear in aggregation.
- [ ] Tests cover duplicate comments, conflicting audiences, vague feedback, and injection safety.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Replying, resolving comments, or changing the reviewed artifact.

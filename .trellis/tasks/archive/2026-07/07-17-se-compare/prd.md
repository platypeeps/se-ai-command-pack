# Implement se-compare

## Goal

Compare supplied alternatives rigorously without prematurely turning the analysis
into a recommendation.

## Requirements

- Resolve alternatives, use case, constraints, criteria, evidence window, and audience.
- Use one fair comparison frame and surface asymmetric or missing evidence.
- Present strengths, weaknesses, tradeoffs, disqualifiers, uncertainties, and
  sensitivity to changed assumptions.
- Keep factual comparison separate from user values and decision weighting.
- Hand an accepted comparison to `se-decide` when a choice is requested.

## Acceptance Criteria

- [ ] Alternatives are judged against the same stated criteria.
- [ ] Missing data cannot silently become a negative score.
- [ ] Tests cover incomparable options, biased criteria, stale evidence, and no clear winner.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Final recommendations, procurement, or implementation planning.

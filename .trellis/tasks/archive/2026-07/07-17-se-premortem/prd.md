# Implement se-premortem

## Goal

Stress-test an accepted plan before execution by assuming failure and identifying
preventable or containable causes.

## Requirements

- Require a plan/objective, context, constraints, horizon, and known assumptions.
- Generate failure modes across technical, operational, people, dependency,
  incentive, security, market, and external lanes as relevant.
- Rank likelihood, impact, detectability, and evidence confidence without fake precision.
- Define leading indicators, prevention, contingency, decision points, owners
  only when supplied, and stop conditions.
- Preserve low-likelihood catastrophic cases separately from ordinary ranking.

## Acceptance Criteria

- [ ] Every mitigation maps to a named failure mode and observable indicator.
- [ ] Speculative scenarios remain labeled and cannot become predicted outcomes.
- [ ] Tests cover thin plans, correlated failures, catastrophic tails, and no mitigation.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Replacing security threat modeling, incident response, or final go/no-go authority.

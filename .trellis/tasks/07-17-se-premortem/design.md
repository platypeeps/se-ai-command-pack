# Implement se-premortem Design

## Overview

Add `se-premortem` under Improve as a prospective stress test for an accepted
plan. It assumes failure to uncover preventable or containable causes while
keeping scenarios explicitly speculative and preserving catastrophic tail risks.

## Proposal

Require the accepted plan/objective, context, constraints, horizon, assumptions,
dependencies, and available evidence. Define what failure means before generating
scenarios and record any thin-plan gaps that limit analysis.

Generate materially distinct failure modes across relevant technical, operational,
people, dependency, incentive, security, market, and external lanes. Identify
correlated/common-cause failures. Classify each scenario as evidence-supported,
analogical, or speculative.

Rank likelihood, impact, detectability, and evidence confidence with ordinal bands
and rationale rather than fake precision. Preserve low-likelihood catastrophic
cases in a separate tail-risk view even when aggregate rank is low.

For each mode define leading indicators, prevention, contingency, decision points,
stop conditions, residual risk, and owner only when supplied. Every mitigation
maps to a failure mode and observable indicator; modes with no viable mitigation
remain explicit and may require plan revision or acceptance.

## Boundaries And Non-Goals

- Do not replace threat modeling, incident response, or final go/no-go authority.
- Do not present imagined scenarios as predictions or facts.
- Do not fabricate owners or precise probabilities.
- Do not hide unmitigated or catastrophic tail risks in an average score.

## Affected Files

- Canonical skill, Improve-family registration, risk/source references, manifest,
  fixtures/tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Thin plans can produce generic risks; surface missing plan detail first.
- Failure modes may be correlated; do not score them as independent.
- Mitigations can introduce new risks; record tradeoffs and residuals.
- No-mitigation cases need escalation/acceptance, not invented controls.
- Overlong lists reduce usefulness; prioritize while retaining tail risks.

## Validation

- Pin failure definition, lane coverage, evidence class, ordinal ranking, correlated
  failures, tail-risk preservation, mitigation/indicator mapping, and owner authority.
- Test thin plans, correlated failures, catastrophic tails, no mitigation, invented
  precision, plan contradictions, and injection.
- Run generation, focused tests, full checks, and diff check.

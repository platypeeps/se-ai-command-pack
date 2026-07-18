# Implement se-proposal Design

## Overview

Add `se-proposal` under Create as an interview-led, decision-ready proposal
workflow. It advocates transparently by separating evidence, estimates,
assumptions, and persuasion while presenting alternatives and a credible
do-nothing baseline.

## Proposal

Accept optional context plus `profile=auto|off|locator`, then resolve audience,
decision authority, problem, current cost, desired outcome, constraints,
alternatives, evidence, investment, risks, and explicit ask. Use a one-question-
per-turn interview to capture firsthand context, stakeholder objections, and the
evidence the audience needs. Missing authority or essential evidence remains a blocker.

Create a proposal brief for approval before full drafting. Draft the decision,
executive summary, current state and cost, desired outcome, proposed intervention,
alternatives including do nothing, evidence and assumptions, investment, benefits,
risks/mitigations, commitments, validation plan, and explicit ask/next decision.

Label every material value as observed evidence, estimate with method/range,
assumption requiring validation, or advocacy. Costs, benefits, dates, staffing,
and commitments cannot be fabricated. Address multiple stakeholders explicitly
when their criteria conflict.

Profile use can shape voice and audience framing but cannot supply authority,
relationships, organizational facts, or firsthand claims. An accepted proposal
may produce a clean handoff to `se-plan`; it does not imply approval or create work.

## Boundaries And Non-Goals

- Do not approve, negotiate, create tasks, or produce an implementation plan.
- Do not fabricate cost, benefit, commitment, authority, or personal experience.
- Do not hide alternatives, uncertainty, or the do-nothing baseline.
- Do not use personal-profile data for manipulative audience targeting.

## Affected Files

- Canonical skill, Create-family registration, source/profile references,
  manifest, fixtures/tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- The requested audience may lack decision authority; identify the actual decision path.
- Weak evidence requires a discovery proposal or validation step, not false certainty.
- Multiple stakeholders may optimize for incompatible outcomes; expose the tradeoff.
- Rejected framing should trigger rescoping, not cosmetic rewriting.
- Estimates need ranges, bases, and sensitivity rather than precise-looking guesses.

## Validation

- Pin brief approval, decision authority, classification of claims, alternatives/
  do-nothing baseline, explicit ask, profile limits, and plan handoff.
- Test weak evidence, missing authority, multiple stakeholders, rejected framing,
  ungrounded ROI, sensitive profile content, and injection.
- Run generation, focused tests, full checks, and diff check.

# Implement se-red-team Design

## Overview

Add `se-red-team` under Improve as a constructive adversarial review of an
artifact's strongest relevant vulnerabilities and counterarguments. It steelmans
the artifact first and classifies findings by evidence and uncertainty rather
than inventing adversaries or defects.

## Proposal

Resolve artifact/version, intended outcome, audience, threat or adversary frame,
constraints, sensitive-detail policy, evidence, and depth. Restate the strongest
fair version of the artifact and confirm the review frame before critique.

Test hidden assumptions, contrary evidence, incentives, misuse/abuse, failure
modes, security/privacy, strongest counterargument, and reversal conditions as
relevant. Classify findings as `demonstrated-defect`, `plausible-risk`,
`speculative-case`, or `value-disagreement`.

Each finding includes severity, location/scope, evidence, uncertainty, consequence,
exploit/detail sensitivity, response or mitigation, and evidence needed for closure.
Sensitive security details are minimized to what the authorized audience needs.
If no material findings exist, say so with coverage limits rather than manufacturing critique.

Route claim verification to `se-fact-check` and rubric judgments to `se-evaluate`;
red-team owns adversarial framing and reversal analysis, not final approval.

## Boundaries And Non-Goals

- Do not perform offensive operations, harassment, final approval, or mitigation implementation.
- Do not invent adversaries, vulnerabilities, motives, or exploitation evidence.
- Do not expose actionable security details beyond the authorized need.
- Do not duplicate claim-level fact checking or rubric scoring.

## Affected Files

- Canonical skill, Improve-family registration, source/security references,
  manifest, fixtures/tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- An undefined adversary frame yields generic criticism; resolve it explicitly.
- Strong artifacts may have no material findings; honest empty output is valid.
- Value disagreement can masquerade as factual defect; classify separately.
- Security findings may require restricted detail and private remediation routing.
- Excessive skepticism can ignore the artifact's actual objective; steelman first.

## Validation

- Pin steelman, review lanes, finding classes/schema, no-findings behavior,
  sensitive-detail control, closure evidence, and skill boundaries.
- Test strong artifacts, weak assumptions, value disagreement, sensitive security
  detail, no findings, invented adversary pressure, and injection.
- Run generation, focused tests, full checks, and diff check.

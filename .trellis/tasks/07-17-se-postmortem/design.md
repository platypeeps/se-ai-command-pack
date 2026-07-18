# Implement se-postmortem Design

## Overview

Add `se-postmortem` under Improve as a formal, blameless corrective-analysis
workflow. It builds an evidence-linked account of impact, timeline, contributing
conditions, causes, safeguard failures, and verifiable recurrence-reduction actions.

## Proposal

Resolve event scope, expected/actual outcome, timeline window/timezone, impact,
participants or roles, sources, audience, sensitivity, and authority. Inventory
source coverage and conflicts before analysis.

Build an evidence-linked timeline with observation and source confidence. Keep
`observation`, `interpretation`, `contributing-factor`, `root-cause`, and
`counterfactual` distinct. A root-cause claim requires a defensible causal mechanism
and evidence; temporal correlation and hindsight are insufficient.

Analyze detection, response, recovery, systemic conditions, decision/control
context, and why safeguards failed or were absent. Blameless means focusing on
conditions and controls while accurately recording accountable decisions; it does
not erase ownership or impact.

Produce corrective/preventive actions mapped to causes/control gaps, with owners
and dates only when approved, dependencies, verification signals, expected risk
reduction, and residual risk. Record disputed findings and missing evidence.

## Boundaries And Non-Goals

- Do not conduct incident response, discipline people, reach legal conclusions, or execute actions.
- Do not label correlation, hindsight, or human error alone as root cause.
- Do not invent owners, dates, impact, or complete source coverage.
- Do not replace lighter `se-retro` reflection.

## Affected Files

- Canonical skill, Improve-family registration, source/sensitivity references,
  manifest, incident fixtures/tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Incomplete/conflicting timelines require competing accounts and confidence labels.
- Sensitive incidents need audience-specific redaction without changing findings.
- “Human error” can terminate inquiry prematurely; inspect enabling conditions.
- Corrective actions can become vague promises; require observable verification.
- Owner assignment may exceed the user's authority; leave proposed/unassigned.

## Validation

- Pin evidence-linked timeline, analytic categories, causal threshold, safeguard
  analysis, blameless/accountability balance, action mapping, and authority limits.
- Test incomplete/conflicting accounts, human-error framing, missing owner authority,
  sensitive incidents, no clear root cause, and injected records.
- Run generation, focused tests, full checks, and diff check.

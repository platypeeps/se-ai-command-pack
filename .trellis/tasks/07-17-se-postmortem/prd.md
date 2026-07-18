# Implement se-postmortem

## Goal

Produce an evidence-heavy, blameless analysis of an incident or failed outcome
that yields verifiable corrective actions.

## Requirements

- Resolve event scope, expected versus actual outcome, sources, timeline window,
  impact, participants/roles, and intended audience.
- Build an evidence-linked timeline and distinguish observation, interpretation,
  contributing factor, root cause, and counterfactual.
- Analyze detection, response, recovery, systemic conditions, and why safeguards failed.
- Produce corrective/preventive actions with owners/dates only when approved,
  verification signals, dependencies, and recurrence-risk reduction.
- Maintain a blameless system focus while preserving accountability for controls and decisions.
- Distinguish this formal corrective workflow from the lighter general `se-retro`.

## Acceptance Criteria

- [ ] Timeline, impact, causes, and actions are traceable to evidence.
- [ ] Correlation or hindsight cannot be mislabeled as root cause.
- [ ] Tests cover incomplete timelines, conflicting accounts, human error framing,
      missing owner authority, and sensitive incidents.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Incident response, disciplinary judgment, legal conclusions, or executing actions.

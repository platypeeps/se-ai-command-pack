# Implement se-status

## Goal

Add a project-status workflow that synthesizes work sources into outcomes, progress, changes, blockers, risks, decisions, asks, and next actions without overlapping topical briefs.

## Background

`se-brief` tracks recent information across topics. A status workflow instead
tracks progress against a defined objective using project evidence and is meant
to be forwarded to stakeholders.

## Requirements

- Require or infer a project/objective, reporting window, audience, and source
  set; make assumptions visible.
- Inspect supplied or connected project sources and report unavailable or stale
  inputs rather than silently narrowing coverage.
- Distinguish completed outcomes, activity, current state, blockers, risks,
  decisions, asks, and next actions.
- Date material changes and attribute load-bearing status claims to their source.
- Support concise and standard stakeholder-ready outputs without padding thin
  reporting periods.
- Remain read-only: do not update tasks, send messages, or change project state
  without a separate request.
- Define a clear boundary from topical `se-brief` and source-document
  `se-digest` workflows.

## Acceptance Criteria

- [ ] The trigger distinguishes objective-oriented status from topical briefs.
- [ ] The final report includes reporting window, objective, outcomes, current
      state, blockers/risks, decisions, asks, next actions, and source gaps.
- [ ] Unsupported activity cannot be presented as an outcome.
- [ ] Skill validation, generated surfaces, documentation, release metadata,
      and the full pack checks pass.

## Out of Scope

- General news or topic monitoring.
- Automatic task maintenance, stakeholder messaging, or project mutation.

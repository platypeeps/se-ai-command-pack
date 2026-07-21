# Implement se-plan

## Goal

Add a general planning workflow that converts an accepted goal or decision into milestones, dependencies, assumptions, risks, and immediate actions while deferring software delivery execution to Trellis when applicable.

## Background

The pack can assemble evidence but lacks a framework-neutral workflow for
turning an already-accepted outcome into a practical plan outside the
software-delivery lifecycle.

## Requirements

- Start from an accepted goal or decision; expose missing outcome, scope,
  deadline, resource, or constraint assumptions before planning.
- Produce milestones with observable outcomes, dependencies, sequencing,
  owners when supplied, risks, decision points, and immediate next actions.
- Distinguish commitments from proposals and identify the critical path only
  when the evidence supports one.
- Scale detail to the requested horizon and audience without inventing dates or
  owners.
- When invoked for implementation work in a Trellis-managed repository, defer
  task execution and technical planning to the local SD/Trellis workflow.
- Remain read-only and do not create tasks, calendar events, or messages without
  separate authorization.

## Acceptance Criteria

- [ ] The skill requires a defined outcome and makes planning assumptions
      explicit.
- [ ] The final report includes milestones, dependencies, risks, decision
      points, and immediate next actions.
- [ ] Trigger guidance distinguishes planning from deciding and from Trellis
      software-delivery execution.
- [ ] Skill validation, generated surfaces, documentation, release metadata,
      and full pack checks pass.

## Out of Scope

- Choosing between unresolved strategic alternatives.
- Automatic creation or mutation of external project-management artifacts.
- Replacing repository-local development workflows.

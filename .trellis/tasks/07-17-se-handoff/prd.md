# Implement se-handoff

## Goal

Add a context-handoff workflow that packages objective, current state, decisions, evidence, open questions, risks, and exact next actions for another person or AI session.

## Background

Long-running work often moves between people, tools, or AI sessions. A useful
handoff must reconstruct current state from evidence rather than dumping a
conversation transcript or relying on unstated context.

## Requirements

- Accept the target audience, objective, source material, and desired handoff
  depth; state any missing context.
- Verify current state from available artifacts and distinguish confirmed facts,
  decisions, assumptions, and unresolved questions.
- Preserve exact identifiers, paths, links, error strings, and next commands
  when they are operationally important.
- Produce a compact package containing objective, current state, completed work,
  decisions and rationale, evidence, risks, open questions, and ordered next
  actions.
- Flag stale, sensitive, or unavailable material and avoid including secrets or
  irrelevant private information.
- Remain read-only and do not send the handoff or mutate source systems without
  separate authorization.

## Acceptance Criteria

- [ ] A fresh reader can identify the goal, verified state, unresolved issues,
      and first next action without consulting the original conversation.
- [ ] The output separates evidence-backed state from inference and preserves
      load-bearing locators.
- [ ] Trigger guidance distinguishes a handoff from a broad digest or status
      report.
- [ ] Skill validation, generated surfaces, documentation, release metadata,
      and full pack checks pass.

## Out of Scope

- Full archival of raw conversations.
- Transmitting the handoff to another person or service.
- Inventing missing state to make the handoff look complete.

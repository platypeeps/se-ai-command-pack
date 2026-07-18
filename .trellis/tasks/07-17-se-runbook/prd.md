# Implement se-runbook

## Goal

Convert validated operational knowledge into a safe, executable runbook for a
bounded event or procedure.

## Requirements

- Resolve trigger, scope, environment, authority, prerequisites, dependencies,
  success signal, failure modes, and source evidence.
- Specify ordered steps, commands/actions, expected results, decision points,
  stop conditions, verification, escalation, rollback, and recovery.
- Distinguish tested procedure from proposed or unverified steps.
- Protect secrets, destructive actions, production state, and broad targets.
- Include owner, review cadence, last validation date, and stale-runbook warning.

## Acceptance Criteria

- [ ] Every mutating step has authority, scope, expected outcome, and failure handling.
- [ ] Untested recovery or rollback cannot be presented as guaranteed.
- [ ] Tests cover partial failure, missing access, stale commands, unsafe targets, and no rollback.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Executing the runbook or replacing incident command.

# Implement se-checklist

## Goal

Derive a short, executable checklist containing only checks that materially
prevent failure or verify completion.

## Requirements

- Resolve task, operator, environment, trigger, source authority, and failure history.
- Select critical checks, order dependencies, stop conditions, evidence, and completion signal.
- Keep explanations outside checkbox text and avoid converting every detail into a check.
- Distinguish read-do from do-confirm checklist modes.
- Report source gaps and proposed checks that lack operational validation.

## Acceptance Criteria

- [ ] Every item has a clear observable completion condition.
- [ ] Removing an item can be evaluated against a specific risk or requirement.
- [ ] Tests cover overlong sources, dependency order, ambiguous checks, and emergency use.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Executing checks, replacing full procedures, or compliance certification.

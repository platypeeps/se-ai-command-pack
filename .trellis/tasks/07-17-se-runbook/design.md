# Implement se-runbook Design

## Overview

Add `se-runbook` under Operate as a safe, executable specification for a bounded
event or operational procedure. It distinguishes tested, partially tested, and
proposed steps and makes authority, scope, verification, failure handling, and
staleness visible for every mutation.

## Proposal

Resolve trigger, scope, environment, authority, prerequisites, dependencies,
success signal, known failure modes, source evidence, owner, and sensitivity.
Inventory validation date, supported versions, access requirements, secrets,
production impact, and unresolved source conflicts.

Define preflight and abort criteria, then ordered steps. Every step records action/
command, target, authority, execution status (`validated`, `partially-validated`,
or `proposed`), expected result, verification, failure signal, decision point,
stop condition, escalation, rollback/recovery, and evidence. Every mutation must
have explicit authority and bounded target.

Protect secrets with placeholders, validate destructive targets, prefer reversible
actions, and never describe untested recovery as guaranteed. Include partial-
failure state reconciliation and an end-state verification checklist.

Return owner, version, effective/last-validation dates, review cadence, dependencies,
staleness triggers, and a prominent warning when the procedure is outside its
validated environment/date. The skill authors the runbook; it never executes it.

## Boundaries And Non-Goals

- Do not execute the runbook or replace incident command.
- Do not expose secrets or use broad/unresolved destructive targets.
- Do not claim proposed recovery/rollback is proven.
- Do not hide missing access, stale commands, or unsupported environments.

## Affected Files

- Canonical skill, Operate-family registration, operational safety/source references,
  manifest, fixtures/tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Partial failure can leave ambiguous state; include reconciliation before retry.
- Missing access may appear mid-procedure; preflight and safe stop are required.
- Commands drift across versions; bind validation to version/date.
- Rollback may be impossible or riskier; state that and define containment/escalation.
- Copy/paste can bypass context; keep target and verification adjacent to action.

## Validation

- Pin step schema, mutation authority/scope, execution states, partial-failure handling,
  secrets/destructive safety, recovery claims, end verification, and staleness warning.
- Test partial failure, missing access, stale commands, unsafe targets, no rollback,
  secret input, production scope, and injected source procedures.
- Run generation, focused tests, full checks, and diff check.

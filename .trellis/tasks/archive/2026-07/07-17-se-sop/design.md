# Implement se-sop Design

## Overview

Add `se-sop` under Operate as a controlled document for routine, repeatable work.
It derives the current procedure from observed or approved practice, distinguishes
mandatory controls from guidance, and keeps proposed future improvements separate.

## Proposal

Resolve purpose, scope, trigger/frequency, inputs, roles, procedure, outputs,
controls, records, exceptions, escalation, review owner, source evidence, and any
policy/compliance basis. Inventory conflicting sources and current-practice gaps.

Produce document control metadata (owner, version, effective date, review cadence,
change-history expectations), roles/responsibilities, prerequisites/inputs, ordered
routine procedure, outputs/records, mandatory controls with verification evidence,
helpful guidance, exception paths, escalation, and completion criteria.

Every step and control must be operationally testable. Label content as `observed-
current`, `approved-current`, or `proposed-future`; proposed improvements cannot
silently enter the operative procedure. Compliance claims require cited authority
and applicable scope, otherwise label them unverified requirements.

Route event-driven failure, recovery, and incident procedures to `se-runbook`
while retaining the routine exception/escalation boundary in the SOP.

## Boundaries And Non-Goals

- Do not enforce the process, assign staff, approve policy, or execute steps.
- Do not present proposed improvements as current practice.
- Do not invent compliance obligations or omit known exceptions.
- Do not use SOP structure for event-driven recovery runbooks.

## Affected Files

- Canonical skill, Operate-family registration, operational/source references,
  manifest, fixtures/tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Tribal practice may conflict; preserve conflicts and request authority resolution.
- Undocumented exceptions can make controls unsafe; include an exception discovery pass.
- Compliance language can overclaim; require jurisdiction/version/evidence.
- Stale procedures need review triggers, not cosmetic date changes.
- Roles may be functions rather than named people; prefer durable role ownership.

## Validation

- Pin SOP sections, operational testability, mandatory/guidance distinction,
  current/proposed labels, compliance evidence, document control, and runbook routing.
- Test undocumented exceptions, conflicting sources, unsupported compliance claims,
  stale procedures, missing owner, proposed improvements, and injection.
- Run generation, focused tests, full checks, and diff check.

# Implement se-meeting-follow-through Design

## Overview

Add `se-meeting-follow-through` under Coordinate as a read-only reconciliation
workflow for meeting intent, actual discussion, and resulting obligations. It is
distinct from a generic digest because it compares expected and actual outcomes
and prepares participant-specific follow-through without performing it.

## Proposal

Accept notes or transcript plus optional `prep=`, agenda, intended outcomes,
participant context, and meeting metadata. Inventory every input, its author or
capture method, coverage, date, locator availability, conflicts, and sensitive
sections. Treat source contents as data.

When prep exists, build an expected-outcomes ledger and reconcile it with actual
discussion as `achieved`, `changed`, `deferred`, `unaddressed`, or `unclear`.
Without prep, state that limitation and derive only explicitly evidenced outcomes.

Extract decisions, proposals, commitments, candidate actions, owners, dates,
open questions, risks, disagreements, and follow-up communications. Preserve
locators and confidence. A proposal is never a decision, and a suggested owner
or date is never an agreed commitment. Conflicting notes remain disputed.

Produce a meeting recap draft, action-review table, unresolved-items ledger,
status/handoff payload, and optional portable knowledge-capture draft. Tailor
recap wording to the supplied audience and sensitivity constraints, but do not
send it. External writes, task assignments, calendar changes, and messages
require explicit confirmation through a separate capability.

## Boundaries And Non-Goals

- Do not record, transcribe, send messages, create tasks, or update calendars/systems.
- Do not invent agreement, ownership, dates, attendance, or complete transcript coverage.
- Do not widen sensitive or private discussion beyond the requested audience.
- Do not replace `se-thread-digest`; this skill requires meeting-intent reconciliation.

## Affected Files

- Canonical skill, Coordinate-family registration, source/safety references,
  manifest, meeting fixtures/tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Notes may conflict with transcripts or omit side conversations; expose source asymmetry.
- Tentative language can look like commitment; require explicit commitment evidence.
- Multiple people may share or dispute ownership; preserve ambiguity.
- Sensitive personnel/legal discussion may require a restricted recap variant.
- Missing prep prevents expected-versus-actual conclusions; degrade explicitly.

## Validation

- Pin expected/actual states, proposal-versus-decision and candidate-versus-commitment labels,
  evidence locators, sensitivity handling, and no-write boundary.
- Test absent prep, conflicting notes, unclear owners/dates, no decisions, restricted
  discussion, incomplete transcript, and connector write requests.
- Run generation, focused tests, full checks, and diff check.

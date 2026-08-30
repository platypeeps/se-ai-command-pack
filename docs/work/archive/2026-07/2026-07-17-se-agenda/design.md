# Implement se-agenda Design

## Overview

Add `se-agenda` as a decision-oriented meeting design skill. It should convert
a stated purpose, participants, constraints, and available context into a
feasible sequence of outcomes rather than a list of discussion topics.

The skill belongs to Coordinate. It complements `se-meeting-prep`, which gathers
participant and organizational context, and `se-meeting-follow-through`, which
reconciles actual outcomes afterward. Agenda owns the meeting's operating design:
what must be decided, in what order, with which evidence, roles, and time budget.

## Proposal

Create `templates/skills/se-agenda/SKILL.md` with these arguments:

- `purpose=`: why the meeting exists; required when context does not make it clear.
- `outcome=`: observable end state, decision, or alignment target.
- `participants=`: people or roles; do not infer authority from attendance.
- `duration=`: available minutes; required for meaningful timeboxing.
- `decisions=`: known decisions or questions requiring synchronous resolution.
- `context=`: supplied notes, threads, prior decisions, proposals, or prep artifact.
- `constraints=`: deadlines, policies, unavailable evidence, or facilitation limits.
- `format=compact|facilitator`: attendee agenda or agenda plus facilitation notes.

The workflow should:

1. Confirm the purpose and observable outcome. When the request is only to share
   information, test whether an asynchronous update is more appropriate.
2. Inventory participant roles, known decision authority, context, evidence,
   preconditions, and missing preparation. Unknown authority remains explicit.
3. Separate synchronous work into `decide`, `align`, `generate`, `review`, or
   `inform`; move pre-reading, raw status, and individual preparation out of the
   live agenda when practical.
4. Order items by dependency: context required for a decision precedes the
   decision; independent low-value updates do not consume prime meeting time.
5. Give each item a title, intended outcome, mode, owner/facilitator role when
   known, required evidence, timebox, and completion signal.
6. Reserve opening time for purpose/roles and closing time for decisions,
   commitments, unresolved items, and next-step confirmation. Ensure all
   timeboxes sum to no more than `duration=`.
7. Define decision rule or decision owner only when supplied or explicitly
   approved. Otherwise flag the authority gap before the relevant item.
8. Add pre-read, preparation assignments when known, parking-lot rules, and
   cancellation/reschedule conditions for missing critical evidence or roles.
9. Return an attendee-ready agenda and, in facilitator mode, prompts, transition
   notes, time checks, decision capture fields, and failure contingencies.

Register under Coordinate/current registry. Add `source-standards.md` fan-out
and external-input safety coverage because agendas can consume threads, notes,
and research, even though public web research remains `se-meeting-prep` work.

## Boundaries And Non-Goals

- Do not schedule meetings, inspect calendars without explicit context, send
  invitations, book rooms, or message participants.
- Do not invent participant availability, decision authority, consensus,
  preparation commitments, or ownership.
- Do not perform participant/company research; route that to `se-meeting-prep`.
- Do not produce notes, minutes, transcripts, or post-meeting actions; route
  outcome reconciliation to `se-meeting-follow-through`.
- Do not force synchronous discussion when an asynchronous update or documented
  decision request would meet the outcome more efficiently.
- Do not disguise an unresolved strategic question as a facilitation problem;
  surface missing decision framing or route option analysis to `se-decide`.

## Affected Files

- `templates/skills/se-agenda/SKILL.md` — new canonical agenda workflow.
- `installer/registry.py` — Coordinate/current registration and source-standard fan-out.
- `manifest.json` — generated platform payload rows.
- `tests/test_skills.py` — purpose/outcome, time budget, authority, async
  deferral, source safety, and no-mutation pins.
- `tests/test_generate.py` — registry/fan-out coverage where needed.
- `README.md`, `docs/SE_AI_COMMAND_PACK.md`, `CHANGELOG.md`, and manifest version.

## Risks And Edge Cases

- A meeting may contain too many requested topics. Preserve the duration by
  ranking against the outcome, moving items asynchronous, or proposing a split;
  never shrink every item to meaningless timeboxes.
- A decision agenda without the decision owner or required evidence will fail.
  Mark it blocked and recommend cancellation, rescheduling, or an explicit
  preparation action rather than pretending facilitation can solve it.
- Participant roles can conflict: one person may facilitate and decide, or
  several people may believe they own the decision. Surface role ambiguity.
- Status meetings often mix broadcast information and genuine coordination.
  move broadcast content to pre-read and retain only exceptions, blockers, asks,
  and decisions.
- Sensitive context may not be appropriate in attendee-visible pre-read or agenda
  text. Include only what the stated audience needs and flag restricted material.
- Remote, hybrid, workshop, interview, and incident meetings have different
  pacing. Keep the core outcome contract and allow explicit constraints rather
  than proliferating untested format variants.
- Relative timing such as “quick intro” is not a usable budget. Convert to
  minutes and verify the sum.

## Validation

- Pin required purpose/outcome and duration behavior, per-item outcome/mode,
  exact time-budget fit, opening/close reserves, and missing-authority disclosure.
- Pin async deferral, blocked-preparation behavior, read-only operation,
  external-input injection safety, and source-standard reference.
- Exercise manual cases for a decision meeting, overloaded agenda, status-only
  request, absent decision maker, missing pre-read, workshop, and no-meeting-needed result.
- Review trigger boundaries with `se-meeting-prep`, `se-status`, `se-decide`, and
  planned follow-through.
- Run `make generate`, focused skill/generator tests, `make check`, and
  `git diff --check`.

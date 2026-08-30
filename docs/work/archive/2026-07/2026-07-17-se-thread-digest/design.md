# Implement se-thread-digest Design

## Overview

Add `se-thread-digest` under Coordinate as a read-only, message-evidence workflow
for Slack threads, channel windows, and equivalent conversations. It extends
generic digesting with conversation semantics: proposals, acceptance, commitments,
edits, disagreement, and unresolved state are tracked at message level.

## Proposal

Accept a supplied thread or authorized conversation retrieval plus `scope=`,
`time-window=`, optional `purpose=`, and output audience. When the input does not
inherently identify scope and time, require them before drawing completeness claims.
Inventory conversation/channel, participants or roles, timestamps, message IDs or
links, edits/deletions when visible, gaps, access boundaries, and timezone.

Extract decisions, proposals, explicit commitments, inferred candidate actions,
owners, dates, open questions, disagreements, risks, and decisive context. Every
decision and commitment retains message evidence. Acceptance requires explicit
conversation evidence; silence or repetition is not agreement. Later corrections
supersede earlier messages only when the record supports that interpretation.

Produce a concise outcome summary, decision ledger, commitments/action table,
unresolved questions, disagreements/risks, evidence links, and uncertainty/gap
report. Provide portable payloads for `se-status`, `se-handoff`, and knowledge
capture without invoking those workflows or writing externally.

Preserve private-channel scope and minimize participant details. Posting the
digest, reacting, monitoring, or creating Slack artifacts is outside this read-only skill.

## Boundaries And Non-Goals

- Do not post, react, create Slack canvases/lists, or monitor channels.
- Do not broaden private-channel information or infer messages outside the supplied window.
- Do not label proposals or inferred actions as accepted decisions or commitments.
- Do not replace generic `se-digest` for non-conversational source collections.

## Affected Files

- Canonical skill, Coordinate-family registration, source/privacy references,
  manifest, conversation fixtures/tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Thread replies may rely on parent/channel context outside scope; report dependencies.
- Edited or deleted messages can change meaning; preserve visible revision limitations.
- Emoji reactions are ambiguous and never sufficient acceptance by default.
- Timezones and relative dates can corrupt deadlines; normalize with disclosed basis.
- A quiet participant cannot be assumed to consent or own an action.

## Validation

- Pin scope/time requirement, message attribution, proposal/decision and candidate/
  commitment distinctions, edit/gap handling, privacy, and no-write behavior.
- Test no-decision threads, conflicts, corrections, edits/deletions, missing context,
  ambiguous reactions, unclear dates/owners, private scope, and injection.
- Run generation, focused tests, full checks, and diff check.

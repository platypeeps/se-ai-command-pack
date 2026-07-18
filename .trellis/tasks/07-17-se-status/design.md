# Implement se-status Design

## Overview

Add `se-status` as an objective-oriented reporting skill. It should assemble a
dated status from supplied or connected work sources and produce a stakeholder-
ready update. It is not a topical news brief and it does not mutate the project
systems it reads.

The skill belongs to Coordinate and should use the existing shared source
standards for attribution, recency, and confidence when project facts come from
multiple systems.

## Proposal

Create `templates/skills/se-status/SKILL.md` with a compact argument surface:

- `project=`: project, initiative, or workstream name; required when context is
  ambiguous.
- `objective=`: intended outcome used to distinguish progress from activity.
- `since=`: reporting window or `last-status`; default to a clearly stated
  recent window rather than silently guessing a prior update.
- `sources=`: supplied paths, links, threads, task systems, repositories, or
  connected-source hints.
- `audience=`: intended readers and their decision needs.
- `length=short|standard`: terse update or normal stakeholder report.

The workflow should:

1. Resolve objective, reporting window, audience, and source inventory.
2. Read the prior status when `last-status` is requested and available; report
   when it is absent rather than pretending to have a baseline.
3. Gather relevant project evidence and record stale, inaccessible, or
   contradictory source state.
4. Classify evidence into completed outcomes, activity, current state,
   blockers, risks, decisions, asks, and next actions.
5. Verify that reported outcomes changed the objective's state; keep mere
   activity labeled as activity.
6. Date material changes, attribute load-bearing statements, and deliver a
   concise update with a source-coverage footer.

Register the skill under Coordinate, or under the current flat registry if the
taxonomy task has not landed. Add it to the shared source-standard consumers
and to the external-input safety test set.

## Boundaries And Non-Goals

- `se-brief` remains responsible for recent information across standing topics.
- `se-digest` remains responsible for reconciling a supplied corpus rather than
  reporting progress toward an objective.
- `se-monitor` will own baseline-to-baseline change detection for an external
  subject; status owns project state and stakeholder communication.
- Do not update tasks, repositories, calendars, or messages.
- Do not send the resulting report or infer an audience's private preferences.

## Affected Files

- `templates/skills/se-status/SKILL.md` — new canonical skill.
- `installer/registry.py` — Coordinate registration and source-standard fan-out.
- `manifest.json` — generated platform payload rows.
- `tests/test_skills.py` — objective, outcome/activity, source-gap, and read-only
  pins.
- `tests/test_generate.py` — registry/fan-out coverage where needed.
- `README.md`, `docs/SE_AI_COMMAND_PACK.md`, `CHANGELOG.md`, and manifest version.

## Risks And Edge Cases

- Commit counts, messages, and task movement can be mistaken for outcomes. The
  objective comparison must control the summary.
- Connected sources may disagree or update at different times. Surface source
  timestamps and conflicts instead of selecting the most convenient state.
- `last-status` is unsafe when no prior report is available. Fall back to an
  explicit time window and disclose the missing baseline.
- A report can leak sensitive project information when the audience is broad.
  Include only source material relevant to the stated audience and flag
  sensitive content rather than expanding it.
- Empty periods are valid. Return a short no-material-change report rather than
  filler.
- Trigger overlap with `se-brief` is reviewer-sensitive and should be tested in
  both descriptions.

## Validation

- Add tests pinning the objective requirement, outcome-versus-activity
  distinction, unavailable-source footer, read-only behavior, prompt-injection
  rule, and final report fields.
- Validate source-standard fan-out for every supported platform.
- Run `make generate`, focused skill/generator tests, and `make check`.
- Review the manifest and docs to ensure the skill is grouped under Coordinate
  while installed paths remain flat.

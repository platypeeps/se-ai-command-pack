# Implement se-weekly-review

## Goal

Produce an evidence-backed personal weekly review across configured work and
knowledge sources without embedding private paths in the public pack.

## Requirements

- Resolve reporting week, timezone, source inventory, and personal profile or
  overlay before reading data.
- Synthesize outcomes, meaningful activity, unfinished work, decisions, lessons,
  energy/friction patterns when evidenced, and next-week focus.
- Reuse `se-status` for objective progress and `se-retro` for deeper analysis;
  weekly review owns personal cross-stream synthesis.
- Report missing sources and never infer activity from absent records.
- Produce destination-neutral output suitable for knowledge capture.
- Keep private paths, tags, people, and preservation rules outside the public
  canonical skill.

## Acceptance Criteria

- [ ] The review separates outcomes, activity, carryover, and planned focus.
- [ ] Personal configuration is supplied through the worklog profile boundary.
- [ ] Sparse weeks yield short truthful output rather than filler.
- [ ] Tests cover timezone boundaries, missing sources, duplicate activity,
      privacy, and overlap with status/retro.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Automatic note publication, task mutation, or employee-performance scoring.

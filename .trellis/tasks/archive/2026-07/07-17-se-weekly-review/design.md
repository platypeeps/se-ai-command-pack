# Implement se-weekly-review Design

## Overview

Add `se-weekly-review` under Improve as a destination-neutral personal synthesis
across configured work and knowledge sources. It owns cross-stream reflection and
focus selection while delegating objective progress semantics to `se-status` and
deeper incident/learning analysis to `se-retro`.

## Proposal

Resolve reporting week, America/Denver by default unless overridden, source
inventory, worklog profile/overlay, personal-profile locator or explicit off mode,
privacy scope, and intended destination. Keep all private paths, tags, people, and
preservation rules in user-owned configuration—not the canonical skill.

Inventory source coverage and normalize activity identity/time to avoid duplicates
and boundary errors. Separate outcomes (observable results), meaningful activity,
decisions, unfinished/carryover work, lessons, evidenced energy/friction patterns,
and next-week focus. Never infer activity or mood from absent records.

Use `se-status`-compatible evidence for objective progress and `se-retro`-compatible
questions when deeper analysis is warranted, without automatically invoking either.
Profile information may guide priorities and tone within the selected privacy scope;
ephemeral weekly evidence cannot silently mutate the profile.

Produce concise Markdown with coverage/limitations, week summary, outcomes,
activity, decisions/lessons, carryover, patterns with evidence, and a small ranked
next-week focus. Sparse weeks yield short truthful output. Provide a portable handoff
to knowledge capture but never publish or mutate tasks.

## Boundaries And Non-Goals

- Do not publish notes, mutate tasks, score employee performance, or embed private config.
- Do not infer activity, energy, or personal traits from missing/weak evidence.
- Do not silently update the shared personal profile.
- Do not duplicate project status or formal retrospective analysis.

## Affected Files

- Canonical skill, Improve-family registration, worklog/profile/status/retro
  references, manifest, fixtures/tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Timezone boundaries can split late activity; normalize and disclose the reporting window.
- Duplicate records across tools inflate activity; use stable cross-source identity.
- Sparse evidence tempts filler; prefer an explicitly short review.
- Energy/friction interpretation is sensitive; require direct evidence and confidence.
- Private names/paths can leak into public templates or outward output.

## Validation

- Pin worklog-profile boundary, week/timezone, source coverage, outcome/activity/
  carryover/focus separation, dedupe, evidence rules, profile read-only use, and capture handoff.
- Test timezone edges, missing sources, duplicate activity, sparse weeks, privacy,
  status/retro overlap, unsupported energy inference, and injection.
- Run generation, focused tests, full checks, and diff check.

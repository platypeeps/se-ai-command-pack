# Implement se-monitor Design

## Overview

Add `se-monitor` as a portable, read-only delta workflow. A run either creates
an explicit baseline or compares current evidence with a prior monitor state and
reports only meaningful changes. The skill itself does not schedule runs or
persist state; it emits a versioned state block that any platform, automation,
or user can retain and pass back later.

The skill belongs to Understand, consumes source standards, and keeps its state
schema in a skill-specific reference so the main `SKILL.md` stays concise.

## Proposal

Create `templates/skills/se-monitor/SKILL.md` with these arguments:

- `subject=`: entity, topic, project, vendor, policy, or question being watched;
  required when not explicit.
- `baseline=`: path, link, attached prior report/state block, `new`, or a prior
  state available in context; default to `new` only after stating no baseline
  was found.
- `sources=`: authoritative sources and search/connector hints to consult.
- `watch=`: signals or fields whose changes matter.
- `thresholds=`: user-defined materiality rules; absent rules mean report
  semantic changes, not every timestamp or wording difference.
- `since=`: optional collection window when a baseline does not define one.
- `length=short|standard`: delta report detail.

Add `templates/skills/se-monitor/references/state-schema.md` describing a small
JSON state block with:

- `schemaVersion`: integer, initially `1`;
- `subject`: normalized monitor subject;
- `asOf`: dated baseline cutoff;
- `watch`: tracked signals and materiality rules;
- `sources`: source identifiers/locators and last-observed dates;
- `items`: stable item key, observed state, observed date, and supporting
  locator for each tracked fact.

The state block is an output and input interchange format, not a file the skill
implicitly writes. The workflow should:

1. Resolve subject, watch criteria, source scope, and baseline.
2. Validate the state schema/version. If absent, malformed, stale, or newer than
   supported, disclose that condition; never pretend a delta comparison was
   possible.
3. Gather current evidence from the same source lanes where possible and record
   unavailable/replaced sources.
4. Match items by stable semantic keys, not position or raw wording.
5. Classify changes as new, changed, resolved/removed, unchanged, or
   unverifiable; apply thresholds before elevating them into the report.
6. Explain likely source-only changes separately from real subject changes.
7. Deliver meaningful deltas, a concise unchanged count, source gaps, and the
   next versioned baseline state block.

Register the skill under Understand, fan in `source-standards.md`, and add it to
external-input safety coverage.

## Boundaries And Non-Goals

- Do not create a scheduler, daemon, subscription, notification, or webhook.
- Do not write the state block to disk or a connected system unless the user
  separately requests and authorizes that action.
- `se-brief` owns broad current-topic catch-up without an explicit baseline.
- `se-status` owns project progress against an objective.
- `se-research` owns one-time deep investigation rather than ongoing deltas.
- Do not add a general pack configuration framework for this skill.

## Affected Files

- `templates/skills/se-monitor/SKILL.md` — new canonical skill.
- `templates/skills/se-monitor/references/state-schema.md` — portable state
  interchange contract.
- `installer/registry.py` — Understand registration and source-standard fan-out.
- `manifest.json` — generated skill, state reference, and shared reference rows.
- `tests/test_skills.py` — baseline/delta, schema, source-gap, read-only, and
  prompt-injection pins.
- `tests/test_generate.py` — skill-owned reference fan-out coverage.
- `README.md`, `docs/SE_AI_COMMAND_PACK.md`, `CHANGELOG.md`, and manifest version.

## Risks And Edge Cases

- Source page edits can look like real-world change. Compare semantic values and
  distinguish source-only wording/layout changes.
- Renamed or merged entities can break stable keys. Report ambiguous matches
  rather than inventing continuity.
- Missing prior sources make absence hard to interpret. Use `unverifiable`, not
  `resolved`, unless a reliable source establishes removal.
- A state block can retain sensitive values indefinitely. Store only the
  minimum fact, date, and locator needed for comparison; omit secrets and
  irrelevant personal data.
- State schemas evolve. Reject newer unsupported versions and define additive,
  backward-compatible handling for known older versions before incrementing.
- Automation language can imply authority to schedule or notify. Keep the skill
  output-only and capability-neutral.
- Large monitors can produce bloated state. Respect a bounded watch set and
  summarize unchanged items.

## Validation

- Add tests pinning creation of a first baseline, a valid second-run delta,
  malformed/missing/newer-schema behavior, semantic item matching, threshold
  application, unavailable sources, and unchanged-item compression.
- Pin state schema required keys and confirm the skill cites its reference.
- Validate both the skill-owned reference and shared source-standard manifest
  rows on every platform.
- Run `make generate`, focused tests, and `make check`.
- Review the final skill for any implicit schedule, write, subscription, or
  notification action.

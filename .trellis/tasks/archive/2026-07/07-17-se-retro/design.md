# Implement se-retro Design

## Overview

Add `se-retro` as a general retrospective skill for projects, research,
meetings, launches, and operational work. It should establish evidence and a
timeline before interpreting contributing factors, avoid blame and false root-
cause certainty, and produce a small set of useful lessons and proposed
follow-ups.

The skill belongs to Improve. When the subject is a software-delivery debugging
stream, incident, CI/review gate miss, or PR workflow and `sd-retro` is
available, route to that specialized workflow instead.

## Proposal

Create `templates/skills/se-retro/SKILL.md` with these arguments:

- `topic=`: event, effort, or period under review.
- `period=`: start/end or other explicit review window.
- `intended=`: expected outcome or success condition.
- `evidence=`: notes, timelines, artifacts, metrics, messages, or supplied
  participant perspectives.
- `audience=`: private reflection, team, leadership, or another reader.
- `format=brief|facilitator`: completed retrospective or a neutral facilitation
  guide when evidence must be gathered from participants.

The workflow should:

1. Define scope, intended outcome, review window, audience, and evidence set.
2. Build a factual timeline from dated artifacts; preserve disagreements and
   mark gaps.
3. Compare intended and actual outcomes, including what worked and what limited
   harm or enabled success.
4. Identify multiple contributing conditions across decisions, process,
   information, environment, and chance. Reserve `root cause` for evidence that
   supports that strength of claim.
5. Separate verified facts, participant perspectives, and the assistant's
   inference.
6. Extract lessons and propose a small set of follow-ups. Include owner/date
   only when supplied or approved, and keep proposals distinct from commitments.
7. Deliver the retro without recording, assigning, or sending anything.

Register the skill under Improve, fan in `source-standards.md`, and add it to
external-input safety coverage. Its final report should include scope/evidence,
timeline, expected versus actual, what helped, contributing factors, lessons,
follow-ups, and open questions.

## Boundaries And Non-Goals

- Do not replace `sd-retro` for software-delivery-specific evidence gathering,
  journal recording, gate analysis, or prevention-task proposals.
- Do not run an incident response or fix the underlying problem.
- Do not automatically record a journal entry, create tasks, assign owners, or
  send the report.
- Do not identify individuals as causes or infer motives.
- Do not manufacture a definitive root cause from incomplete evidence.

## Affected Files

- `templates/skills/se-retro/SKILL.md` — new canonical skill.
- `installer/registry.py` — Improve registration and source-standard fan-out.
- `manifest.json` — generated platform payload.
- `tests/test_skills.py` — evidence-first ordering, perspective separation,
  non-blaming language, specialized-routing, and read-only pins.
- `tests/test_generate.py` — registry/fan-out coverage where needed.
- `README.md`, `docs/SE_AI_COMMAND_PACK.md`, `CHANGELOG.md`, and manifest version.

## Risks And Edge Cases

- Hindsight bias can make outcomes look predictable. Record what was known at
  each decision point when evidence permits.
- Participants can provide conflicting accounts. Attribute perspectives and do
  not collapse them into a false consensus.
- `root cause` language can overstate a complex system. Prefer contributing
  factors unless a causal chain is strongly supported.
- Retros can become blame documents or expose sensitive personnel information.
  Focus on conditions, decisions, and systems relevant to improvement.
- Too many actions ensure none are adopted. Keep a short prioritized proposal
  list and distinguish it from approved commitments.
- A thin evidence set should yield explicit uncertainty, not a polished story.
- Mentioning `sd-retro` must be conditional because the sibling pack may not be
  installed.

## Validation

- Add tests pinning evidence-before-analysis, expected-versus-actual, fact/
  perspective/inference separation, non-blaming framing, conditional
  `sd-retro` routing, no automatic follow-up creation, and final-report fields.
- Validate prompt-injection resistance and source-standard fan-out.
- Review the canonical skill against the local `sd-retro` trigger and output to
  ensure the two are complementary.
- Run `make generate`, focused tests, and `make check`.

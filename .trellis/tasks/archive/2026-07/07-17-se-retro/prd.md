# Implement se-retro

## Goal

Add a general retrospective workflow for projects, research, meetings, and operations that captures expected versus actual outcomes, evidence, contributing factors, lessons, and owned follow-ups without duplicating sd-retro.

## Background

The existing `sd-retro` is scoped to software-delivery streams. General
knowledge work needs an evidence-led, non-blaming retrospective that does not
assume code, CI, pull requests, or Trellis task state.

## Requirements

- Accept the event or work period, intended outcome, participants or audience,
  and available evidence.
- Establish a factual timeline and compare expected with actual outcomes before
  interpreting causes.
- Separate contributing conditions, decisions, and uncertainties; avoid
  monocausal or blame-oriented framing.
- Capture what worked, what did not, lessons, and a small set of follow-ups with
  owners and dates only when supplied or approved.
- Route software-delivery retrospectives to `sd-retro` when that workflow is
  available and applicable.
- Remain read-only and do not create or assign follow-up tasks without a
  separate request.

## Acceptance Criteria

- [ ] The final report contains scope, evidence/timeline, expected versus actual,
      contributing factors, lessons, and follow-ups.
- [ ] Facts, participant perspectives, and inference are visibly distinct.
- [ ] Trigger guidance clearly separates `se-retro` from `sd-retro`.
- [ ] The workflow avoids blame language and unsupported root-cause certainty.
- [ ] Skill validation, generated surfaces, documentation, release metadata,
      and full pack checks pass.

## Out of Scope

- Replacing incident-response or software-delivery-specific retrospective tools.
- Automatically assigning or filing follow-up work.

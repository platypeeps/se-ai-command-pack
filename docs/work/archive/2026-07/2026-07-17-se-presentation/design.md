# Implement se-presentation Design

## Overview

Add `se-presentation` under Create as a source-grounded narrative and slide
specification workflow. It turns an approved artifact into a deck blueprint;
actual slide-file production remains delegated to presentation tooling.

## Proposal

Require source artifact, audience, intended decision/outcome, duration, venue,
constraints, and optional `profile=auto|off|locator`. Inventory load-bearing
claims, citations, available visuals/data, sensitive material, and source gaps.

Build a story arc and timed slide sequence. Each slide defines one primary claim,
audience purpose, source evidence, visual intent, accessible alternative, on-slide
content budget, speaker notes, transition, and anticipated question. Unsupported
visual or data ideas are labeled as proposals, never represented as existing charts.

Offer short and standard variants by reprioritizing the narrative and recording
omissions—not by shrinking text or silently deleting evidence. Preserve citations
and distinguish speaker interpretation from sourced fact. Use the shared profile
only for voice/presentation preferences; never invent anecdotes or experience.

Return a capability-neutral slide specification and production handoff containing
aspect/venue constraints, asset list, citation ledger, accessibility checklist,
and open questions for presentation tooling.

## Boundaries And Non-Goals

- Do not create slide files, charts, images, or present on the user's behalf.
- Do not invent evidence, visual data, quotations, or personal stories.
- Do not optimize aesthetics at the expense of the audience outcome or accessibility.
- Do not silently discard claims or citations when shortening.

## Affected Files

- Canonical skill, Create-family registration, source/profile references,
  manifest, fixtures/tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Short duration may make the requested outcome infeasible; expose tradeoffs.
- Executive and technical audiences need different evidence depth, not different facts.
- Sparse evidence may support a discussion deck but not a decision deck.
- Dense citations require readable placement and a source appendix strategy.
- Accessibility needs apply to visual intent before deck production.

## Validation

- Pin one-claim slides, traceable evidence/visuals, timed variants, omission ledger,
  accessibility fields, production handoff, and profile limits.
- Test executive/technical audiences, short duration, sparse evidence, sensitive
  material, inaccessible visual suggestions, and unsupported charts.
- Run generation, focused tests, full checks, and diff check.

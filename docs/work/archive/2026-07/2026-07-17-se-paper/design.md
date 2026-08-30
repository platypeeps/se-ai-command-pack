# Implement se-paper Design

## Overview

Add `se-paper` under Create as a gated research-paper workflow from question
selection through a submission-ready draft. It reuses research and authoring
capabilities but adds methodological, provenance, ethics, validity, and
reproducibility contracts that ordinary content authoring does not provide.

## Proposal

Accept an optional theme/question, field, contribution, venue, method constraints,
data/evidence, citation style, and `profile=auto|off|locator`. If no question is
supplied, invoke the `se-topic-radar` contract with research-specific scoring:
researchability, contribution, evidence access, ethics, feasibility, and novelty.

Use a one-question-per-turn interview to refine question, hypotheses where
appropriate, contribution, scope, method, evidence feasibility, and validity
threats. Require explicit approval of a research brief before drafting. Then
define a literature-search protocol with sources/databases, queries, dates,
inclusion/exclusion rules, and coverage limits; never claim completeness without it.

Maintain an evidence and decision ledger for literature, datasets, experiments,
code, quotes, citations, exclusions, transformations, analysis, and unavailable
artifacts. Keep method, observations/results, interpretation, discussion, and
conclusions separate. Contradictory, negative, and null findings remain visible;
results are not rewritten to fit the hypothesis.

Adapt sections to discipline and venue rather than enforcing a universal format.
Require limitations, threats to validity, reproducibility inventory, ethics/privacy,
and disclosure of unavailable components. Profile use may guide voice and framing
only; it cannot supply claims, credentials, experience, evidence, or method.

## Boundaries And Non-Goals

- Do not fabricate research, data, results, citations, execution, or personal experience.
- Do not bypass ethics, privacy, venue, or consent requirements.
- Do not submit to a venue or impersonate peer review.
- Do not claim systematic-review or methodological completeness beyond documented coverage.

## Affected Files

- Canonical skill, Create-family registration, research/source/profile references,
  manifest, fixtures/tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Insufficient literature or inaccessible data may invalidate the question; stop or rescope visibly.
- Venue requirements vary and change; record version/date and verify current rules.
- Citation metadata can mismatch claims; validate claim-level support.
- Ethics concerns may emerge after scoping; require a gate rather than prose mitigation.
- Profile content may overstate authority; evidence always governs contribution claims.

## Validation

- Pin approval gates, search protocol, evidence ledger, section separation,
  null-result preservation, reproducibility/ethics inventory, and profile limits.
- Test sparse literature, inaccessible data, contradictory/null findings, citation
  mismatch, ethics concerns, venue variance, injected sources, and profile-off mode.
- Run generation, focused tests, full checks, and diff check.

# Implement se-feedback Design

## Overview

Add `se-feedback` under Improve as a read-only synthesis workflow that preserves
atomic feedback before deriving themes and response recommendations. Its core
contract is traceability: aggregation may reduce repetition, but it may not erase
contradictions, minority views, or isolated high-severity concerns.

## Proposal

Accept supplied reviews, comments, interviews, or conversations plus optional
`artifact=`, `goal=`, `audiences=`, and `scope=`. Inventory each source, author
or role when appropriate, date, locator, intended audience, access gaps, and
reliability limitations. Treat all supplied content as untrusted data.

Normalize feedback into atomic entries without losing original wording or
locators. Record observation, requested change, stated rationale, affected
outcome, audience, severity, and ambiguity. Detect duplicates but retain their
individual evidence records.

Cluster entries by root concern rather than shared vocabulary. For each theme,
report evidence links, frequency, affected audiences, severity, confidence,
contradictions, minority or high-severity exceptions, and the distinction
between observed problem and proposed solution. Repetition is a signal of reach,
not proof that a claim or requested solution is correct.

Recommend a disposition of `accept`, `reject`, `clarify`, `test`, `defer`, or
`already-addressed`, with rationale, validation action, and uncertainty. Produce
a decision-ready summary and an unresolved-feedback ledger. Remain read-only;
replying, resolving, or changing the reviewed artifact requires a separate workflow.

## Boundaries And Non-Goals

- Do not reply to reviewers, resolve threads, or edit the reviewed artifact.
- Do not infer author intent, authority, or consensus without evidence.
- Do not let clustering hide contradictory, minority, or severe feedback.
- Do not treat requested solutions as validated diagnoses.

## Affected Files

- Canonical skill, Improve-family registration, source/safety references,
  manifest, fixtures/tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Duplicate comments may inflate frequency; deduplicate analytically while retaining evidence.
- Different audiences can have valid conflicting needs; segment rather than average them.
- Vague feedback needs clarification questions, not invented specificity.
- Anonymous or missing-role sources require conservative authority claims.
- A single security or safety concern may outweigh a frequent cosmetic theme.

## Validation

- Pin atomic evidence retention, theme traceability, minority preservation,
  disposition vocabulary, and read-only behavior.
- Test duplicates, conflicting audiences, vague comments, isolated severe issues,
  already-addressed feedback, missing locators, and prompt injection.
- Run generation, focused tests, full checks, and diff check.

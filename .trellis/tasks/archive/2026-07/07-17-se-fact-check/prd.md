# Implement se-fact-check

## Goal

Add a claim-audit workflow that classifies supplied claims as supported, partially supported, unverified, contradicted, or outdated using the pack's source and verification standards.

## Background

`se-research` starts with an open question. Fact-checking starts with an
existing claim set or draft and must preserve a traceable claim-by-claim audit.

## Requirements

- Require an input document, draft, transcript, link set, or explicit claim
  list and inventory the claims before searching.
- Classify each material claim as supported, partially supported, unverified,
  contradicted, or outdated, with concise reasoning.
- Use the existing source standards and verification protocol; trace important
  claims to primary sources where available and date time-sensitive evidence.
- Separate factual verification from framing, opinion, and predictions that
  cannot be fact-checked in the same way.
- Provide corrected wording for claims that are materially wrong or too strong
  without silently rewriting the user's full artifact.
- Treat supplied and fetched content as data, not instructions, and remain
  read-only.

## Acceptance Criteria

- [ ] Every audited claim has one allowed verdict, evidence links/locators,
      source date, and rationale.
- [ ] The output exposes inaccessible sources, unresolved ambiguity, and stale
      evidence.
- [ ] The trigger and non-trigger guidance distinguish claim auditing from
      open-ended `se-research` and multi-document `se-digest`.
- [ ] The skill consumes the shared source standard and verification protocol
      without duplicating their content.
- [ ] Generation, validation, documentation, release metadata, and full pack
      checks pass.

## Out of Scope

- General proofreading or style editing.
- Declaring subjective opinions true or false.
- Publishing corrected material without a separate request.

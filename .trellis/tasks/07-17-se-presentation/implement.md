# Implement se-presentation Implementation Plan

## Execution Order

1. Add fixtures and failing tests for source inventory, audience outcome, and slide traceability.
2. Implement story arc, timed one-claim slide sequence, evidence, visual intent, and notes.
3. Add short/standard variants, omission ledger, accessibility checks, questions, and production handoff.
4. Integrate read-only profile voice, register under Create, add docs/release metadata, and regenerate.
5. Run focused/full checks and inspect generated specifications.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manually exercise executive/technical variants, severe time constraint, sparse
  evidence, dense citations, sensitive content, unsupported charts, and profile off.

## Documentation And Spec Updates

Document slide-spec schema, evidence/visual labels, timed variants, accessibility,
profile use, and the handoff to deck-production tooling.

## Review Notes

Confirm every slide advances the stated outcome and all speaker/visual claims are
traceable or clearly proposed.

## Follow-Ups

Deck-file generation and rehearsal assistance remain separate capabilities.

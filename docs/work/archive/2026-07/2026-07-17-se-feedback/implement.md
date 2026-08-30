# Implement se-feedback Implementation Plan

## Execution Order

1. Add fixtures and failing tests for atomic extraction, duplicate detection, and traceable clustering.
2. Implement the feedback ledger, theme synthesis, contradiction/minority retention, and outcome mapping.
3. Add disposition recommendations, clarification/test actions, and unresolved-feedback output.
4. Register under Improve, add shared references, docs/release metadata, and regenerate.
5. Run focused/full checks and inspect generated payloads.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manually exercise duplicates, opposed audiences, vague feedback, a lone severe
  concern, stale feedback, missing roles, and injected instructions.

## Documentation And Spec Updates

Document atomic-to-theme traceability, frequency-versus-correctness, supported
dispositions, minority preservation, and the read-only boundary.

## Review Notes

Trace every theme and recommendation to atomic evidence and confirm aggregation
cannot silently discard disagreement or severity.

## Follow-Ups

Replying, resolving review threads, or editing artifacts remains separate work.

# Implement se-thread-digest Implementation Plan

## Execution Order

1. Add synthetic conversation fixtures and failing tests for scope, evidence, and state classification.
2. Implement message inventory and evidence-linked decision, commitment, question, and disagreement ledgers.
3. Add corrections/edits/gaps, privacy controls, concise digest, and downstream portable payloads.
4. Register under Coordinate, add shared references, safety/docs/release metadata, and regenerate.
5. Run focused/full checks and inspect generated payloads.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manually exercise no decision, conflicting/corrected messages, edits, deleted context,
  reaction-only responses, unclear owner/date, private scope, and posting requests.

## Documentation And Spec Updates

Document required scope/window, conversational state semantics, evidence links,
privacy boundaries, downstream handoffs, and read-only connector behavior.

## Review Notes

Trace every decision and commitment to decisive messages and ensure ambiguity
remains visible rather than being resolved by narrative smoothing.

## Follow-Ups

Channel monitoring and posting summaries remain separate Slack integrations.

# Implement se-explain Implementation Plan

## Execution Order

1. Add audience, false-premise, analogy, current-claim, and follow-up tests.
2. Implement a standard explanation skeleton with explicit limitations.
3. Add depth/audience variants, walkthrough/QA formats, and progressive follow-ups.
4. Register under Understand, add shared source/safety coverage, docs, release, generation.
5. Run focused and full checks.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manual novice/expert explanations, false premise, analogy breakdown, current
  API claim, and successive zoom-in questions.

## Documentation And Spec Updates

Document trigger boundaries and the explanation layer/analogy contract.

## Review Notes

Check accuracy at every simplification boundary and ensure examples do not
masquerade as evidence.

## Follow-Ups

Route durable learning sequences to `se-learn`; do not grow this skill into a curriculum.

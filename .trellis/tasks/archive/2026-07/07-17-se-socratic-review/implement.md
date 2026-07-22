# Implement se-socratic-review Implementation Plan

## Execution Order

1. Add multi-turn synthetic transcripts and failing one-question/adaptation tests.
2. Implement target contract, one-question loop, response classification, and stop behavior.
3. Add misconception repair, help contamination, transfer checks, and final evidence report.
4. Register under Understand, add conditional source/safety coverage, docs/release, regenerate.
5. Run focused/full checks and manually exercise dialogue paths.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manual correct guess, deep reasoning, partial answer, misconception loop,
  requested hint, reveal, stop, and time/question limit.

## Documentation And Spec Updates

Document formative/non-grading use, one-question contract, adaptation evidence,
and boundaries from learning paths/study guides.

## Review Notes

Inspect each prompt for hidden multiple questions or leading answer content;
ensure conclusions cite demonstrated responses.

## Follow-Ups

Persistent progress storage and formal assessment remain separate future capabilities.

# Implement se-topic-radar Implementation Plan

## Execution Order

1. Add synthetic activity/news/prior-content fixtures and failing coverage/scoring tests.
2. Implement source inventory, signal extraction, candidate generation, and duplicate detection.
3. Add transparent scoring, privacy/profile rules, adequacy gate, ranked output, and author/paper handoff.
4. Register under Create, add current-source/profile references, docs/release metadata, and regenerate.
5. Run focused/full checks and inspect rankings for distinctness and evidence.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manually exercise rich and absent activity, stale and breaking news, duplicate
  prior topics, private work, low evidence, effort limits, and profile off.

## Documentation And Spec Updates

Document source coverage, scoring rubric, exactly-ten adequacy condition, duplicate/
privacy rules, current-research requirements, and downstream selection handoff.

## Review Notes

Trace every score and “why positioned” claim to authorized evidence and ensure
the list is neither trend-padding nor sensitive-activity leakage.

## Follow-Ups

Continuous monitoring and editorial-calendar maintenance remain separate skills.

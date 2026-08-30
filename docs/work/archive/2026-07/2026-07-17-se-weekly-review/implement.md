# Implement se-weekly-review Implementation Plan

## Execution Order

1. Add multi-source weekly fixtures and failing timezone/coverage/dedupe tests.
2. Implement worklog/profile resolution, bounded source inventory, and normalized activity ledger.
3. Add outcome/activity/carryover/lesson/pattern/focus synthesis and portable capture output.
4. Register under Improve, add status/retro/profile references, docs/release metadata, and regenerate.
5. Run focused/full checks and inspect rich and sparse-week outputs.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manually exercise Denver boundary, missing/duplicate sources, sparse week,
  private configuration, energy inference, profile off, and status/retro overlap.

## Documentation And Spec Updates

Document personal configuration boundary, reporting-window semantics, source
coverage/dedupe, section distinctions, profile read-only behavior, and capture handoff.

## Review Notes

Confirm every claimed outcome or pattern has evidence and private configuration
never enters public canonical assets.

## Follow-Ups

Automatic publication, task mutation, and profile updates remain separate workflows.

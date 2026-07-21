# Implement se-technical-editor Implementation Plan

## Execution Order

1. Add draft/evidence fixtures and failing tests for review passes, finding classes, and approval boundaries.
2. Implement scoped passes and the severity/location/rationale/action editorial report.
3. Add code/citation validation states, voice sample, generic-prose evidence, revision plan, and change ledger.
4. Integrate read-only profile preferences, register under Improve, add docs/release metadata, and regenerate.
5. Run focused/full checks and inspect report and approved-edit modes.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manually exercise wrong-but-fluent prose, citation mismatch, unrun code,
  confidentiality, voice conflict, style-only feedback, and unauthorized rewrite.

## Documentation And Spec Updates

Document pass taxonomy, finding classes, verification language, report/edit modes,
approval requirements, voice preservation, and profile constraints.

## Review Notes

Confirm every finding is located and justified and no substantive edit occurs
without the requested authority.

## Follow-Ups

Primary research, topic discovery, and direct publication remain separate workflows.

# Implement se-proposal Implementation Plan

## Execution Order

1. Add fixtures and failing tests for authority, evidence classes, alternatives, and explicit ask.
2. Implement interview, proposal brief approval, decision requirements, objections, and evidence gaps.
3. Add full proposal structure, estimates/assumptions, do-nothing baseline, risks, and plan handoff.
4. Integrate read-only profile framing, register under Create, add docs/release metadata, and regenerate.
5. Run focused/full checks and inspect generated payloads.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manually exercise missing authority, weak evidence, conflicting stakeholders,
  rejected framing, uncertain costs, invalid profile inference, and explicit rejection.

## Documentation And Spec Updates

Document interview/approval gates, evidence-estimate-assumption labels, alternatives,
do-nothing baseline, profile constraints, and accepted-proposal handoff.

## Review Notes

Verify material claims are classified and sourced, and persuasive framing never
silently converts assumptions into evidence.

## Follow-Ups

Negotiation, approval, task creation, and implementation planning remain separate workflows.

# Implement se-paper Implementation Plan

## Execution Order

1. Add fixtures and failing tests for brief approval, search protocol, and evidence provenance.
2. Implement topic selection/interview, research brief, method/evidence feasibility, and ethics gates.
3. Add literature coverage, evidence/decision ledger, disciplined section drafting, limitations, and reproducibility inventory.
4. Integrate read-only profile framing, register under Create, add docs/release metadata, and regenerate.
5. Run focused/full checks and inspect generated payloads.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manually exercise no question, weak literature, inaccessible data, null and
  contradictory results, ethics stop, venue variation, citation mismatch, and profile off.

## Documentation And Spec Updates

Document research gates, coverage claims, provenance, method/result/interpretation
separation, reproducibility and ethics disclosures, plus profile-use constraints.

## Review Notes

Verify claims trace to literature/data/analysis or labeled interpretation and no
preferred narrative can overwrite negative or inconclusive evidence.

## Follow-Ups

Journal submission, ethics approval, data collection, and execution remain separate workflows.

# Implement se-red-team Implementation Plan

## Execution Order

1. Add artifact/threat fixtures and failing tests for steelman and finding classification.
2. Implement frame resolution and adversarial passes across assumptions, evidence, incentives, misuse, and reversals.
3. Add finding schema, mitigation/closure evidence, sensitive-detail control, no-findings output, and routing.
4. Register under Improve, add source/security references, docs/release metadata, and regenerate.
5. Run focused/full checks and inspect generated reviews.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manually exercise a strong artifact, weak assumption, unsupported adversary,
  value dispute, sensitive vulnerability, no findings, and depth variants.

## Documentation And Spec Updates

Document steelman-first behavior, finding classes, severity/evidence schema,
sensitive-detail rules, closure evidence, and fact-check/evaluate boundaries.

## Review Notes

Confirm demonstrated defects have evidence and plausible/speculative cases never
read as known vulnerabilities.

## Follow-Ups

Offensive testing and mitigation implementation remain separate authorized work.

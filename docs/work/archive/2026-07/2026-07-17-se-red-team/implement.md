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

## Rollback Points

- Before registration: remove the canonical template and focused tests if the
  contract cannot keep speculative security cases distinct from known defects.
- Before generation: revert registry/reference and release metadata together;
  never hand-edit generated manifest or catalog rows.
- Before shipping: require idempotent generation, focused tests, full checks,
  install fan-out audit, and a clean diff.

## Review Notes

Confirm demonstrated defects have evidence and plausible/speculative cases never
read as known vulnerabilities.

## Follow-Ups

Offensive testing and mitigation implementation remain separate authorized work.

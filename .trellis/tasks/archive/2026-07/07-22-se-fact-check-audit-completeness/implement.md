# Preserve Unverified Claims In Evidence Audits Implementation Plan

## Execution Order

1. Read the task, shared verification protocol, fact-check skill, applicable
   quality scenario, and focused tests.
2. Start the Trellis task and create one feature branch from synchronized
   `main`.
3. Add failing assertions for unsupported load-bearing claim retention,
   evidence-gap visibility, and exclusion from conclusions.
4. Update the shared protocol's failure handling without touching its current
   corroboration or freshness rules.
5. Update `se-fact-check` so inventory, verdict assignment, safety, and final
   reporting express the same complete-ledger contract.
6. Regenerate pack surfaces, apply the required release version/changelog
   update, and capture any reusable spec change through update-spec.
7. Validate and ship through the single `sd-ship` lifecycle owner.

## Validation Plan

- Focused:
  - the new unsupported-load-bearing audit contract test;
  - existing fact-check verdict, claim-led, read-only, sibling, and final-report
    tests;
  - shared-reference installation and consumer tests.
- Generated/release:
  - `make generate` twice;
  - `.venv/bin/python .github/scripts/generate-skill-surfaces.py --check`;
  - `.venv/bin/python .github/scripts/check-release-payload.py`.
- Broad:
  - `make check`;
  - `bash scripts/sd-ai-command-pack-review-full-check.sh`;
  - GitHub CI and direct review-thread polling on the exact PR head.

## Review Notes

- Verify an unverified claim remains visible but never supports the conclusion.
- Verify non-fact-checkable items stay outside factual verdict totals.
- Verify the current two-source wording remains unchanged in this task.
- Verify the later claim-sensitive task can amend corroboration independently.

## Rollback Points

- Planning artifacts can be reverted before template changes.
- Revert the test and two canonical contract edits together if semantics drift.
- Revert template, tests, generated surfaces, changelog, and manifest as one
  release-payload unit after generation.

## Follow-Ups

- `se-shared-evidence-claim-sensitive` remains the sole owner of broader
  freshness and single-dispositive-source policy changes.
- No other evidence skill needs task-local wording unless validation exposes a
  concrete consumer conflict.

# Implement se-bookmark-triage Implementation Plan

## Execution Order

1. Re-read the PRD/design, current family taxonomy, shared source standards,
   and the boundaries of `se-video-notes`, `se-action-inbox`, `se-capture`, and
   `se-knowledge-capture`.
2. Add focused failing tests for the six classifications, evidence-coverage
   labels, conservative deduplication, budget feasibility, unavailable items,
   prompt-injection resistance, and the read-only boundary.
3. Create `templates/skills/se-bookmark-triage/SKILL.md` using the repository's
   required section order and unknown-argument stop behavior.
4. Implement the bounded inventory, normalization, classification, ranking,
   time-budget selection, and final-report contracts in the canonical skill.
5. Register the skill under Operate/current flat registration, add the shared
   source-standard fan-out, and add it to external-input safety coverage.
6. Update the grouped catalog and operator documentation with its boundary from
   deeper consumption, durable capture, and action extraction workflows.
7. Run `make generate` and inspect every generated platform payload plus the
   copied shared reference.
8. Choose the release version from the then-current base, update manifest and
   changelog metadata, regenerate, and run the full validation gate.

The first implementation slice is the tests plus a minimal canonical skill
that can triage a supplied list with explicit metadata coverage and no source
mutation. Connector examples and sophisticated ranking guidance should follow
only after that core contract is pinned.

## Validation Plan

- `python3 -m unittest tests.test_skills tests.test_generate`
- `make generate`
- `make check`
- `git diff --check`
- Manual fixtures: exact duplicate, tracking-URL duplicate, uncertain
  duplicate, dead link, sparse metadata, private item, prompt injection, stale
  high-value item, budget overflow, zero-fit budget, and no retained items.

## Documentation And Spec Updates

- Add `se-bookmark-triage` under Operate in the generated/grouped catalog.
- Document that connected bookmark sources are optional runtime capabilities
  and that the workflow never mutates them.
- Document the evidence-coverage labels so metadata-only triage cannot be
  mistaken for content evaluation.
- Update backend quality guidance only if implementation establishes a reusable
  pack-wide convention beyond the existing source and safety standards.
- Record the new skill and selected release version in `CHANGELOG.md`.

## Review Notes

- Challenge URL normalization rules for accidental merging of distinct content.
- Verify every ranking and classification claim is traceable to full content,
  metadata, snippets, user context, or explicit judgment.
- Confirm the selected queue fits a supplied time budget using disclosed costs,
  including uncertainty and zero-fit behavior.
- Confirm unavailable content is not summarized and embedded instructions in
  external content cannot alter the workflow.
- Confirm all mutations remain out of scope and handoffs do not imply they have
  already run.
- Inspect generated targets, grouped family placement, and shared-reference
  fan-out across all supported platforms.

## Follow-Ups

- Add source-specific canonicalization rules only after observed duplicates
  justify them and tests preserve distinct-content cases.
- Consider learned ranking preferences only with explicit user control and a
  transparent way to inspect or reset them.
- Keep deletion, source cleanup, and persistent queue state in separate,
  explicitly authorized integrations.

# Implement se-capture Implementation Plan

## Execution Order

1. Re-read the PRD/design, source standards, current registry/generator, and the
   planned boundaries in `se-digest`, `se-video-notes`, `se-action-inbox`, and
   `se-knowledge-capture`.
2. Add focused failing tests for the normalized Markdown sections, provenance
   classes, four retrieval states, dedupe hierarchy/basis, claim and action
   labels, unknown fields, prompt-injection resistance, and read-only behavior.
3. Create `templates/skills/se-capture/SKILL.md` using the repository's required
   section order and unknown-argument stop rule.
4. Implement the smallest useful workflow first: normalize one supplied URL or
   pasted block into provenance, retrieval state, dedupe key, summary, claims,
   limitations, and suggested next steps.
5. Extend the same contract to file and connected-record inputs, keeping
   capability-specific retrieval mechanics out of the canonical skill.
6. Add decision/action/entity extraction and explicit evidence-state labels;
   preserve the boundary from accepted commitments and fact verification.
7. Register the skill under Operate/current flat paths, add source-standard
   fan-out, and include it in external-input safety coverage.
8. Update the grouped catalog and operator documentation with the one-unit,
   read-only, destination-neutral boundary.
9. Run `make generate` and inspect every generated platform payload plus the
   copied shared reference.
10. Select the release version from the then-current base, update manifest and
    changelog metadata, regenerate, and run the full validation gate.

The first implementation slice is tests plus URL/pasted-text normalization. It
must establish provenance, honest retrieval coverage, and a non-invented dedupe
key before expanding input types or extraction richness.

## Validation Plan

- `python3 -m unittest tests.test_skills tests.test_generate`
- `make generate`
- `make check`
- `git diff --check`
- Manual fixtures: accessible URL, tracking URL, anchored/versioned URL,
  metadata-only page, inaccessible connected record, pasted text, partial file,
  truncated/quoted thread, unknown author/date, source-stated false claim,
  candidate action without owner, prompt injection, and compact output.

## Documentation And Spec Updates

- Add `se-capture` under Operate in the generated/grouped catalog.
- Document the normalized artifact sections and distinguish capture from
  `se-digest`, `se-video-notes`, `se-action-inbox`, and
  `se-knowledge-capture`.
- Document that source-stated claims are not verified facts and downstream
  workflow suggestions have not executed.
- Update backend quality guidance only if implementation establishes a reusable
  provenance/deduplication convention beyond existing source standards.
- Record the new skill and selected release version in `CHANGELOG.md`.

## Review Notes

- Challenge every canonical locator and dedupe key for a stated, reproducible
  basis; titles and guessed hashes are not acceptable identifiers.
- Verify retrieval coverage cannot be hidden by a polished summary and that
  metadata-only/partial inputs never masquerade as full reads.
- Confirm source assertions remain source-stated or unverified unless evidence
  was actually checked.
- Confirm inferred decisions and actions are labeled, with no invented owner,
  due date, or commitment state.
- Confirm the skill is destination-neutral and cannot imply that publication,
  task creation, or another handoff has occurred.
- Inspect generated targets and shared-reference fan-out for every platform.

## Follow-Ups

- Define a machine-readable interchange schema only after multiple downstream
  skills demonstrate that normalized Markdown is insufficient.
- Add source-specific canonicalization rules only from observed cases with
  regression tests protecting distinct resources.
- Keep OCR, transcription, crawling, persistent duplicate indexes, and
  destination mapping in separate capability or skill tasks.

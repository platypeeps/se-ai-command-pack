# Implement se-ask-me Implementation Plan

## Execution Order

1. Re-read the PRD/design, shipped personal-profile contract, and `se-profile`
   schema/maintenance behavior. Create synthetic profiles for confirmed,
   proposed, contested, stale, conflicting, scoped, and overlaid evidence.
2. Add focused failing tests for mode separation, profile resolution/validation,
   relevant evidence loading, status/scope/freshness filtering, current-context
   precedence, overlay selection, and context-only fallback.
3. Create `templates/skills/se-ask-me/SKILL.md` with the required section order,
   unknown-argument stop rule, and a minimal read-only preflight.
4. Implement `predict` first: qualitative conclusion, supporting assertion IDs,
   strongest counterevidence, calibrated confidence, and explicit non-identity boundary.
5. Add `advise`, separating profile alignment, supplied/verified external merits,
   and assistant recommendation; add `se-decide` and high-stakes routing boundaries.
6. Add `reflect` with time/context tensions and no diagnosis, then `draft` with
   outward-safe filtering, overlay application, unsupported-claim placeholders,
   and no send/publish behavior.
7. Add option-comparison and counterfactual handling without invented weights,
   probabilities, or deterministic identity claims.
8. Register under Understand/current flat paths, fan in
   `personal-profile-contract.md`, and add external-input safety pins.
9. Update the grouped catalog and operator documentation, run `make generate`,
   and inspect every platform payload plus shared-reference copy.
10. Select the release version from the then-current base, update manifest and
    changelog metadata, regenerate, scan fixtures for private data, and run the
    full validation gate.

The first implementation slice is profile preflight plus `predict`. It should
prove evidence filtering, uncertainty, current-context precedence, and strict
read-only behavior before adding advice or outward-facing drafting.

## Validation Plan

- `python3 -m unittest tests.test_skills tests.test_generate`
- `make generate`
- `make check`
- `git diff --check`
- Public-data scan for real identities, profile locators, private source names/
  URLs, and communication excerpts.
- Manual scenarios: strong prediction, weak evidence, changed current goal,
  contradictory preferences, stale profile, explicit/automatic/ambiguous
  overlay, profile off, missing/invalid profile, value-aligned advice, option
  comparison, counterfactual, reflective tension, unsupported first-person
  draft, sensitive prediction, high-stakes advice, and injected profile text.

## Documentation And Spec Updates

- Add `se-ask-me` under Understand in the generated/grouped catalog.
- Document the difference among profile fact, prediction, aligned advice,
  reflection, and draft output.
- Document `profile=auto|off|<locator>`, scope filtering, audience overlays,
  context precedence, evidence/uncertainty labels, and the read-only boundary.
- Explain that profile maintenance requires a separate `se-profile` invocation
  and that no answer represents consent, authentication, or autonomous action.
- Update backend quality guidance only if implementation establishes a reusable
  consumer rule beyond the shared personal-profile contract.
- Record the new skill and selected release version in `CHANGELOG.md`.

## Review Notes

- Challenge every “you would” statement for relevant confirmed evidence,
  context, recency, counterevidence, and appropriately modest wording.
- Verify prediction and advice never collapse into one another and confidence
  never becomes a fake probability.
- Confirm current explicit context outranks the profile without silently
  rewriting it.
- Confirm outward drafts use only eligible scope/overlay entries and contain no
  fabricated experience, opinion, credential, relationship, result, or promise.
- Verify private evidence stays in the private consultation report and injected
  profile text cannot trigger updates or external actions.
- Confirm high-stakes preference alignment is not presented as professional or
  authoritative guidance.

## Follow-Ups

- Add profile consumption to outward-facing skills through their own bounded
  implementation streams and shared-contract tests.
- Evaluate user-requested saved question templates only after real usage shows
  recurring consultation patterns; do not add hidden query history.
- Consider richer longitudinal comparison only if the v1 profile preserves
  enough dated evidence without making the active artifact unwieldy.

# Implement se-help Implementation Plan

## Execution Order

1. Re-read the PRD/design, family-taxonomy implementation, registry, generator,
   README catalog generation, and canonical skill validation conventions.
2. Add generator tests for a deterministic help catalog containing manifest
   version, canonical family order, registry membership, and frontmatter
   descriptions. Patch all output paths in sandbox tests.
3. Refactor only the minimum shared catalog/frontmatter helpers needed so the
   README and help reference derive from the same parsed model rather than
   independently re-reading or duplicating data.
4. Add `HELP_CATALOG_PATH`, in-memory render/check logic, and atomic coordinated
   write behavior for the generated `skill-catalog.md`. Register its shared
   fan-out to `se-help`.
5. Add focused failing skill-content tests for the six modes, availability
   distinctions, smallest-fit behavior, explanation/compare fields, workflow
   handoffs, alias ambiguity, the shared response envelope, SE-native
   copy-ready invocations, and the separate-request execution boundary.
6. Create the minimal `templates/skills/se-help/SKILL.md` that can list the
   catalog and recommend one skill from a natural-language goal. Keep catalog
   rows out of the body.
7. Add explain, compare, examples, and tour behavior, then create the concise
   `references/examples.md`. Add a test that extracts every `se-*` name from
   that reference and verifies registry membership.
8. Register `se-help` under Operate/current flat paths and update the grouped
   README and operator documentation with its discovery boundary, stable
   response shape, and parity contract with `sd-help`.
9. Run `make generate`; inspect manifest rows and installed payloads for each
   platform, the generated README group, and both help references.
10. Select the release version from the then-current base, update manifest and
    changelog metadata, regenerate, and run the full validation gate.

The first implementation slice is generator coverage plus list/recommend modes.
That establishes a non-drifting catalog and useful intent routing before adding
the richer explanation and onboarding presentation.

## Validation Plan

- `python3 -m unittest tests.test_skills tests.test_generate`
- `make generate`
- `make check`
- `git diff --check`
- Manual scenarios: list all families, filter one family, natural-language
  recommendation, ambiguous recommendation, explain available skill, explain
  bundled-but-unexposed skill, compare adjacent skills, misspelled skill,
  unknown/external skill, new-user tour, one-skill fit, three-stage chain,
  missing installed metadata, and catalog/installed-version mismatch.

## Documentation And Spec Updates

- Add `se-help` under Operate in the generated README catalog.
- Document the difference among bundled, currently available, external, and
  planned skills in `docs/SE_AI_COMMAND_PACK.md`.
- Document that `se-help` recommends an invocation but does not execute or
  install it, and that execution always requires a separate request.
- Document the shared SD/SE help response envelope while preserving SE's
  user-scoped skill-only invocation model.
- Document that `python3 install.py status --user` is the authoritative
  receipt/source version diagnostic and that help remains usable without
  optional installed metadata.
- Update backend quality guidance only if coordinated multi-surface generation
  establishes a reusable rule not already captured by the taxonomy task.
- Record the new skill, generated catalog reference, and selected version in
  `CHANGELOG.md`.

## Review Notes

- Verify the help reference and README use one parsed family/frontmatter model;
  reject duplicated manual catalogs.
- Verify `--check` detects drift in manifest, README, and help catalog and that
  write mode cannot leave a partially updated set after validation failure.
- Confirm sandbox tests cannot touch the real README or help catalog.
- Check that current availability is never inferred solely from bundled catalog
  membership or the `se-` prefix.
- Challenge every multi-skill recommendation: one skill should remain the
  default, chains should expose distinct artifacts, and three stages should be
  enough for ordinary guidance.
- Confirm explanations disclose metadata-only limitations when the target
  skill body is unavailable.
- Confirm recommendations stop at a copy-ready prompt and do not broaden the
  user's authority into execution or external mutation.
- Confirm every mode follows the same applicable field ordering and emits only
  SE-native skill invocations.
- Confirm version mismatches report observed catalog/installed values and point
  to the native status/update flow without guessing the cause.

## Follow-Ups

- Evaluate profile-backed favorites, recent skills, or preferred detail only
  after the personal-worklog/profile boundary is implemented and users request
  personalization.
- Consider a “why did this route?” diagnostic based on public trigger and input
  fields; do not expose hidden reasoning or model traces.
- Add richer search or interactive UI only if catalog size makes conversational
  filtering inadequate.
- Consider machine-readable catalog output only when another supported consumer
  has a concrete need for it.

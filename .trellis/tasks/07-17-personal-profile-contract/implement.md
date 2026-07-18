# Design the personal profile integration contract Implementation Plan

## Execution Order

1. Review the PRD/design with the user, focusing on assertion fields, visibility
   scopes, profile discovery, audience-overlay selection, and the initial
   consumer list. Record changes without adding personal example data.
2. Create synthetic v1 profile fixtures for a base profile, sparse overlay,
   proposed inference, contradiction, stale entry, manual edit, and generated-
   output feedback loop. Use them to challenge the schema before it ships.
3. Update the `se-profile` and `se-ask-me` designs to consume the approved schema
   and assign ownership: only `se-profile` mutates; all other consumers are read-only.
4. Add the profile argument/precedence contract to planned outward-facing skill
   tasks as they are designed. Do not bulk-edit implemented skills without a
   bounded release and focused tests.
5. Mark this design decision complete once schema, precedence, persistence,
   overlay, review, privacy, and consumer contracts are approved. Do not add a
   manifest row or release bump for planning artifacts.
6. In the `se-profile` implementation stream, create the shared
   `personal-profile-contract.md`, register its initial consumers, add tests,
   generate payloads, update docs/release metadata, and run the full gate.

The first safe next step is synthetic schema review. It tests whether a human
can inspect and correct the artifact before any connector write workflow or
cross-skill fan-out is implemented.

## Validation Plan

- `git diff --check`
- Manual schema matrix: explicit/observed/inferred basis crossed with
  confirmed/proposed/contested/retired status and all three visibility scopes.
- Manual overlay matrix: explicit match, unique automatic match, ambiguity,
  combination conflict, stale overlay, and attempted boundary weakening.
- Manual consumer matrix: profile off, missing locator, stale profile, private
  evidence, conflicting voice preferences, explicit user override, venue
  constraint, and unsupported first-person claim.
- Manual persistence matrix: new Obsidian note, preserved manual edit, failed
  write, failed read-back, unavailable Obsidian with Notion fallback, export,
  and schema migration.
- Privacy scan of every public artifact and synthetic fixture.

## Documentation And Spec Updates

- Keep personal paths, destinations, source inventories, and profile instances
  in private owning surfaces.
- When the contract ships with `se-profile`, document profile opt-in/discovery,
  scopes, overlays, review, correction/forgetting, and `profile=off` in the
  operator guide.
- Add a repo spec only after implementation proves a reusable rule; the likely
  candidate is that public skills may consume private profiles only through an
  explicit shared contract and never mutate them incidentally.
- This design-only task does not update README, changelog, manifest, or version.

## Review Notes

- Reject examples containing real personal values, paths, identities, private
  URLs, channel names, or excerpts.
- Verify stable IDs and provenance do not make the file too opaque for direct
  user editing.
- Challenge every default profile load for prior opt-in and every outward use
  for scope, freshness, audience fit, and disclosure safety.
- Verify overlays remain sparse and cannot suppress boundaries or fabricate a
  separate persona.
- Verify generated outputs cannot recursively validate the model that produced them.
- Confirm the profile is never treated as authentication, consent to external
  action, or proof of a current opinion/commitment.

## Follow-Ups

- `se-profile` implements creation, maintenance, persistence, review, overlays,
  correction, forgetting, import, and export.
- `se-ask-me` implements evidence-aware, read-only self-consultation.
- Each outward-facing consumer adopts the shared contract in its own bounded
  implementation or release stream.
- Consider a machine-readable index or split evidence archive only after a real
  profile demonstrates that one Markdown artifact is too large or slow.
- Consider installer-level profile discovery only after at least two host
  platforms need the same configuration and migration behavior.

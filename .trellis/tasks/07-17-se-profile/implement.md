# Implement se-profile Implementation Plan

## Execution Order

1. Re-read the PRD/design and approved personal-profile contract. Create only
   synthetic v1 profile fixtures covering valid, proposed, contested, stale,
   malformed, conflicting, and manually edited states.
2. Add focused failing tests for mode/argument coverage, common preflight,
   schema fields/enums, stable IDs, bounded sources, sensitive-trait exclusion,
   evidence lineage, approval boundaries, preservation, and verified read-back.
3. Add `templates/skills/_shared/references/personal-profile-contract.md` from
   the approved contract, keeping the canonical skill body focused on workflow.
4. Create the minimal `templates/skills/se-profile/SKILL.md` supporting
   `create`, `status`, a direct explicit correction, and read-back verification
   against one user-selected destination.
5. Add source-backed `propose-update` and `apply-approved`, including numbered
   proposals, concurrent re-read, derivative-output detection, and prompt-
   injection protection.
6. Add `correct` and `forget`, including visibility/sensitive/destructive
   confirmation boundaries, cross-reference cleanup, and honest deletion scope.
7. Add `review` and `audience` modes with sparse overlays, feedback-loop and
   overgeneralization checks, cadence-as-preference, and item-level approvals.
8. Add import/export validation and explicit Obsidian-primary/Notion-fallback
   behavior without connector-specific API instructions in the canonical skill.
9. Register `se-profile` under Operate/current flat paths, fan in the personal
   profile contract and source standards, and add external-input safety pins.
10. Update the grouped catalog/operator documentation, run `make generate`, and
    inspect every platform payload plus shared-reference copy.
11. Select the release version from the then-current base, update manifest and
    changelog metadata, regenerate, scan fixtures for private data, and run the
    full validation gate.

The first implementation slice is deliberately narrow: synthetic schema tests,
the shared contract, profile creation/status, and one explicit correction with
verified persistence. Source inference, review, overlays, and import follow only
after that ownership and write boundary is pinned.

## Validation Plan

- `python3 -m unittest tests.test_skills tests.test_generate`
- `make generate`
- `make check`
- `git diff --check`
- Public-data scan for real identities, personal paths, vault/workspace/channel
  names, private URLs, credentials, and source excerpts.
- Manual scenarios: first-run interview, skipped categories, malformed profile,
  direct preference, outward-scope broadening, observed proposal, inferred
  proposal, contradiction, concurrent edit, stale review, generated-output
  feedback loop, overlay merge conflict, entry/evidence/whole-profile forget,
  Obsidian outage, explicit Notion fallback, import conflict, and redacted export.

## Documentation And Spec Updates

- Add `se-profile` under Operate in the generated/grouped catalog.
- Document the v1 artifact, profile ownership, bounded-source consent,
  approval/write/read-back lifecycle, visibility scopes, audience overlays,
  review cadence, correction/forgetting, and verified deletion limits.
- Document that private locator configuration is host-owned and that the public
  installer stores no profile location or content.
- Document that all other skills are read-only consumers and support
  `profile=off` when they adopt the contract.
- Add a backend quality spec only if implementation establishes a general rule
  beyond the shared contract, such as preserving user-owned sections across
  connector-neutral semantic writes.
- Record the new skill, shared contract, and selected release version in `CHANGELOG.md`.

## Review Notes

- Reject any real personal datum or plausible private locator in public tests,
  examples, docs, or task artifacts.
- Challenge every source scope for bounded consent and every assertion for
  atomic wording, subject/authorship, evidence lineage, context, and visibility.
- Confirm inferred traits cannot become confirmed and sensitive traits cannot
  be inferred at all.
- Verify simple explicit maintenance does not create needless friction, while
  conflicts, broader visibility, boundaries, sensitive facts, migration, and
  deletion receive explicit confirmation.
- Confirm every mutation re-reads current state, preserves unknown/user-owned
  content, writes, reads back, and verifies semantic IDs.
- Verify forget reports the systems actually checked and never promises erasure
  from backups, history, or prior model context.
- Confirm cadence does not schedule or authorize recurring ingestion and that
  consumer use never writes back.

## Follow-Ups

- Implement `se-ask-me` as the first read-only consumer after the profile
  contract and maintenance path are stable.
- Adopt profile consumption in outward-facing skills through bounded per-skill
  changes or as each planned skill is implemented.
- Consider a split evidence archive only after real profiles demonstrate that
  one Markdown artifact is too large; preserve portable export if introduced.
- Consider installer-level locator configuration only after multiple host
  platforms require the same discovery/migration contract.

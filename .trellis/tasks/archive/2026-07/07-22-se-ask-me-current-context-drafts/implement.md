# Allow Explicit Current Context In SE Ask Me Drafts Implementation Plan

## Execution Order

1. Read the task artifacts, `se-ask-me` template, focused tests, applicable
   Trellis quality specs, and shared profile contract.
2. Start the Trellis task and create one feature branch from synchronized
   `main`.
3. Add focused failing assertions for request-scoped current-context
   eligibility, unchanged profile/overlay gates, ambiguity handling, and no
   persistence.
4. Update only the canonical `templates/skills/se-ask-me/SKILL.md` contract:
   define evidence classes, apply visibility before draft use, keep profile
   eligibility unchanged, and separate current context in the final report.
5. Run focused tests, then `make generate` twice. Update the manifest version
   and changelog when required by the release-payload gate.
6. Capture any reusable contract through the normal update-spec stage, refresh
   repository maps/KB through their owners, and commit coherent batches.
7. Run the full deterministic gate and ship through the single `sd-ship`
   lifecycle owner.

## Validation Plan

- Focused:
  - `.venv/bin/python -m unittest tests.test_skills.SkillSafetyPinsTest.test_ask_me_separates_modes_evidence_and_uncertainty`
  - `.venv/bin/python -m unittest tests.test_skills.SkillSafetyPinsTest.test_ask_me_preserves_scope_identity_and_authority`
  - the new current-context draft contract test.
- Generated/release:
  - `make generate` twice;
  - `.venv/bin/python .github/scripts/generate-skill-surfaces.py --check`;
  - `.venv/bin/python .github/scripts/check-release-payload.py`.
- Broad:
  - `bash scripts/sd-ai-command-pack-review-full-check.sh`;
  - GitHub CI and direct review-thread verification on the current PR head.

## Documentation And Spec Updates

- Keep user-facing behavior in the canonical skill rather than a separate
  duplicated guide.
- Add a changelog entry and version bump when the release payload gate requires
  them.
- Let `sd-update-spec` decide whether the request-scoped versus durable-profile
  evidence distinction is reusable enough for
  `.trellis/spec/backend/quality-guidelines.md`.
- Regenerate catalogs and refresh the Obsidian KB through existing scripts.

## Review Notes

- Verify that current context cannot be used as a generic escape hatch for
  private profile facts or untrusted source text.
- Verify outward visibility is explicit for audience-sensitive first-person
  claims.
- Verify the text does not imply that current context persists or confirms the
  durable profile.
- Verify contradictions prefer the current request without silently rewriting
  profile history.

## Rollback Points

- Before changing the template, planning artifacts can be reverted without
  payload impact.
- Before the version bump, revert the focused template/test batch together.
- After generation, revert template, tests, generated surfaces, changelog, and
  manifest as one release-payload unit.

## Follow-Ups

- Broader profile-contract changes or new persistence behavior are out of
  scope and require separate Trellis tasks.
- No analyzer, routing, or other SE skill changes belong in this PR.

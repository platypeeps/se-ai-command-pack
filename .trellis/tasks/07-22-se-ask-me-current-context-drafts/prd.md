# Allow explicit current context in se-ask-me drafts

## Goal

Review snapshot 726d2d57c275b1d600940fbd523528081a43a898bfdaac2cdad34dec06fba0ae; finding 5.2.5.1. Permit explicit current-task statements in outward drafts while retaining confirmed outward-safe eligibility for profile-derived assertions. Affected template: templates/skills/se-ask-me/SKILL.md; focused tests under tests/test_skills.py.

## Requirements

- Let outward draft mode use an explicit factual statement supplied by the user
  for the current draft even when it is not stored in the durable profile.
- Label such evidence as current context and keep it distinct from durable
  profile assertions.
- Continue to require `confirmed` and `outward-safe` eligibility for facts
  derived from the profile or an overlay.
- Preserve the focused-question or marked-placeholder path for ambiguous
  visibility, authority, experience, opinion, credentials, relationships,
  results, promises, and availability.
- Keep `se-ask-me` read-only; this task must not update the profile.
- Change only canonical templates under `templates/skills/**`, then regenerate
  supported targets through the normal sync path.

## Acceptance Criteria

- [ ] A user-supplied current-task fact can appear in the requested outward
      draft without first being persisted to the profile.
- [ ] A private-only profile assertion remains excluded from outward output.
- [ ] An ambiguous current statement produces a question or marked placeholder.
- [ ] Current context does not silently become durable profile evidence.
- [ ] Focused profile/draft safety tests and generated target checks pass.

## Notes

- Finding: `5.2.5.1`; routing state: `untracked`.
- Preserve anti-impersonation, visibility, and audience-widening controls.

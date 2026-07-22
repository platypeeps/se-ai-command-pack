# Clarify the author and tutorial skill boundary

## Goal

Review snapshot 726d2d57c275b1d600940fbd523528081a43a898bfdaac2cdad34dec06fba0ae; finding 5.4.1.1. Route article-shaped tutorials centered on original thesis or experience to se-author and executable checkpoint-driven teaching to se-tutorial. Affected templates: templates/skills/se-author/SKILL.md and templates/skills/se-tutorial/SKILL.md; focused routing tests under tests/test_skills.py.

## Requirements

- Define `se-author` tutorial ownership as article-shaped work centered on an
  original thesis, argument, experience, or publication contribution.
- Define `se-tutorial` ownership as ordered technical teaching whose primary
  outcome is completing and verifying an observable result.
- Route ambiguous requests by the intended reader outcome rather than removing
  tutorial capability from either skill.
- Preserve the existing research, editing, publication, safety, checkpoint,
  cleanup, and execution-state contracts.
- Keep documentation and trigger examples consistent with the clarified
  boundary.
- Change only canonical templates under `templates/skills/**`, then regenerate
  supported targets through the normal sync path.

## Acceptance Criteria

- [ ] A thought-leadership tutorial based on the user's experience routes to
      `se-author`.
- [ ] A checkpoint-driven guide to configure or build an observable result
      routes to `se-tutorial`.
- [ ] An ambiguous tutorial request prompts for the outcome-changing detail
      instead of arbitrarily selecting a workflow.
- [ ] Neither skill loses its accepted tutorial use cases or safety boundaries.
- [ ] Focused routing tests and generated target checks pass.

## Notes

- Finding: `5.4.1.1`; routing state: `untracked`.

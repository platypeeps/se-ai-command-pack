---
title: Fix fresh-session encoding and document runtime profiles
status: done
created: 2026-07-25
branch: task/07-25-runtime-profile-gaps
---
# Fix fresh-session encoding and document runtime profiles

Parent: `.trellis/tasks/07-25-agent-artifacts` (Tier 3). Settled inputs: parent
`design.md` section 1 and `research/cross-platform-agent-support.md`.

## Goal

Close the two known gaps in the existing RuntimeProfile layer: the portable
`fresh-session` runtime context silently degrades at generation time, and the entire
RuntimeProfile/overlay system is undocumented in the operator guide.

## Requirements

- R1: Give `fresh-session` (used by se-red-team) an explicit encoding instead of silent
  omission. Evaluate during planning: in-body instruction in the generated overlay, a
  generated doc note, or a host frontmatter field. The chosen encoding must state the
  intent (independent run without inherited conclusions) wherever the profile applies.
- R2: Document the RuntimeProfile system in `docs/SE_AI_COMMAND_PACK.md`: add `generated/`
  to the layout table; add runtime-profile steps to the "Adding a skill" and "Adding a
  platform" checklists; explain the portable vocabulary (`inline | forked | fresh-session`)
  and the Claude-only overlay translation.
- R3: No behavior change for any skill other than se-red-team's isolation expression.

## Acceptance Criteria

- [x] Generated output for se-red-team expresses the fresh-session recommendation (no
      silent collapse to host default), with the mechanism documented.
- [x] docs/SE_AI_COMMAND_PACK.md covers layout (`generated/`), runtime profiles, and both
      maintainer checklists.
- [x] `make check` (generator `--check`, release payload gate) passes; version bump and
      dated changelog entry per repo rules.
- [x] Tests pinning overlay behavior updated where affected (tests/test_generate.py,
      tests/test_skill_review.py contextIsolation cases).

## Dependencies / order

- None. Recommended FIRST in the tree: small, standalone, and later children build on a
  correctly documented profile layer.

## Notes

- Lightweight task: PRD-only may be sufficient; decide at review.

## Cross-program coordination (2026-07-25 review)

- This task OWNS the operator-guide documentation of `generated/` and the RuntimeProfile
  overlay system (R2). The audit task `07-25-audit-maintainer-docs-accuracy` (ledger
  A-023/A-024) was narrowed on 2026-07-25 to avoid overlap: it keeps `make setup`, the
  manifest-schema `source` row, and CONTRIBUTING payload-definition fixes. Its evidence
  list (README.md:430, docs/SE_AI_COMMAND_PACK.md layout table) is useful input for R2.

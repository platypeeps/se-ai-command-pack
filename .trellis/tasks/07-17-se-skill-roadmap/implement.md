# Expand SE skill families and workflows Implementation Plan

## Execution Order

1. Finish planning artifacts for every linked child and park only those with a
   genuinely blocking product decision.
2. Implement, review, and archive `skill-family-taxonomy` first.
3. Rebase on current `main`; implement the P1 skills in this order:
   `se-decide`, `se-status`, `se-fact-check`.
4. Rebase before each follow-on child and implement `se-plan`, `se-handoff`,
   `se-monitor`, then `se-retro`, subject to each task's readiness.
5. Complete the `personal-worklog-profile` design decision; create separately
   approved implementation tasks only if its recommendation calls for them.
6. After all deliverable children are complete, construct the cross-skill
   trigger matrix and resolve contradictions in the owning child or a narrowly
   scoped follow-up.
7. Run the final integration validation and archive this parent only after the
   child list and public catalog agree.

## Validation Plan

- `python3 ./.trellis/scripts/task.py list`
- `make generate`
- `make check`
- `git diff --check`
- Installer dry-run against a newly created temporary root with all supported
  platform anchors, never the developer's real home directory.
- Manual review of flat installed targets and shared-reference fan-out.

## Documentation And Spec Updates

- Keep family/catalog documentation owned by the taxonomy child.
- Keep each skill's README entry and changelog wording owned by that skill's
  child task.
- Update backend specs only for conventions that survived more than one child
  implementation and are now demonstrably reusable.
- The parent may record the final trigger matrix in its task artifacts unless a
  concise public catalog version materially helps users.

## Review Notes

- Prefer small child PRs; generated manifest, version, and changelog conflicts
  must be regenerated from current canonical state.
- Do not mark the parent implemented merely because planning artifacts exist.
- No child should weaken source attribution, prompt-injection resistance,
  read-only defaults, or unknown-argument handling.
- Review the public/private boundary again before any worklog payload change.

## Follow-Ups

- Consider family-based install filtering only after catalog size creates a
  demonstrated usability problem.
- Consider command adapters only after skill-only invocation proves
  insufficient on a supported platform.
- Use observed trigger confusion to decide whether future skills should be
  combined, renamed, or retired.

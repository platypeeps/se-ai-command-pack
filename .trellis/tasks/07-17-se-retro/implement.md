# Implement se-retro Implementation Plan

## Execution Order

1. Re-read the task, source standards, current skill conventions, and the local
   `.agents/skills/sd-retro/SKILL.md` specialization boundary.
2. Add focused failing tests for evidence ordering, uncertainty, non-blaming
   language, conditional specialized routing, and read-only behavior.
3. Create `templates/skills/se-retro/SKILL.md` with canonical frontmatter,
   arguments, workflow, safety rules, and final report.
4. Register the skill under Improve/current registry, fan in source standards,
   and update external-input safety pins.
5. Update catalog and operator documentation.
6. Run `make generate` and inspect every platform/reference target.
7. Choose the next release version from current `main`, update manifest header
   and dated changelog, regenerate, and run validation.

## Validation Plan

- `python3 -m unittest tests.test_skills tests.test_generate`
- `make generate`
- `make check`
- `git diff --check`
- Manual examples: successful project, failed meeting, conflicting participant
  accounts, thin evidence, and a coding/CI incident with `sd-retro` available.

## Documentation And Spec Updates

- Add `se-retro` under Improve in the generated README catalog.
- Explain the conditional specialized-workflow boundary where useful, without
  making the sibling pack a dependency.
- Update backend specs only if evidence/perspective separation becomes a shared
  skill convention.
- Record the new skill in the dated changelog release entry.

## Review Notes

- Challenge causal language and any inference about individual motives.
- Verify follow-ups are proposals unless owners/dates were explicitly accepted.
- Ensure the shipped skill remains useful when `sd-retro` is absent.
- Keep journal recording and Trellis task creation out of this general skill.

## Follow-Ups

- Consider facilitator templates only after the core evidence-led retro is used
  in real sessions.
- Keep automated action-item filing in a separate consent-gated integration.

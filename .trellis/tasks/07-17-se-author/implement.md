# Implement se-author Implementation Plan

## Execution Order

1. Re-read the PRD/design, taxonomy state, current skill conventions,
   `source-standards.md`, `se-research`, and planned contracts for topic radar,
   technical editor, publish, distill, fact-check, and paper.
2. Decide during implementation whether the workspace schema fits concisely in
   `SKILL.md`; add one direct reference file only when progressive disclosure
   materially reduces the canonical prompt.
3. Add focused failing tests for theme/no-theme routing, one-question interview,
   brief approval, user/assistant separation, ordered drafting passes, resume,
   thesis-drift approval, no fabricated experience, injection safety, and no publication.
4. Create `templates/skills/se-author/SKILL.md` with the repository's required
   sections, strict argument validation, stage routing, and final package shape.
5. Add the optional workspace reference and tests for its presence/content only
   if Step 2 justified it; avoid auxiliary documentation.
6. Register the skill under Create/current flat registry, add source-standard
   fan-out, and include it in external-input safety pins.
7. Update the grouped catalog/operator guide with boundaries from research,
   digest, paper, editor, and publish workflows.
8. Run `make generate`; inspect every platform skill/reference target.
9. Select the next version from then-current `main`, update manifest/changelog,
   regenerate, and complete validation.

The first implementation slice should pin the interview and brief checkpoint
and produce an approved skeleton from a supplied theme. Add discovery and resume
paths after the core authorship boundary is proven.

## Validation Plan

- `python3 -m unittest tests.test_skills tests.test_generate`
- `make generate`
- `make check`
- `git diff --check`
- Manual forward tests: supplied theme, no theme/no sources, vague thesis,
  firsthand case study, fast draft, resume after brief, resume after draft,
  conflicting artifacts, and publication request.

## Documentation And Spec Updates

- Add `se-author` under Create in the grouped catalog while preserving flat install paths.
- Document the optional supporting-skill handoffs without making unshipped skills
  hard dependencies when implementation order differs.
- Explain that workspace artifacts may be files or equivalent host-managed state;
  do not prescribe Obsidian, Notion, or a specific filesystem.
- Update backend specs only if implementation establishes a reusable pack-wide
  checkpoint/reference convention.
- Record the new skill and release version in `CHANGELOG.md`.

## Review Notes

- Verify the user remains the source of personal experience, judgments, and
  original contribution; generated prose cannot manufacture authorship.
- Confirm exactly one interview question is asked at a time and each question
  resolves the highest-value gap.
- Challenge every checkpoint transition for explicit approval or a clearly
  requested shortcut with disclosed missing inputs.
- Ensure research evidence supports rather than silently replaces the thesis.
- Confirm resume never overwrites conflicting artifacts or claims a nonexistent approval.
- Verify no publishing or destination write occurs inside the skill.

## Follow-Ups

- Extract topic discovery into `se-topic-radar` only after its independent task lands.
- Use real authoring sessions to refine interview stopping criteria before adding
  more format variants.
- Keep research-paper methodology in `se-paper` and connector writes in `se-publish`.

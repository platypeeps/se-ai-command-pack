# Implement se-fact-check Implementation Plan

## Execution Order

1. Re-read this task plus the current `se-research`, `se-digest`, source
   standards, verification protocol, registry, and generator fan-out logic.
2. Add focused failing tests for verdict vocabulary, claim-led behavior, safety
   boundaries, and the stable research protocol target.
3. Move the verification protocol into `_shared/references/` without changing
   its basename, claim ladder, passes, or failure behavior; generalize only its
   research-brief-specific introductory wording for shared ownership.
4. Create `templates/skills/se-fact-check/SKILL.md` with the canonical section
   order and framework-neutral language.
5. Register the skill under the landed Understand family and configure both
   shared references for the correct consumers while preserving derived
   `SKILL_NAMES` compatibility.
6. Update pack identity and operator documentation for the new skill and shared
   protocol.
7. Run `make generate` and verify each supported platform receives the skill,
   source standards, and verification protocol.
8. Publish version `0.5.0`, update the manifest header and dated changelog,
   regenerate, and run the validation plan.

## Validation Plan

- `.venv/bin/python -m unittest discover -s tests -p 'test_skills.py'`
- `.venv/bin/python -m unittest discover -s tests -p 'test_generate.py'`
- `make generate`
- `make check`
- Inspect the manifest diff and confirm
  `<skills-dir>/se-research/references/verification-protocol.md` is retained.
- Run `git diff --check` before review.

## Documentation And Spec Updates

- Add `se-fact-check` under Understand in `README.md`.
- Update the operator guide to identify both shared references and their
  consumers.
- Update backend specs only if moving a skill-owned reference to shared content
  establishes a new reusable migration convention.
- Record the payload and protocol-source change in `CHANGELOG.md`.

## Review Notes

- Treat installed target stability as a compatibility requirement even though
  the repository source path moves.
- Review verdict semantics for mutual exclusivity and make uncertainty visible.
- Ensure the skill audits claims rather than becoming a generic research or
  editing prompt.
- Do not duplicate the verification protocol inside the new skill directory.

## Follow-Ups

- Consider artifact-level correction or tracked-change support only after the
  read-only audit workflow proves useful.
- Do not add automated publication or enforcement behavior in this task.

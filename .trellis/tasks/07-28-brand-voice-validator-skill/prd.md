# Create brand voice validator skill

## Goal

Add a new skill to the pack that validates written content (docs, announcements, PR
descriptions, UI copy, marketing text) against a defined brand voice: tone,
terminology (preferred/banned terms), style rules, and audience fit. The skill
reports violations with locations and suggested rewrites; it does not silently
rewrite content.

## Requirements

- New source skill under `templates/skills/` (working name `se-brand-voice`;
  final name decided in design — must carry the `se-` prefix and read naturally
  beside the existing 53 skills).
- SKILL.md follows pack conventions: generator-valid frontmatter, usage
  examples, key=value argument table consistent with the catalog.
- Core behavior:
  - Input: content by path or pasted text.
  - Voice definition: resolved from a repo-local guidelines file when present;
    an explicit argument can point at an alternative. When no guidelines exist,
    the skill must say so and offer a bootstrap mode that drafts starter
    guidelines from sample content the user supplies — never validate against
    an invented, unstated voice.
  - Output: findings grouped by rule (tone, terminology, style), each with
    location, the offending text, and a suggested rewrite; a short verdict
    summary. Validation is read-only by default.
- Argument names must reuse the pack's existing axis vocabulary rather than
  minting new spellings; align with the outcome of
  `07-25-audit-skill-arg-vocabulary` (ledger A-006) if that lands first.
- Registration: regenerate surfaces (`make generate`) so `generated/`, all
  platform copies, and `manifest.json` include the skill. If the skill cites
  any `_shared/references/` file, remember the manual `SHARED_REFERENCES`
  consumer append in `installer/registry.py` (ledger A-007 — no gate catches a
  miss today).
- `validate_skills` and `tests/test_skills.py` pass with the new skill in
  place.

## Acceptance Criteria

- [ ] `templates/skills/<name>/SKILL.md` exists and passes generator
      validation.
- [ ] Generated and platform copies plus `manifest.json` regenerated and
      committed together with the source.
- [ ] Skill documents the no-guidelines bootstrap behavior explicitly.
- [ ] Argument table introduces no new name for an axis the pack already
      spells another way.
- [ ] `tests/test_skills.py` passes; skill appears in the skill catalog.

## Out of scope

- Auto-rewriting or bulk-fixing content (suggest-only).
- CI enforcement of brand voice on repo content.
- Shipping an opinionated default brand voice for consumers.

## Notes

- Coordination: argument vocabulary work (`07-25-audit-skill-arg-vocabulary`,
  A-006) and shared-reference closure (`07-25-audit-shared-reference-closure`,
  A-007) both touch the seams this skill lands on; check their status before
  implementation to avoid re-diverging.

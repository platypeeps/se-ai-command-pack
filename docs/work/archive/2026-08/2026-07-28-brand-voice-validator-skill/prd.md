---
title: Create brand voice validator skill
status: done
created: 2026-07-28
branch: task/07-28-brand-voice-validator-skill
---
# Create brand voice validator skill

## Goal

Add a new skill to the pack that validates written content (docs, announcements, PR
descriptions, UI copy, marketing text) against a defined brand voice: tone,
terminology (preferred/banned terms), style rules, and audience fit. The skill
reports violations with locations and suggested rewrites; it does not silently
rewrite content.

## Requirements

- New source skill under `templates/skills/`, named `se-brand-voice` (resolved
  in `design.md` D1) — carries the `se-` prefix and reads naturally beside the
  53 skills already registered in `installer/registry.py`.
- SKILL.md follows pack conventions: generator-valid frontmatter, usage
  examples, key=value argument table consistent with the catalog.
- Core behavior:
  - Input: content by path or pasted text.
  - Voice definition: resolved from a repo-local guidelines file when present;
    an explicit argument can point at an alternative. When no guidelines exist,
    the skill must say so and offer a bootstrap mode that drafts starter
    guidelines from sample content the user supplies — never validate against
    an invented, unstated voice. The candidate paths and their precedence are
    fixed in `design.md` D8; `auto` never searches broadly.
  - Output: findings grouped by rule (tone, terminology, style, audience fit),
    each with location, the offending text, and a suggested rewrite; a short
    verdict summary. Every mode is read-only; the skill writes no file.
- Argument names must reuse the pack's existing axis vocabulary rather than
  minting new spellings. A-006 has landed: `installer/registry.py` enforces
  `CANONICAL_ARGUMENT_LADDERS` and `KNOWN_COVERED_AXIS_ALIASES` through
  `argument_vocabulary_errors()`, so this is a gate, not a coordination hope.
- Registration: regenerate surfaces (`make generate`) so the generated Claude
  overlay, the bundled catalogs, and `manifest.json` install rows for every
  registered platform include the skill (only Claude gets a tracked generated
  overlay; other platforms install directly from the canonical template). A cited
  `_shared/references/` file still needs its `SHARED_REFERENCES` consumer
  append in `installer/registry.py`; A-007 has landed, so the generator's
  reverse citation closure now fails on a miss instead of shipping a broken
  citation.
- `validate_skills` and `tests/test_skills.py` pass with the new skill in
  place.

## Acceptance Criteria

- [x] `templates/skills/<name>/SKILL.md` exists and passes generator
      validation.
- [x] Generated Claude overlay, bundled catalogs, and `manifest.json` rows for
      every registered platform regenerated and committed with the source.
- [x] Skill documents the no-guidelines bootstrap behavior explicitly, and
      bootstrap returns a draft in the report without writing any file.
- [x] Argument table introduces no new name for an axis the pack already
      spells another way.
- [x] `tests/test_skills.py` passes; skill appears in the skill catalog.

## Out of scope

- Auto-rewriting or bulk-fixing content (suggest-only).
- CI enforcement of brand voice on repo content.
- Shipping an opinionated default brand voice for consumers.

## Convergence (2026-08-05)

- Name resolved: `se-brand-voice`; family `improve`. Rationale in `design.md` D1/D2.
- Coordination checks are resolved, not pending:
  - A-006 (argument vocabulary) **landed**. `installer/registry.py` now enforces
    `CANONICAL_ARGUMENT_LADDERS` and `KNOWN_COVERED_AXIS_ALIASES` through
    `argument_vocabulary_errors()`, called from the generator's `validate_skill`.
    The argument table is authored against that vocabulary.
  - A-007 (shared-reference closure) **landed**. `validate_skills()` performs
    reverse citation closure, so a cited-but-unshipped `references/<file>.md`
    now fails generation. The requirement below to remember the manual
    `SHARED_REFERENCES` append still holds as an authoring step, but it is now
    gate-enforced rather than unguarded.
- Release shape: new shipped skill changes `templates/**`, `generated/**`, and
  `installer/**`, so the release gate requires a version bump and dated
  changelog heading. Target `0.67.0` (pack history uses a minor bump per new
  skill).

## Notes

- Coordination is closed, not pending: argument vocabulary
  (`07-25-audit-skill-arg-vocabulary`, A-006) and shared-reference closure
  (`07-25-audit-shared-reference-closure`, A-007) both landed and are now
  enforced gates. Authoring follows those gates; no status check remains.

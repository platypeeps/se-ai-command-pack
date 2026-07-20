# Introduce skill family taxonomy and grouped catalog

## Goal

Add outcome-oriented skill family metadata, generate grouped catalog documentation, preserve flat source and installed paths, and document the separation between shipped skills, installer lifecycle commands, repo development tooling, and future command adapters.

## Background

The registry currently stores only an ordered tuple of skill names, while the
README maintains one flat skill table manually. The generator treats every
direct child of `templates/skills/` as a skill, so filesystem nesting is not an
appropriate categorization mechanism.

## Requirements

- Define stable outcome-oriented families: Understand, Decide, Create,
  Coordinate, Operate, and Improve.
- Make family membership a single source of truth in the registry while
  preserving a derived `SKILL_NAMES` interface where compatibility requires it.
- Group the public skill catalog by family without duplicating canonical skill
  descriptions in multiple hand-maintained sources.
- Keep `templates/skills/se-*/` and every installed platform skill directory
  flat.
- Document the distinct roles of shipped skills, `install.py` lifecycle
  commands, repo-local SD/Trellis helpers, and possible future thin command
  adapters.
- Add validation for unknown families, duplicate skills, stable ordering, and
  existing prefix/path rules.
- Cover the registry and generated documentation behavior with focused tests.

## Acceptance Criteria

- [ ] Every registered skill belongs to exactly one allowed family.
- [ ] Create and Operate are valid families even before their first shipped
      skills land; Learn remains a documented subtheme within Understand rather
      than a separate top-level family.
- [ ] Existing manifest target paths and current skill IDs are unchanged.
- [ ] README skill listings are grouped by family and remain synchronized with
      registry/frontmatter data through generation or an equivalent drift gate.
- [ ] The generator rejects invalid family metadata with actionable errors.
- [ ] Documentation does not imply that per-platform command adapters are
      currently shipped.
- [ ] `make generate` and `make check` pass with the new taxonomy.

## Out of Scope

- Moving canonical or installed skills into family subdirectories.
- Adding `--family` installation filtering.
- Implementing command or prompt adapters.

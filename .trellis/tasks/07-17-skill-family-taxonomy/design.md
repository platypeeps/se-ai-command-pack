# Introduce skill family taxonomy and grouped catalog Design

## Overview

Add a lightweight family model to the canonical skill registry and use it to
generate a grouped README catalog. Keep skill source directories, installed
targets, manifest rows, and user-facing skill IDs flat and unchanged.

The taxonomy is catalog metadata, not installation metadata. The installer does
not need a family field in every per-platform file row, so this change should
not alter the manifest schema or add family filtering.

## Proposal

In `installer/registry.py`, introduce a frozen `SkillInfo` dataclass with
`name` and `family`. Define an ordered family-label mapping:

- `understand` → Understand
- `decide` → Decide
- `coordinate` → Coordinate
- `improve` → Improve

Replace the hand-authored tuple with an ordered `SKILLS: tuple[SkillInfo, ...]`
and derive `SKILL_NAMES = tuple(skill.name for skill in SKILLS)` for generator,
installer, and test compatibility. Preserve the current skill order so existing
manifest row ordering does not churn:

- Understand: `se-research`, `se-scan`, `se-digest`
- Coordinate: `se-brief`, `se-meeting-prep`
- Decide and Improve remain valid empty families until their child skills land.

Extend `validate_registry()` to reject unknown families, duplicate names, empty
family/name values, missing `se-` prefixes, and any name-to-family ambiguity.
Do not copy descriptions into the registry; `SKILL.md` frontmatter remains the
canonical trigger text.

Add explicit managed markers around the README skill catalog. Extend
`.github/scripts/generate-skill-surfaces.py` to:

1. Parse each registered skill's validated frontmatter.
2. Render non-empty family sections in declared family order.
3. Render a `Skill | Use when` table using the canonical frontmatter
   description verbatim.
4. Replace only the content between unique catalog markers.
5. In `--check` mode, fail independently for manifest drift or catalog drift.

Keep `regenerated_manifest_text()` and `SKILL_NAMES` available to avoid an
unnecessary broad refactor. Add a separate `regenerated_readme_text()` boundary
and patch `README_PATH` in sandbox generator tests so test generation never
touches the real repository README.

Update documentation to name three separate surfaces:

- shipped `se-*` skills, grouped by outcome family;
- `install.py` lifecycle commands, grouped as pack management; and
- repo-local SD/Trellis helpers, used to develop the pack but not shipped by it.

Document future per-platform commands only as thin, flat adapters such as
`/se:research`; do not implement them or add nested category namespaces.

## Boundaries And Non-Goals

- Do not move `templates/skills/se-*` into family directories.
- Do not move sources such as `templates/skills/se-research/SKILL.md` or
  change the existing flat installed layout.
- Do not add family fields to generated manifest rows or bump the manifest
  schema.
- Do not add `--family` installer selection.
- Do not implement command/prompt adapters.
- Do not duplicate skill descriptions in the registry or another catalog file.

## Affected Files

- `installer/registry.py` — `SkillInfo`, ordered families, canonical `SKILLS`,
  derived `SKILL_NAMES`, and validation.
- `.github/scripts/generate-skill-surfaces.py` — frontmatter-backed catalog
  rendering and README drift/write handling.
- `README.md` — managed markers and family-grouped generated catalog.
- `docs/SE_AI_COMMAND_PACK.md` — updated registry/generator and surface guidance.
- `tests/test_skills.py` — family membership and catalog coverage pins.
- `tests/test_generate.py` — catalog rendering, drift, marker, ordering, and
  sandbox path isolation tests.
- `.trellis/spec/backend/directory-structure.md` and
  `.trellis/spec/backend/quality-guidelines.md` — update only after the new
  canonical metadata/generation contract is implemented.

`manifest.json`, canonical skill templates, installed receipts, and pack
version should remain byte-for-byte unchanged unless implementation discovers a
real payload change. Do not bump the release merely for registry/catalog tooling.

## Risks And Edge Cases

- Extending `main()` can make sandbox tests write the real README unless
  `README_PATH` is injectable and patched in every synthetic test.
- Missing or duplicate managed markers could corrupt surrounding documentation.
  Fail without writing when marker validation is not exact.
- Generating descriptions from frontmatter can expose Markdown table-breaking
  characters. Either reject newlines/pipes in descriptions or escape pipe
  characters deterministically.
- Empty families should not produce confusing empty README sections, but their
  identifiers must remain valid for future skills.
- Reordering `SKILLS` would reorder manifest rows and create noisy diffs. Keep
  the current registry order independent from display grouping.
- A partial write could update the manifest but not README. Compute and validate
  both outputs before writing either; keep writes small and deterministic.

## Validation

- Unit-test valid family membership, unknown families, duplicate names, and
  derived `SKILL_NAMES` compatibility.
- Unit-test grouped catalog order, empty-family omission, frontmatter source,
  pipe escaping/rejection, missing or duplicate markers, and `--check` drift.
- Assert synthetic generator runs write only patched temporary paths.
- Run `make generate` twice and confirm the second run is a no-op.
- Run `make check` and verify `manifest.json` and version remain unchanged when
  there is no payload change.

## SD Work Designs Proposal - 2026-07-17

### Expanded Family Model

The expanded roadmap supersedes the original four-family list. Use six stable,
outcome-oriented top-level families in this display order:

- `understand` → Understand
- `decide` → Decide
- `create` → Create
- `coordinate` → Coordinate
- `operate` → Operate
- `improve` → Improve

The distinction is based on the primary outcome of invoking a skill:

- **Understand** finds, verifies, synthesizes, explains, compares, or teaches
  knowledge. Learning remains a subtheme here until multiple implemented skills
  demonstrate a need for a separate top-level family.
- **Decide** selects direction or turns accepted direction into bounded choices
  and plans.
- **Create** develops original or adapted intellectual artifacts such as
  articles, papers, proposals, tutorials, presentations, diagrams, and publication drafts.
- **Coordinate** aligns people, meetings, commitments, status, communication,
  and handoffs.
- **Operate** supports repeatable execution, monitoring, capture into operating
  systems, runbooks, procedures, and checklists.
- **Improve** critiques, evaluates, stress-tests, learns from outcomes, and
  refines existing work.

The family remains singular canonical metadata: each skill belongs to exactly
one family even when it hands work to another family. Cross-family relationships
belong in skill documentation, not additional registry memberships.

### Assignment Guidance

The taxonomy task only registers skills that exist when it is implemented. Use
this planned map to keep later child tasks consistent without adding unshipped
names prematurely:

- **Understand**: `se-research`, `se-scan`, `se-digest`, `se-fact-check`,
  `se-distill`, `se-explain`, `se-literature-map`, `se-compare`, `se-learn`,
  `se-study-guide`, `se-socratic-review`, `se-video-notes`, `se-knowledge-gap`,
  `se-ask-me`.
- **Decide**: `se-decide`, `se-plan`, `se-premortem`.
- **Create**: `se-author`, `se-paper`, `se-topic-radar`, `se-proposal`,
  `se-tutorial`, `se-presentation`, `se-diagram`, `se-publish`.
- **Coordinate**: `se-brief`, `se-meeting-prep`, `se-status`, `se-handoff`,
  `se-action-inbox`, `se-thread-digest`, `se-agenda`, `se-stakeholder-map`,
  `se-feedback`, `se-meeting-follow-through`.
- **Operate**: `se-monitor`, `se-watchlist`, `se-capture`,
  `se-knowledge-capture`, `se-bookmark-triage`, `se-runbook`, `se-sop`,
  `se-checklist`, `se-profile`.
- **Improve**: `se-retro`, `se-postmortem`, `se-evaluate`, `se-red-team`,
  `se-technical-editor`, `se-weekly-review`.

When a later task reveals a stronger primary outcome, update this guidance and
that task together. Do not encode multi-family aliases to avoid making catalog
placement ambiguous.

### Changes To The Original Proposal

- Expand `FAMILY_LABELS` from four entries to six in the order above.
- Keep existing shipped assignments unchanged: `se-research`, `se-scan`, and
  `se-digest` remain Understand; `se-brief` and `se-meeting-prep` remain Coordinate.
- Treat Decide, Create, Operate, and Improve as valid empty families until their
  respective child tasks ship. Continue omitting empty family sections from the README.
- Add tests proving all six identifiers are accepted, unknown identifiers are
  rejected, and empty-family omission does not change declared family order.
- Update operator documentation to use “family” as the canonical term;
  “category” may appear only as a plain-language synonym.

All original compatibility boundaries remain: flat source/install paths,
unchanged skill IDs, no manifest family fields, no installer family filter, and
no nested command namespace.

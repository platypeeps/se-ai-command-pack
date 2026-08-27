# Author the 13 se-* skills inspired by claude-skills

Parent: [`../08-26-adopt-claude-skills/`](../08-26-adopt-claude-skills/) — R1; parent AC1, AC6.

## Goal

Write 13 new pack skills in `templates/skills/`, each inspired by an upstream
`Shearerbeard/claude-skills` skill but re-authored to this repository's
conventions, register them in `installer/registry.py`, and regenerate every
skill surface so they ship fleet-wide through the normal install pipeline.

## Roster

| se- skill | Upstream inspiration | Re-authoring notes |
| --- | --- | --- |
| `se-rust-design` | `rust-design` | Type-driven design: make illegal states unrepresentable, parse-don't-validate, typestate. |
| `se-rust-quality` | `rust-quality` | Idiomatic-Rust bar: error design, clippy posture, API guidelines. |
| `se-rust-modules` | `rust-modules` | Module/crate boundaries, visibility discipline. |
| `se-rust-async` | `rust-async` | Async discipline: cancellation safety, spawn hygiene, Send bounds. |
| `se-rust-review` | `rust-review` | Rust-specific review checklist. Positioned as a local lens; the sd-review lane stays the review authority. |
| `se-typed-holes` | `typed-holes` | Skeleton-first workflow with `todo!()` holes; companion to the agent trio. |
| `se-gate-probes` | `gate-probes` | Pre-merge probes (sprawl, duplication, god modules, reviewability, plan probes). Routing table rewritten to this pack's lanes: `trellis-check`, `sd-review`, sibling `se-*` skills. No route to any non-adopted upstream skill (parent AC6); no "review this diff" claim (parent C5). |
| `se-docs-bustest` | `docs-bustest` | Docs must survive the "bus test": a newcomer can execute them cold. |
| `se-rebase-hygiene` | `rebase-hygiene` | Fetch-first, merge-tree dry run, pre-planned resolutions, `--force-with-lease` verification. Keep `disable-model-invocation: true` semantics if the platform supports it; state the user-invoked-only intent in the body either way. Must not contradict the repo's no-unapproved-force-push policy: the skill plans and verifies, the user approves the push. |
| `se-skill-retro` | `skill-retro` + `process-feedback` | Audits skill triggering after a session: which skills should have fired, misfired, or were missing. Routes findings to owners: `se-*` skill defect fixed in `templates/skills/` (ships fleet-wide); sd/Trellis finding filed against the owning repo. Replaces upstream's marketplace `feedback/` destination. |
| `se-prose-lint` | `prose-lint` | Drives the Vale gate from the vale child; degrades gracefully (states the gap, does not fail the session) where Vale is absent (parent C5). |
| `se-humanizer` | `humanizer` | De-AI-ifying prose passes. Upstream is MIT with an explicit license header — attribute inspiration in the inspiration map, ship re-authored text. Same graceful degradation as `se-prose-lint` for any Vale-backed checks. |
| `se-adr-review` | `adr-review` | Review-process-specific (decision below). |

## `se-adr-review` scope (user decision 2026-08-26)

Very specific to the ADR **review** process; fleet repos will carry ADRs.

- Triggers: PRs or diffs touching `docs/adr/`, `DECISIONS.md`, or `*.adr.md`;
  ADR status transitions (proposed → accepted/rejected/superseded); an explicit
  "review this ADR" request.
- Checks: MADR-style section completeness, RFC-2119 force in decision drivers,
  honest consequences (positive and negative), forward links from superseded
  ADRs, status lifecycle validity, and the premise-freshness sweep — verify
  stated-absent facts are still absent, pinned refs still exist, dependency
  claims and quantitative claims still hold; a changed premise is a P1.
- Output: fixed P1/P2/P3 report format with one verdict line.
- Non-goals: authoring ADRs, templating new ADRs, general design review.

## Requirements

- R1. Each skill is a `templates/skills/<name>/SKILL.md` following the pack's
  canonical frontmatter and body conventions, written in this pack's voice —
  no upstream text copied verbatim.
- R2. Each skill gets a `SkillInfo` row in `installer/registry.py`. The family
  assignment is a design decision: either a new family (recommended:
  `engineer`, with `FAMILY_LABELS`/`FAMILY_DESCRIPTIONS` entries) or a mapping
  onto the existing six; decide once in `design.md` and apply uniformly.
- R3. Regenerate all derived surfaces with the toolchain interpreter
  (`bash "$SD_PACK_TOOLCHAIN" run-python -- .github/scripts/generate-skill-surfaces.py`;
  bare `python3` lacks `yaml`) and keep `--check` green.
- R4. Descriptions must be trigger-accurate: model-invoked skills describe when
  they apply; user-invoked-only skills (`se-rebase-hygiene`) say so.
- R5. No skill references a non-adopted upstream skill or an upstream-only
  tool. Routing stays inside this pack's shipped surfaces (parent AC6).
- R6. Cross-references between sibling skills (for example `se-gate-probes`
  routing to `se-docs-bustest`, `se-typed-holes` referencing the agent trio)
  use the final `se-` names.

## Constraints

- C1. Parent C5 conflict findings are binding (no sd-review turf claims, no
  click/pytest mandates, no per-commit approval demands, Vale degradation).
- C2. Registry and generator invariants hold: `se-` prefix, unique names,
  every skill in exactly one family.
- C3. `make check` green; no changes to vendored Trellis payload.

## Acceptance Criteria

- [ ] AC1. All 13 `templates/skills/<name>/SKILL.md` files exist with valid
      canonical frontmatter.
- [ ] AC2. `installer/registry.py` registers exactly these 13 new names; the
      family decision is recorded in `design.md` and implemented.
- [ ] AC3. Generator `--check` passes and regenerated surfaces (catalog,
      manifest, per-platform trees) are committed.
- [ ] AC4. Grep over `templates/` for the non-adopted upstream names
      (`git-commit`, `codex-cli`, `opencode-cli`,
      `collaborating-with-antigravity`, `mermaid`, `plan-discipline`,
      `process-feedback`, bare `adr-review`, bare `skill-retro`,
      unprefixed `rust-*`/`typed-holes`/`gate-probes`/`docs-bustest`/
      `rebase-hygiene`/`prose-lint`/`humanizer` as skill references) returns
      no dangling route. Inspiration-map mentions live in the
      inspiration-watch child, not in skill bodies.
- [ ] AC5. `make check` green.

This is a complex task: `design.md` (family decision, per-skill frontmatter
plan, shared conventions) and `implement.md` (ordered authoring + regeneration
steps with validation gates) are required before `task.py start`.

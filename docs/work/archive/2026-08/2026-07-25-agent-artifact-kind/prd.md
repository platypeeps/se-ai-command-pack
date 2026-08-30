---
title: Add agent artifact kind to installer and generator
status: done
created: 2026-07-25
---
# Add agent artifact kind to installer and generator

Parent: `.trellis/tasks/07-25-agent-artifacts` (Tier 2 plumbing). Settled inputs: parent
`design.md` section 1 and `research/cross-platform-agent-support.md` (binding).

## Goal

Make `agent` a first-class SE artifact kind: canonical neutral MD agent sources under
`templates/`, rendered per platform (Claude MD, Codex TOML), fanned through the manifest,
and installed/removed/verified by the existing installer — with the Amp/`agents` anchor
explicitly excluded.

## Requirements

- R1: `installer/manifest.py` `KNOWN_MANIFEST_KINDS` gains `agent`; `validate_manifest`
  accepts agent rows (`scope: user`, `install: if-anchor-exists`).
- R2: Generator (`.github/scripts/generate-skill-surfaces.py`) replaces the hardcoded
  `if platform == "claude" and relative == "SKILL.md"` branch with a per-platform
  overlay/renderer hook; agent renderers: Claude MD (near-passthrough into the generated
  tree) and Codex TOML (`name`, `description`, `developer_instructions`, optional `model`,
  `sandbox_mode`).
- R3: The `agents`/Amp anchor receives NO agent rows (Amp has no agent-file support);
  this exclusion is asserted by a test, not just convention.
- R4: Canonical agent sources live under `templates/` in a validated format (frontmatter
  allowlist analog, neutrality lint applies to bodies).
- R5: Drift gates extended: generator `--check`, release-payload version gate, provenance
  round-trip (`install`, `status`, `remove`, `update`) for agent rows.
- R6: A minimal sample/smoke agent may ship to prove plumbing, but wave-1 role content
  belongs to 07-25-worker-agents.

## Acceptance Criteria

- [ ] Installer round-trip works for agent rows on claude and codex anchors; `agents`
      anchor receives none (test-asserted).
- [ ] Renderer outputs validated (TOML escaping, MD dialect); `--check` detects drift.
- [ ] tests/test_generate.py, tests/test_install.py, tests/test_skills.py extended.
- [ ] Version bump + changelog; docs updated for the new kind (maintainer checklists).

## Dependencies / order

- Independent of Tier 1 tasks. BLOCKS 07-25-worker-agents.
- Open question to resolve in design: user-scope only (`~/.claude/agents`,
  `~/.codex/agents`) or also project-scope; verify Codex user-scope avoids the
  project-trust gate.

## Notes

- Complex task: needs `design.md` + `implement.md` before start.

## Cross-program coordination (2026-07-25 review)

- Registry contract consumer (A-002): shipped `skill_review.py` AST-parses
  `installer/registry.py` (SKILLS / PLATFORM_REGISTRY / SHARED_REFERENCES shapes) on
  consumer machines. `07-25-audit-registry-snapshot-contract` must land BEFORE (or within)
  this task's registry reshaping, and the snapshot schema version must bump with the new
  `agent` kind so installed copies detect incompatibility instead of misparsing.
- Generator refactor (A-003, A-007): absorb the `skill-catalog.md` special case
  (`07-25-audit-generated-catalog-location`) into the renderer-hook refactor instead of
  preserving the one-off exception; coordinate sequencing with the citation-closure gate
  (`07-25-audit-shared-reference-closure`), which edits the same validate path.
- Codex anchor (A-044): resolve `07-25-audit-codex-home-contract` in this task's design
  gate before shipping a second codex surface (agents dir doubles the drift otherwise).

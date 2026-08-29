# Implementation plan — se-coherence-audit

Ordered. Each step names its own check. Do not advance past a red check.

## 1. Author the skill body

- [ ] `templates/skills/se-coherence-audit/SKILL.md` — frontmatter per
      `design.md`, then `# SE Coherence Audit`, `## When to use` (with the
      boundary paragraph naming `se-knowledge-gap`, `se-fact-check`,
      `se-prose-lint`, `se-docs-bustest`, `se-red-team`), `## Arguments`,
      `## Workflow` (7 steps), `## Safety rules` (read-only; no scope widening;
      no low-confidence findings; partial coverage never reported as complete),
      `## Final report`. Match the section order and voice of
      `templates/skills/se-knowledge-gap/SKILL.md`.
- [ ] `references/detector-criteria.md` — four classes, each with qualifies /
      evidence required / near-miss.
- [ ] `references/ledger-format.md` — finding schema table, severity model,
      coverage block shape, worked example finding of each class.

Check: none is possible yet, and claiming one would be false — every skill
validator iterates `SKILL_NAMES`, so an unregistered directory is invisible to
it. The step-2 check is this step's first real gate; do not report step 1 as
verified on its own.

## 2. Register in the pack

- [ ] `installer/registry.py`: `SKILLS` row (`family="improve"`, appended),
      `DEEP_ANALYSIS` runtime profile membership, `argument-vocabulary.md`
      shared-reference consumer.
- [ ] `tests/test_generate.py`: add the skill to the `EXPECTED_SHARED_SOURCES`
      golden snapshot. Skipping this fails
      `test_registered_shared_sources_match_snapshot`, not the generator.

Check: `python3 -m pytest tests/test_generate.py tests/test_install.py -q` — pass.

## 3. Test the skill

- [ ] `tests/test_skills.py`: a test class for `se-coherence-audit` matching the
      shape used for its neighbors in that file — read an existing neighbor's
      class first and mirror it rather than inventing a new shape.

Check: `python3 -m pytest tests/test_skills.py tests/test_frontmatter_conformance.py -q`
— pass, and the new class actually runs (`-k coherence` selects it).

## 4. Bump version, then regenerate

- [ ] Hand-edit `manifest.json` `version` one minor **first** — the generator
      preserves the committed value and will not compute it.
- [ ] `make generate`, then commit `manifest.json`,
      `generated/skills/claude/se-coherence-audit/SKILL.md`,
      `generated/references/skill-catalog.md`,
      `generated/registry-snapshot.json`. Do not hand-edit the catalog; it is
      generated output.

Check: `make release-check` — expect pass. That runs
`generate-skill-surfaces.py --check`, the canonical staleness proof; a failure
names the file whose committed text differs from the regenerated text.

## 5. Boundary edit to se-knowledge-gap

- [ ] One paragraph in `templates/skills/se-knowledge-gap/SKILL.md` naming this
      skill as the owner of inward corpus-defect audits. Regenerate.

Check: `grep -rl "se-coherence-audit" templates/skills/se-knowledge-gap generated/skills/claude`
returns both the template and the regenerated `claude` overlay — only that
overlay is committed under `generated/skills/`.

## 6. Docs

- [ ] `README.md` skill list, `docs/SE_AI_COMMAND_PACK.md` entry,
      `CHANGELOG.md` dated heading — mirroring `47d1fb0`. The version itself was
      bumped in step 4.

Check: `python3 -m pytest tests/test_installer_docs.py tests/test_release_gate.py -q` — pass.

## 7. Dogfood the skill (acceptance A6)

- [x] Run the authored skill against this repo:
      `input=AGENTS.md,.claude/rules/` — produce a ledger. (Those
      paths are fine to name here; only the shipped `SKILL.md` is brand-linted.)
      Ledger: `research/dogfood-ledger-2026-08-28.md`. The corpus is narrower
      than A6 first named: the root agent-instruction file it also listed does
      not exist in this repository, so A6 was corrected rather than satisfied
      with a substitute.
- [x] Manually confirm every reported contradiction against both quoted
      passages. The run reported no `contradiction`; its one conflict is
      `missing-precedence`, and both of its passages were re-read.

Check: every finding has a `path:line` and a verbatim quote; zero fabricated
contradiction pairs. A fabricated pair sends the detector criteria back to
step 1 — this is the gate that catches the skill's primary failure mode.

## 8. Full gate

Check: `make check` — expect green, including `prose-lint`, `release-check`,
`lock-check`, `trellis-provenance`.

## Review gates

- After step 4: registry, test snapshot, and generated artifacts reviewed
  together; a stale `manifest.json` is the most likely silent defect.
- After step 7: the dogfood ledger is the substantive review artifact — the
  skill is judged on that output, not on its prose.

## Rollback points

- Steps 1–6 are one commit; revert it and the pack is unchanged.
- Step 7 failures roll back to step 1 (criteria edit + regenerate), never to a
  weakened acceptance check.

# Implement: author the 13 se-* skills

Toolchain note: generator and tests run through
`bash "$SD_PACK_TOOLCHAIN" run-python -- ...`; bare `python3` lacks `yaml`.

## Step 1 — registry groundwork

- Add `engineer` to `FAMILY_LABELS` and `FAMILY_DESCRIPTIONS` (same position
  in both dicts).
- Add 13 `SkillInfo(name=..., family="engineer")` rows to `SKILLS`.
- Add runtime profile assignments per design D2 (add `ENGINEERING_REVIEW`
  constant only if no existing constant carries both/inline/deep/xhigh).
- Validate: run the generator `--check`; the registry self-checks execute at
  import, so an unbalanced family dict or missing profile assignment raises
  immediately. Expected result at this point: registry imports clean and
  `--check` fails only on the 13 not-yet-authored template dirs — that is
  the signal for Step 2, not a defect.
- Rollback point: revert `installer/registry.py` alone.

## Step 2 — rust line (6 skills)

- Author `templates/skills/se-rust-{design,quality,modules,async,review}/SKILL.md`
  plus `se-typed-holes/SKILL.md` per design D3/D4.
- Cross-references: `se-typed-holes` names the agent trio as optional
  executors (files land in the sibling task; reference by final name);
  `se-rust-review` routes verdict authority to the sd-review lane.
- Gate: generator `--check` still fails only on the not-yet-authored names.

## Step 3 — gates line (3 skills)

- `se-gate-probes` (11 probes, block-on-FAIL table, routing per D3),
  `se-docs-bustest`, `se-rebase-hygiene` (user-only posture; body states the
  no-unapproved-push rule).

## Step 4 — feedback and prose line (3 skills)

- `se-skill-retro` (routing split per D4), `se-prose-lint`, `se-humanizer`
  (both with the Vale degradation clause; `se-prose-lint` names
  `make prose-lint` as the deterministic backend when present).

## Step 5 — `se-adr-review`

- Implement the PRD scope section verbatim as the Workflow: trigger list,
  MADR completeness, RFC-2119 drivers, honest consequences, status lifecycle,
  premise-freshness sweep (changed premise = P1), fixed report format.

## Step 6 — regenerate and verify

- `bash "$SD_PACK_TOOLCHAIN" run-python -- .github/scripts/generate-skill-surfaces.py`
  then `--check`; commit regenerated surfaces with the templates.
- Negative grep (parent AC4 / task AC4): non-adopted and unprefixed upstream
  names over `templates/` — expect zero skill-reference hits.
- `make check` green.
- Rollback point: each step's commit reverts independently; Step 6 is the
  integration gate.

## Validation commands

```bash
bash "$SD_PACK_TOOLCHAIN" run-python -- .github/scripts/generate-skill-surfaces.py --check
# Full AC4 name list: non-adopted skills AND unprefixed forms of adopted ones.
# The [^a-z-] guard keeps se-* forms (se-adr-review, se-rust-design) from matching.
# `make prose-lint` is the one legitimate bare hit (the Make target, not a
# skill reference) — filter it; everything surviving the pipe is a defect.
grep -rnE '(^|[^a-z-])(git-commit|codex-cli|opencode-cli|collaborating-with-antigravity|mermaid|plan-discipline|process-feedback|adr-review|skill-retro|typed-holes|gate-probes|docs-bustest|rebase-hygiene|prose-lint|humanizer|rust-(design|quality|modules|async|review))([^a-z-]|$)' templates/skills templates/agents | grep -v 'make prose-lint'
make check
```

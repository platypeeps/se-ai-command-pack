# Implement — Sub-agent dispatch pilot

Ordered execution. Load `trellis-before-dev` before editing. Branch off `main`.

## Steps

1. **Read the model + doctrine** (no edits): `sd-audit-repo` `## Dispatch
   protocol` (`.claude/skills/sd-audit-repo/SKILL.md:156-172`) and
   `runtime-routing.md` "Subagent decomposition"
   (`templates/skills/se-review-skills/references/runtime-routing.md:67-86`).

2. **se-research canonical body** — `templates/skills/se-research/SKILL.md`:
   insert `## Sub-agent dispatch` between `## Workflow` (ends ~line 69) and
   `## Safety rules`. Units parallelize **within** each phase, never across:
   per search lane (step 3), then per claim verification (step 4), then per
   disconfirmation query (step 5) — steps 3->4->5 stay ordered. Include strategy
   line, orchestrator-ownership, worker input contract (inputs, exclusions,
   authority, **expected artifact**, **stop condition**), the **no-recursion
   guard** (when already running as a forked sub-agent, run units inline — no
   further spawn), the conditional `Active task:` prefix (only when a Trellis task
   is active), inline fallback — all host-neutral.

3. **se-fact-check canonical body** — `templates/skills/se-fact-check/SKILL.md`:
   insert `## Sub-agent dispatch` between `## Workflow` (ends ~line 81) and
   `## Safety rules`. Unit: per atomic claim (steps 5-6). Same sub-structure
   (expected artifact = the claim's verdict record; no-recursion guard; conditional
   `Active task:` prefix; inline fallback).

4. **Version + changelog:** `manifest.json` `0.66.9 -> 0.66.10`; prepend
   `## 0.66.10 - 2026-08-05` to `CHANGELOG.md` describing the pilot.

5. **Regenerate:** `make generate`. Expect changes only in
   `generated/skills/claude/se-research/SKILL.md`,
   `generated/skills/claude/se-fact-check/SKILL.md`, and
   `templates/skills/_shared/references/skill-catalog.md` (version line).
   `manifest.json` changes only in its hand-edited `version` field — no files are
   added/removed, so the generator's `files` array stays byte-identical. Any
   unexpected `files`-array churn is a defect to investigate, not to commit.

## Validation

- `make check` (test + lint + release-check). Must be exit 0:
  - `generate-skill-surfaces.py --check` drift gate clean (overlays byte-stable).
  - `tests/test_skills.py` REQUIRED_SECTIONS ordering + neutrality pass for both
    changed bodies.
  - `check-release-payload.py`: version `0.66.9 -> 0.66.10`, changelog heading
    matches.
- Targeted grep gate: `BANNED_PHRASE_PATTERN` returns zero hits in the two
  changed canonical bodies and their overlays.
- R4 guard: the dispatch prose references only host BUILT-IN sub-agents; grep the
  two changed bodies to confirm they name no SE worker agent or the
  `07-25-worker-agents` deliverable (that enhancement lands separately).
- Semantic-content assertions (AC1/AC3 — section validation alone is
  insufficient, it only checks required-heading order):
  - grep each changed body for exactly one `## Sub-agent dispatch` heading and an
    inline-fallback sentence ("on inline platforms ... sequentially");
  - grep each for the no-recursion guard phrase;
  - prove the `## Final report` section text is unchanged: `git diff` the two
    bodies and confirm the diff hunks touch only the inserted dispatch block —
    zero hunks inside `## Final report` (or `git show HEAD:<path>` vs working copy
    limited to the report section).
- Review preflight: `node scripts/sd-ai-command-pack-review-preflight.mjs`
  (0 failures before publish).

## Review gates

- Two-lane planning adversarial review at convergence (this file + design.md).
- `sd-ship until=merge` review stage (deterministic + local providers) before
  merge.

## Rollback

- Single `git revert` of the feature commit removes all prose + version changes;
  no data/contract migration. Safe at any point pre-merge by dropping the branch.

## Acceptance mapping (from prd.md)

- AC1 (dispatch section + inline fallback; lint + section validation pass) ->
  steps 2-3 + `make check`.
- AC2 (generator `--check` clean; overlays byte-stable otherwise) -> step 5 +
  release-check.
- AC3 (final-report contracts unchanged) -> steps 2-3 insert only between
  Workflow and Safety; final-report untouched.
- AC4 (version bump + dated changelog) -> step 4.

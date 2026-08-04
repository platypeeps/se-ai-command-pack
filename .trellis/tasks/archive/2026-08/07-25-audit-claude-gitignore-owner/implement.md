# Implement — Fix .claude dogfood tracking conflict (A-001)

Option A (track sd-adapters, parity). Small, reversible edits to `.gitignore` +
`CONTRIBUTING.md`, then stage the newly-trackable adapters.

## Checklist

1. **Edit `.gitignore` top block** — replace the wholesale `.claude/` (line 27,
   with its two-line comment) with the descend-and-allowlist block from
   `design.md`. Keep the managed block (`:55-197`) untouched.

2. **Verify ignore behavior BEFORE staging** (falsifiable checks):
   - `git check-ignore -v .claude/commands/sd/start.md` → **no match** (exit 1).
   - `git check-ignore -v .claude/skills/sd-help/SKILL.md` → **no match**.
   - `git check-ignore -v .claude/skills/caveman/SKILL.md` (or any local skill)
     → **still matched** (`.claude/*`). Confirms no over-capture.
   - `git check-ignore -v .claude/settings.local.json` → still matched.
   - `git check-ignore -v .claude/commands/trellis/<file>` → still matched
     (out of scope, unchanged).

3. **Diff the trackable set** — `git add -A .claude/ && git status --porcelain
   .claude/ | wc -l`. Expect the receipt-claimed set (~59). Then
   `git status --porcelain .claude/` and eyeball: every staged path is an sd-*
   adapter; no caveman/claude-mem/buildpartner/local path staged. If any local
   path appears, unstage and tighten the block.

4. **Cross-check against the receipt** — the staged `.claude/*` set must be a
   superset of (or equal to) the 59 rows in
   `.sd-ai-command-pack/installed-targets.txt`. Any claimed row NOT staged is a
   gap; investigate before proceeding.

5. **Document ownership** — add a "`.claude/` tracking policy" subsection to
   `CONTRIBUTING.md` per design.md (decision, parity rationale, do-not-re-add
   wholesale `.claude/`, upstream follow-up pointer).

6. **Run install-audit (AC2)** —
   `python3 scripts/sd-ai-command-pack-install-audit.py` (or the repo's
   documented invocation). Expect: no missing-target failures/warnings for
   `.claude/*` rows. Capture the decisive output line.

7. **Repo gate** — `make check` (or the narrower relevant target if `make check`
   is heavy). Must stay green. Capture result.

8. **AC3 honesty** — confirm this repo's `install.py` does not rewrite
   `.gitignore` (already verified in the mechanism map); note the `trellis init`
   limitation + follow-up in the PR body. Do not claim full oscillation-proofing.

9. **File the upstream follow-up task** (closes the PRD follow-up requirement) —
   create a Trellis task for the external `trellis init` change (emit narrow
   `.claude/**` rules like `.gemini`, no wholesale `.claude/`). Done in the
   work-loop follow-up phase; recorded here so it is not dropped.

## Validation commands (named checks)

- `git check-ignore` samples (step 2) — the primary AC1 gate.
- `python3 scripts/sd-ai-command-pack-install-audit.py` — AC2 gate.
- `make check` — repo regression gate.

## Rollback

Single-commit revert restores line 27 and un-stages the adapters; no data loss
(files remain on disk either way).

## Follow-up (separable, out of this task's scope)

Upstream `trellis init`: make it emit narrow `.claude/**` local-state rules (like
`.gemini`) instead of wholesale `.claude/`, so the fix is durable across
`trellis init --claude` refreshes. Record as a Trellis task.

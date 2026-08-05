# Fix fresh-session encoding and document runtime profiles — Implementation Plan

## Execution Order

1. **Renderer change** (`.github/scripts/generate-skill-surfaces.py`,
   `render_claude_skill`): after building `f"---\n{dumped}---\n{body}"`, when
   `profile.context == "fresh-session"`, append the generated fresh-session note
   block (marker comment `<!-- generated: runtime-profile fresh-session -->`
   followed by the blockquote from design.md). Update the function docstring to
   record the single deliberate body exception for fresh-session.
2. **Release metadata FIRST** (ordering matters): version bump + dated
   `CHANGELOG.md` entry per repo rules. This must precede the final regeneration
   because the generated help/skill catalog embeds the manifest version
   (`rendered_help_catalog(metadata, version)`, :1055) and `--check` rejects a
   stale catalog (:1244).
3. **Regenerate overlays + catalog (final)**: run `make generate` (=
   `.github/scripts/generate-skill-surfaces.py`, no `--check`, which writes
   `generated/skills/claude/**` + manifest/README/skill-catalog). Because the
   version bump already landed, the regenerated catalog carries the new version.
   Confirm the only overlay change is
   `generated/skills/claude/se-red-team/SKILL.md`; commit overlay + catalog
   together.
4. **Generator tests** (`tests/test_generate.py`): in the se-red-team case
   (~line 323-330) keep `assertNotIn("context", red_team_metadata)`; add an
   assertion that the generated red-team body contains the note marker; add a
   guard that the set of overlays whose body contains the marker equals exactly
   `{se-red-team}` (not merely "one other overlay lacks it").
5. **contextIsolation test** (`tests/test_skill_review.py`): add a fresh-session
   fixture asserting se-red-team's `contextIsolation` stays
   `inline-or-host-default` — the body note is advisory and must NOT be
   misreported as host-enforced fork/fresh isolation (analyzer keys off
   frontmatter `context == "fork"` only, skill_review.py:1363). This closes the
   PRD's named contextIsolation acceptance item and is R3 evidence.
6. **Docs** (`docs/SE_AI_COMMAND_PACK.md`): add `generated/` layout row;
   add runtime-profile section (portable `inline | forked | fresh-session`
   vocabulary + Claude overlay translation table incl. the in-body note);
   add runtime-profile steps to "Adding a skill" and "Adding a platform"
   checklists. (Docs carry no version string; safe after the bump.)

## Validation Plan

- Focused: `make test` (repo uses `unittest` via the Makefile, NOT pytest —
  pytest is absent from requirements-dev.txt), or targeted
  `<RUN_PYTHON> -m unittest tests.test_generate tests.test_skill_review`.
- Broad gate: `make check` (= `test lint release-check`; `release-check` runs the
  generator `--check` drift gate + `check-release-payload.py`). Green before ship.
- Manual diff check: `git diff --stat generated/skills/claude/` shows exactly
  one changed overlay (se-red-team); `git diff --stat` also shows the regenerated
  catalog carrying the bumped version.

## Documentation And Spec Updates

- `docs/SE_AI_COMMAND_PACK.md` per step 5 (this task OWNS the RuntimeProfile +
  `generated/` documentation per the parent's cross-program coordination note).
- `CHANGELOG.md` dated entry; version bump.

## Review Notes

- Reviewer-sensitive: the honesty argument for NOT using `context: fork`.
  Per runtime-routing.md:26 `forked` = host-managed isolated subagent that
  returns to the caller; `fresh-session` = independent run without inherited
  conclusions; they are "not interchangeable." `fork` advertises a bounded
  returning subagent, not an independent session — wrong encoding. Call this
  out in the PR body (do not overclaim that fork "inherits conclusions").
- Confirm the generated-body invariant docstring change is present so the
  "body unchanged" contract is not silently violated.
- Confirm the marker-bearing overlay set equals `{se-red-team}` (drift gate +
  explicit test), and that version bump preceded the final `make generate`.

## Rollback Points

- Renderer change is isolated to one branch in `render_claude_skill`; reverting
  the commit + regenerating restores prior output and the original test.
- Docs and changelog are additive; independently revertible.

## Follow-Ups (outside this PR)

- Fresh-session encoding for non-Claude hosts (Codex TOML etc.) if/when a host
  gains a matching primitive — currently none; documented as unsupported here.
- If Claude later ships a native independent-session frontmatter field, migrate
  the in-body note to that field (tracked as a future runtime-profile refinement).

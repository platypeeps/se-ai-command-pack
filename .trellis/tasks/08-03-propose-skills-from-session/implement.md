# Implement — se-propose-skills (packaged)

In-repo deliverable this time. Order matters: author → register → generate →
gate → verify.

## Checklist

1. **Confirm conventions from live code** (do not trust memory):
   - Read a peer skill end-to-end for exact section wording/patterns:
     `templates/skills/se-retro/SKILL.md` and `se-capture/SKILL.md`.
   - In `installer/registry.py`, find `se-retro` and `se-capture`: their `family`
     and their `RUNTIME_PROFILE_ASSIGNMENTS` group. Mirror the closest fit for a
     user-invoked, output-writing, session-review skill.
   - Read `.github/scripts/generate-skill-surfaces.py` REQUIRED_SECTIONS,
     ALLOWED_FRONTMATTER_KEYS, DESCRIPTION_PREFIX, BANNED_PHRASE_PATTERN to author
     against the real validators.

2. **Author** `templates/skills/se-propose-skills/SKILL.md`:
   - Frontmatter: `name: se-propose-skills`; `description:` starting `"Use when"`,
     single line, no double-quotes.
   - Sections in order: `## When to use`, `## Arguments`, `## Workflow`,
     `## Safety rules`, `## Final report` (design Contract A).
   - Embed the emitted-note template verbatim (design Contract B), including the
     Meta Bind dropdown line and the canon footer.
   - No banned brand names in the body — say "the current session" / "the
     assistant", never a product name. (Frontmatter `tags` in the *emitted note*
     may keep `claude` as an existing vault vocabulary value; that is note
     content, not this SKILL.md body.)

3. **Register** in `installer/registry.py`:
   - Add `SkillInfo(name="se-propose-skills", family="improve")` to `SKILLS`
     (verified peer: `se-retro`, registry line 134).
   - Add `se-propose-skills` to the same `RUNTIME_PROFILE_ASSIGNMENTS` group that
     holds `se-retro` (registry line ~193) — read the block, use that group name.
   - Guard: `description` must contain NO double quotes (validator line 210); keep
     body prose free of capitalized brand words (line 94 pattern is
     case-sensitive — lowercase `claude` tag in the embedded note is fine).

4. **Generate**: `make generate`. Confirm it created
   `generated/skills/claude/se-propose-skills/SKILL.md` and added manifest rows.

5. **Release gate**: read the current `manifest.json` `version`, bump it (minor)
   per the existing scheme, and add a matching `## <version> - 2026-08-03` heading
   to `CHANGELOG.md` describing the new skill.

6. **Supersede prototype (D7)**: remove
   `~/.claude/skills/propose-skills-from-session/` (the interim personal build).

## Validation commands (named checks)

- **Generator drift + validation:**
  `python3 .github/scripts/generate-skill-surfaces.py --check`
  Pass = exit 0, no drift, skill validated (sections/frontmatter/prefix/banned).
- **Registry import validation:**
  `python3 -c "import installer.registry"` (runs `validate_registry` at import) →
  exit 0.
- **Release-payload gate:**
  `python3 .github/scripts/check-release-payload.py` → exit 0 (version + dated
  CHANGELOG heading present).
- **Targeted tests:**
  `python3 -m pytest tests/test_generate.py tests/test_skills.py tests/test_release_gate.py -q`
  Pass = 0 failures.
- **Behavioral (the real acceptance test):** invoke `se-propose-skills` with
  `target=<tmpdir>` on this session and confirm a note appears at
  `<tmpdir>/System/Databases/Skill Proposals/<name>.md` with the verbatim dropdown,
  four sections in order, `status: proposed`, and no `ledger` fields. Then invoke
  with `profile=off` and confirm zero writes + inline report. Then a second
  `target=<tmpdir>` run skips the now-existing name.

## Named verification (per Verification rule)

Check: `generate-skill-surfaces.py --check` exits 0 AND
`pytest tests/test_generate.py tests/test_skills.py tests/test_release_gate.py`
is green AND a `target=<tmpdir>` invocation writes one canon note while
`profile=off` writes none. Failure = any nonzero exit, any red test, a written
note that diverges from Contract B, or a write when no target resolved.

Verifiable locally end-to-end (generator + pytest + a live invocation). No
external dependency.

## Risky points / rollback

- **Gate coupling:** editing `templates/**` without the manifest bump + CHANGELOG
  heading fails the release gate. Do steps 4–5 together.
- **Runtime-profile omission:** a registered skill with no profile assignment
  makes `validate_registry` raise at import — catches in step-2/3 immediately.
- **Meta Bind syntax:** copy the dropdown line verbatim; do not regenerate.
- **Writing into a real destination during behavioral test:** use a `target=`
  tmpdir, never the live vault, for the acceptance run.
- Rollback: revert the registry/generated/manifest/CHANGELOG commit and delete
  `templates/skills/se-propose-skills/`.

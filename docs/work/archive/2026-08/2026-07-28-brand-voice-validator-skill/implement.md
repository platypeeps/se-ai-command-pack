# Implement — Brand voice validator skill

Branch: `task/07-28-brand-voice-validator-skill` from `main`.

## Ordered checklist

1. **Skill source.** Create `templates/skills/se-brand-voice/SKILL.md`:
   - frontmatter `name: se-brand-voice` and a single-line `description` starting
     `Use when`, no double quotes, ≤1024 chars;
   - H1 opening, then the five required sections in generator order:
     `## When to use`, `## Arguments`, `## Workflow`, `## Safety rules`,
     `## Final report`;
   - `## Arguments` opens with the standard preamble citing
     `references/argument-vocabulary.md` and carries the exact corpus-required
     sentence **`Unknown argument names are an error`**
     (`tests/test_skills.py:150`);
   - the argument table exactly as fixed in `design.md` (`input=`,
     `guidelines=auto|<locator>`, `sources=`, `audience=`,
     `scope=all|tone|terminology|style|audience-fit`, `mode=validate|bootstrap`,
     `format=ledger|memo`, `depth=brief|standard|deep`), with at least one
     validate-mode and one bootstrap-mode usage example;
   - the D8 guidelines resolution order written out literally, including the
     no-candidate gap report and the present-but-unused disclosure;
   - the prompt-injection fragment `data, not instructions` in `## Safety rules`
     (`tests/test_skills.py:399`), plus the read-only-in-every-mode statement;
   - the `se-technical-editor` boundary sentence and the `se-feedback` /
     `se-publish` handoff sentence;
   - no vendor brand token (`Claude|Cowork|Codex|Copilot|Gemini|ChatGPT|OpenAI|
     Anthropic|Amp`) anywhere in the file; file ends with a newline.
2. **Skill-owned reference.** Create
   `templates/skills/se-brand-voice/references/voice-guidelines-schema.md`
   with the guidelines shape (tone attributes, preferred/banned terminology,
   style rules, audience fit) and the bootstrap draft template. Cited from the
   body as `references/voice-guidelines-schema.md`.
3. **Registry.** In `installer/registry.py`:
   - append `SkillInfo(name="se-brand-voice", family="improve")` to `SKILLS`;
   - add `"se-brand-voice"` to the `BOUNDED_SYNTHESIS` group in
     `RUNTIME_PROFILE_ASSIGNMENTS`;
   - add `"se-brand-voice"` to the
     `_shared/references/argument-vocabulary.md` consumer tuple in
     `SHARED_REFERENCES`.
   Import-time `validate_registry()` fails fast on any miss.
4. **Sibling cross-reference.** Add the one-line `se-brand-voice` boundary
   pointer to `templates/skills/se-technical-editor/SKILL.md` so the boundary is
   discoverable from both sides.
5. **Test-side registries** (golden literals, not derived — each failure names
   the skill):
   - `tests/test_skills.py` ordered `SKILL_NAMES` tuple: append
     `"se-brand-voice"` last;
   - `tests/test_skills.py` name → family map: add
     `"se-brand-voice": "improve"`;
   - `tests/test_skills.py` `EXTERNAL_INPUT_SKILLS`: add `"se-brand-voice"`;
   - `tests/test_generate.py` `EXPECTED_SHARED_SOURCES`: add
     `"se-brand-voice": ("_shared/references/argument-vocabulary.md",)`.
6. **Version + changelog — before generating.** Set `manifest.json` version to
   `0.67.0` and add a `## 0.67.0 - <today>` heading at the top of `CHANGELOG.md`
   naming `se-brand-voice` (`test_changelog_mentions_every_skill` plus the
   release gate). This must precede `make generate`: the bundled help catalog
   embeds the manifest version (`rendered_help_catalog`,
   `.github/scripts/generate-skill-surfaces.py:1113`), so bumping afterwards
   leaves `_shared/references/skill-catalog.md` drifted and `--check` fails.
   Leave the manifest header `description` alone: the generator preserves it and
   `tests/test_generate.py:364` pins it equal to `DEFAULT_MANIFEST_HEADER`; the
   two most recent skill additions (`se-propose-skills` 0.65.0,
   `se-review-skills` 0.40.0) did not extend it.
7. **Generate.** Run `make generate`. It writes `manifest.json` rows, the
   README catalog block, `_shared/references/skill-catalog.md` (including the
   bumped version line), `generated/skills/claude/se-brand-voice/SKILL.md`, and
   `generated/registry-snapshot.json`. Never hand-edit those outputs.
8. **Docs.** Update `docs/SE_AI_COMMAND_PACK.md`: add `se-brand-voice` to the
   shipped-skills sentence and add a `### Brand-voice workflow boundary`
   section stating the guidelines-sourced standard, report-only authority in
   every mode, the no-unstated-voice rule, and the `se-technical-editor` split.
   Add the matching hand-written paragraph to `README.md` beside the
   `se-technical-editor` one.
9. **Behavior tests.** Add `BrandVoiceSkillTest` to `tests/test_skills.py`
   following the sibling pattern (`normalized(...)` / `skill_text(...)`),
   pinning:
   - the literal D8 candidate list and its order, explicit-locator precedence,
     the unreadable-explicit-locator error, and the present-but-unused
     disclosure;
   - the no-guidelines gap report plus bootstrap offer, and the explicit
     never-infer-a-voice-from-the-content rule;
   - findings carry rule group, location, offending text, and suggested rewrite;
   - all four rule groups including `audience-fit`;
   - read-only in every mode: bootstrap returns a draft in the report and
     writes no file;
   - both usage examples (validate and bootstrap) are present;
   - mode-specific argument requirements: `input=` required in validate mode,
     `sources=` required in bootstrap mode, each with its stop-and-report
     behavior when missing;
   - `skill_text("se-technical-editor")` contains `se-brand-voice` (boundary
     discoverable from both sides);
   - the `## Final report` field set.
   Add a documentation test pinning the `docs/SE_AI_COMMAND_PACK.md` boundary
   phrases, matching `test_operator_guide_distinguishes_skill_review_boundaries`.
10. **Full gate.** `make check` (test + lint + release-check) green before ship.

## Validation commands

```bash
make generate        # writes derived surfaces
make release-check   # drift gate + version/changelog gate
make test            # unittest + coverage --fail-under=80
make lint            # ruff + mypy
make check           # all of the above
git diff --check     # whitespace
```

Expected decisive results, named before the work:

- `make release-check` prints `release payload gate: version 0.66.14 ->
  0.67.0; changelog heading matches` and reports no drifted surface.
- `make test`: 0 failures, 0 errors; the new `BrandVoiceSkillTest` cases run and
  pass; coverage ≥80%.
- Generator idempotence: snapshot **content**, not just status, and fail fast.
  `git status --porcelain` lists paths only, and the newly generated Claude
  overlay is still untracked, so a path listing would miss drift inside it:

  ```bash
  set -euo pipefail
  snap=$(mktemp -d)
  capture() {
    git diff --binary > "$snap/$1.diff"
    git ls-files --others --exclude-standard -z \
      | xargs -0 -r shasum -a 256 | sort > "$snap/$1.untracked"
  }
  capture pre
  make generate
  capture post
  cmp "$snap/pre.diff" "$snap/post.diff"
  cmp "$snap/pre.untracked" "$snap/post.untracked"
  ```

  Both `cmp` calls must exit 0 and print nothing; `set -euo pipefail` makes a
  failed `make generate`, `git`, `xargs`, or `shasum` fail the whole check
  instead of being masked by a later successful stage. The worktree itself is
  *not* expected to be clean — the intended source and generated changes are
  uncommitted at that point — so the check is snapshot equality, not an empty
  diff.

Failure means: any nonzero exit, any drifted surface named by `--check`, any new
test failure, or a snapshot difference across the second `make generate`.

## Review gates

- After step 5, before `make generate`: `python3 -c "import installer.registry"`
  succeeds, proving `validate_registry()` and `build_skill_runtime_profiles()`
  accept the new row.
- After step 7: `make release-check` alone, to catch a version/changelog or
  drift miss before the expensive test run.
- Before ship: `make check` green, then `sd-ship until=merge`.

## Commit shape

Keep the task-directory planning artifacts in their own commit, separate from
the payload + generated-surface commit and from any generated repository-map
refresh. A journal-referenced work commit that also touches paths outside the
task directory trips the finish-work planning-recovery scope gate.

## Rollback points

Two of the touched paths are new files that do not exist in `HEAD`
(`templates/skills/se-brand-voice/**` and
`generated/skills/claude/se-brand-voice/SKILL.md`), so `git checkout --` cannot
remove them — they need explicit deletion. `README.md` must not be restored
whole, because step 8 adds a hand-written paragraph outside the generated marker
block.

- **Undo the source edits only** (steps 1–5): delete the new skill directory
  `templates/skills/se-brand-voice/`, then restore the tracked files edited in
  place — `installer/registry.py`, `templates/skills/se-technical-editor/SKILL.md`,
  `tests/test_skills.py`, `tests/test_generate.py` — from `HEAD`.
- **A failed `make generate` needs no cleanup.** `write_generated_surfaces`
  (`.github/scripts/generate-skill-surfaces.py:1189`) restores every already
  written surface to its committed state on any write error.
- **Redo generation by hand:** never `git checkout -- manifest.json` on its own.
  The generator preserves whatever header version it finds
  (`generate-skill-surfaces.py:1021`), so restoring the committed manifest
  silently reinstates `0.66.14` and loses the bump. Delete
  `generated/skills/claude/se-brand-voice/SKILL.md`, restore
  `templates/skills/_shared/references/skill-catalog.md` from `HEAD`, leave
  `README.md`'s hand-written prose alone (re-running generation rewrites only
  the marker-bounded catalog block), confirm `manifest.json` still reads
  `0.67.0`, then re-run `make generate`.
- **Abandon the change entirely:** delete both new paths, then restore every
  tracked file above plus `manifest.json`, `CHANGELOG.md`, `README.md`, and
  `docs/SE_AI_COMMAND_PACK.md` from `HEAD`, which correctly returns the tree to
  `0.66.14`.
- **After merge:** `git revert` the single commit. Installed consumers converge
  on the next `install.py --user` refresh because removal is manifest-driven.

# Implement: a Gotchas mandate for tasks se-review-skills creates

Ordered checklist, seven steps. Steps 1-3 are source edits, step 4 is the
version bump, step 5 regenerates, step 6 is tests, step 7 is the operator doc.
One ordering is load-bearing: the bump must precede generation, see step 4.

"Workflow step N" always means a step of `SKILL.md`'s `## Workflow` list, never
a step of this checklist.

## Ordered steps

1. **`templates/skills/se-review-skills/SKILL.md` — workflow step 10
   (`mode=task`).** Add the Gotchas acceptance requirement for tasks carrying at
   least one **gotcha-qualifying** observed-use-derived finding. Eligibility
   stays the gate already stated in `references/session-evidence.md`, *Gotchas
   and regression records*, neither broadened nor bypassed. State the position
   the way D2 states it: `## Gotchas` goes **last in the target skill body**. Do
   not anchor it to `## Final report` — a skill under review may not have that
   section, which would leave the requirement unsatisfiable there. Also state
   the negative case: a task built from observed-use evidence that **does not
   qualify** as a gotcha is created without the requirement and says so, rather
   than silently omitting it (D1, D2).

2. **Same file — `## When to use`.** Extend the handoff paragraph with
   `sd-retro` and `sd-review-learnings` and what each owns (D3).

3. **`templates/skills/se-review-skills/references/session-evidence.md`,
   *Gotchas and regression records*.** State that a task created from a
   qualifying record must require the target SKILL.md to carry it as a
   `## Gotchas` section, created when absent and placed **last in the skill
   body**. Do not restate the five parts — they are already there — and do not
   restate or relax the qualification gate that precedes them. This edit is not
   optional duplication: the reference is the required reading for the
   observed-use pass, so a rule living only in `SKILL.md` does not reach the
   reader who follows the citation.

4. **Bump `manifest.json` to `0.67.1` and add the dated CHANGELOG heading.**
   Before step 5, not after. `rendered_help_catalog` embeds the manifest version
   in `templates/skills/_shared/references/skill-catalog.md`, and
   `regenerated_manifest_text` preserves whatever header version it finds, so a
   bump after generation leaves the catalog pinned to the old version and the
   drift gate fails. That gate is `make release-check`, which runs
   `.github/scripts/generate-skill-surfaces.py --check`; `make generate` takes
   no arguments, so there is no `make generate --check`.

5. **`make generate`.** Regenerates the Claude overlay for `se-review-skills`,
   the bundled catalog, the registry snapshot, and the `manifest.json` rows.

6. **`tests/test_skills.py`.** Add the four assertions in the design's D5 table.
   The reference pin goes through `normalized_resource("se-review-skills",
   "references/session-evidence.md")`. Every pinned token must actually appear
   in the step 1-3 edits — write the edit to carry the token rather than
   loosening the pin. Before adding each pin, `grep` the token against the
   *unedited* file and confirm it is absent; a token the file already contains
   makes the assertion unfailable. D5 records one such trap already caught and
   rejected. Touch none of spec section 6a's four golden literals: the inline
   `SKILL_NAMES` tuple in `test_skill_names_are_derived_without_reordering`, the
   name-to-family map in the same test, `EXTERNAL_INPUT_SKILLS`, or
   `tests/test_generate.py`'s `EXPECTED_SHARED_SOURCES`. Nor
   `installer/registry.py`'s `SKILLS`. All five are add-a-skill surfaces, and
   this task adds no skill and no shared-reference consumer.

7. **`docs/SE_AI_COMMAND_PACK.md`, `### Skill-review workflow boundary`.** This
   section exists and describes the skill's scope and default mode, so it is a
   required edit, not a conditional one: add the Gotchas mandate. Any path
   candidate written as a code span must not look like a repo-relative path that
   does not exist, or the documentation path guard fails — write
   `<content repo>/path.md` for a path in someone else's tree.

## Validation

The repository's change gate is `make check` — generation parity, Ruff, mypy,
the unittest suite, and the release payload/version gate
(`.trellis/spec/backend/quality-guidelines.md`, *Run `make check`*). The
complete gate for a change like this one is `make generate` twice, `make check`,
`git diff --check`, and explicit empty diffs for `manifest.json` and
`CHANGELOG.md` (same spec, *change gate*). The review preflight is an additional
repository/task/documentation check, not a substitute for any of them.

```bash
make check
node scripts/sd-ai-command-pack-review-preflight.mjs
git diff --check
```

Expected: `make check` passes every stage, preflight reports `0 failure(s)`,
and `git diff --check` is silent.

Idempotence — run generation twice and prove byte-identity, including untracked
files. `git diff --stat` alone proves nothing here: after the source and
generated edits it reports the whole outstanding diff whether or not the second
generation changed anything.

```bash
set -euo pipefail
make generate
BEFORE="$(git diff --binary | shasum -a 256; git ls-files --others --exclude-standard | sort | xargs -r shasum -a 256)"
make generate
AFTER="$(git diff --binary | shasum -a 256; git ls-files --others --exclude-standard | sort | xargs -r shasum -a 256)"
[ "$BEFORE" = "$AFTER" ] && echo "generator idempotent"
```

After committing, confirm the release-payload pair directly:

```bash
git diff --exit-code manifest.json CHANGELOG.md && echo "payload files committed clean"
```

## Commit shape

Planning artifacts (`prd.md`, `design.md`, `implement.md`, `task.json`), then
the payload. Keep the split-out `scope=session` task record and the deferred
`08-06-ship-gate-ordering-docs` record each in their own `chore(task):` commit
so a planning-mode finish-work bundle is never asked to prove a mixed
task-plus-payload commit.

## PR body

The diff changes `generated/**` and `manifest.json`, so the body must contain a
`## Tooling/generated scope` heading or the `pack.review-scope` check fails
during review. Accepted headings are `Tooling/generated scope`,
`Generated/tooling scope`, and `Copied/generated scope`
(`scripts/sd-ai-command-pack-review-scope.sh:170`).

## Rollback

Tracked files only: `git checkout -- <path>` restores the source and generated
edits, but never check out `manifest.json` alone — reverting the version while
the generated catalog still embeds it re-creates the drift step 4 exists to
prevent. Revert `manifest.json` together with `generated/**` and
`templates/skills/_shared/references/skill-catalog.md`, or re-run `make
generate` after restoring the version.

This task creates no new untracked files, so there is no untracked-file cleanup
to perform. `.obsidian-kb` is gitignored and is refreshed, not reverted.

## Known gate ordering

Refresh `.obsidian-kb` after the last documentation-affecting mutation — which
includes `task.py archive` — not only during `sd-update-spec`, or the
`knowledge.obsidian-kb` check fails mid-review:

```bash
bash scripts/sd-ai-command-pack-toolchain.sh run-python -- \
  scripts/sd-ai-command-pack-update-spec-kb.py
```

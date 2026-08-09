# Document ship-loop gate ordering: PR-body tooling scope and KB refresh points

## Goal

Two deterministic `sd-check` gates block mid-ship for reasons that are not
discoverable before they fire. Both cost a review round to diagnose during the
`se-brand-voice` ship (PR #152), and **both fired again on PR #156**, which is
what promotes this from a one-off annoyance to a recurring tax. Record them
where the next run reads them.

## Background

> Line citations below are pinned to installed pack `0.64.3`:
> `scripts/sd-ai-command-pack-review-scope.sh` at 414 lines and
> `scripts/sd-ai-command-pack-pr-body-scope.py` at 839 lines. Both are
> `install: "always"` in `.sd-ai-command-pack/manifest.json`, so a pack refresh
> overwrites them and the line numbers move. Two files are cited here, so every
> citation names its file as well as its enclosing symbol — shell function or
> Python definition. Re-locate by symbol, not by line, on any other version.

**`pack.review-scope`.** When a branch changes tooling/generated files, the PR
body must contain a recognized scope heading — `Tooling/generated scope`,
`Generated/tooling scope`, or `Copied/generated scope`
(`github_pr_body_mentions_scope`,
`scripts/sd-ai-command-pack-review-scope.sh:170`). Nothing prompts for it at PR
creation time, and the failure surfaces only after `sd-review` runs its typed
`sd-check`. Every skill-addition PR regenerates `generated/**`, `manifest.json`,
and the bundled catalog, so every such PR needs the section.

**The mixed-scope case has no automated remedy.** PR #156 hit a variant this
PRD originally missed. `sd-ai-command-pack-pr-body-scope.py
--prepare-tooling-body` auto-appends the section only for a diff that is
entirely tooling; on an empty or mixed diff it exits `3`
(`scripts/sd-ai-command-pack-pr-body-scope.py:36`) and writes nothing. PR #156
changed `.prism/rules.json` (tooling) together with
`.trellis/spec/backend/quality-guidelines.md` (authored prose), so the
preparer correctly declined while `pack.review-scope` still failed. The run
must then hand-author the section and verify it against the check's own
`grep -Eiq` pattern. The helper is not silent — it prints an `info:` line
saying the body was left unchanged because the diff is not
tooling/generated-only — but that message is descriptive, not directive: it
names the condition without stating that a hand-authored section is now the
operator's job. Combined with exit `3` being a non-error, a run that knows
only "the preparer adds it" reads the info line as benign and retries the
preparer instead of writing the section.

**The third scope category fires after the PR body is already written.** The
check recognizes three categories, not one — classified in `main`'s dispatch
(`scripts/sd-ai-command-pack-review-scope.sh:348-356`): copied/generated Trellis
or pack files (`is_copied_review_scope_path`), known repository-map files
(`docs/repomix-map.md`, `scripts/update_repomix`), and **Trellis workspace
journal/index files** — `.trellis/workspace/*/journal-*.md` and
`.trellis/workspace/*/index.md` (`is_trellis_journal_scope_path`,
`scripts/sd-ai-command-pack-review-scope.sh:154-162`).
PR #152 and #156 both hit the first category, so this PRD originally described
only that one.

The journal/index case is structurally guaranteed rather than incidental, and it
arrives late. A branch whose diff contains no scoped file at PR-creation time
correctly gets no scope section and passes. Planning finalization then commits
the journal and workspace index, and `pack.review-scope` fires on the
successor-head re-entry — after the body was authored and judged complete.
`--prepare-tooling-body` does not pre-empt it either — but **not** for the
mixed-diff reason above, and getting this wrong points at the wrong remedy. Both
`.trellis/tasks/**` and `.trellis/workspace/**` are tooling patterns in
`DEFAULT_RULES` (`scripts/sd-ai-command-pack-pr-body-scope.py:117-118`), and
`prepare_tooling_body` returns `3` only for an empty diff or one containing a
path that no tooling pattern matches
(`scripts/sd-ai-command-pack-pr-body-scope.py:615-644`).
PR #163's diff was 19 files, all inside those two families — zero unmatched — so
the preparer *would* have appended the section. It was never given the chance:
`sd-create-pr` forbids running automatic preparation against a user-provided
body, requiring it be preserved byte-for-byte
(`.agents/skills/sd-create-pr/SKILL.md:276-279`), and these planning PRs all
carry custom bodies.

So this is a policy boundary, not a classification failure, and the remedy
follows from that: for a custom-bodied PR the run must author the section itself,
because the one tool that would have added it is deliberately not consulted. The
genuinely mixed case above (PR #156) is a different failure with the same
symptom — there `.trellis/spec/**` matches no tooling pattern, so the preparer
declines on the merits even when it is run.

Observed on PR #163 (2026-08-07): `sd-review` failed `pack.review-scope` twice
before the body gained a hand-authored `Tooling/generated scope` section, then
passed on attempt 3.

PR #162 is the instructive comparison, and it is instructive in the opposite
direction from the obvious guess. Its diff contained **no** pack-target or
Trellis-runtime file — its own body states "No shipped file changes. Every path
is under `.trellis/tasks/`", and `.trellis/tasks/**` matches neither
`is_pack_target_path` (`scripts/sd-ai-command-pack-review-scope.sh:116-128`,
exact installed targets plus three metadata paths) nor `is_trellis_runtime_path`
(`scripts/sd-ai-command-pack-review-scope.sh:86-114`, which lists runtime and
platform directories and excludes task artifacts). Its only scoped path was the same
finalization journal/index pair. So both PRs triggered the gate through the same
third category, and the difference in outcome was **not** in the diff: #162's
body already carried a `Tooling/generated scope` section, written proactively to
describe the task-metadata review surface, and #163's did not.

That is the practical lesson and it is stronger than a diff-shape rule: a run
cannot decide from the diff at PR-creation time whether the section will be
needed, because the diff that decides it does not exist yet. Writing the section
proactively is what worked. Note also that `.trellis/tasks/**` *is* in scope for
the Python PR-body helper (`DEFAULT_RULES`,
`scripts/sd-ai-command-pack-pr-body-scope.py:107`), which is a wider path set
than the shell check enforces (`scripts/sd-ai-command-pack-pr-body-scope.py:117-120`
lists `.trellis/tasks/**` and `.trellis/workspace/**` alongside the runtime
directories) — two tools with different scopes, so neither one's coverage
predicts the other's.

**`knowledge.obsidian-kb`.** The KB check compares `.obsidian-kb` against the
current tracked documentation set and fails when it drifts. It went stale twice
in one ship: once after an edit to `docs/SE_AI_COMMAND_PACK.md` made *after*
`sd-update-spec` had already refreshed the KB, and again after
`task.py archive` moved the task directory under `.trellis/tasks/archive/`.
The refresh is idempotent and touches only gitignored paths, so the fix is
cheap — but only if the run knows to do it after the last documentation-shaped
mutation rather than once at the start.

## Requirements

- Record both gates in `.trellis/spec/backend/quality-guidelines.md`, alongside
  the existing section 6a add-skill ordering contract, with the exact heading
  strings the scope check accepts and the exact remediation command for the KB
  check.
- State the ordering rule for the KB refresh explicitly: refresh after the last
  documentation-affecting mutation of the branch, which includes the archive
  commit, not merely once during `sd-update-spec`.
- State that `--prepare-tooling-body` covers only tooling-only diffs, that a
  mixed diff exits `3` without writing, and that the section must then be
  hand-authored and checked against the accepted-heading pattern.
- Enumerate all three scope categories, not just copied/generated files, and
  state the ordering consequence of the journal/index one: a scope section that
  was correctly absent at PR creation becomes required once planning
  finalization commits the journal and workspace index, so the body needs the
  section before the successor-head re-entry rather than at creation time.
  Enumerate from the check's own predicates, not from the categories these
  observed PRs happened to hit — the single-category reading is exactly the error
  this task's first draft made.
- Prefer documentation over new automation. Do not add a new check, a PR
  template requirement, or a generator rule as part of this task.

Placement note: `quality-guidelines.md` now has a second conventions home — the
`## Review And Retry Conventions` section added by PR #156, which sits before
`## Code Review Checklist` rather than near section 6a. Read the file before
adding to it and pick the better of the two homes; do not assume a single
location.

## Acceptance Criteria

- [x] `.trellis/spec/backend/quality-guidelines.md` names all three accepted
      scope headings and states which file families trigger the requirement.
      SATISFIED 2026-08-09: the new `pack.review-scope` convention in
      `## Review And Retry Conventions` lists `Tooling/generated scope`,
      `Generated/tooling scope`, `Copied/generated scope` (verbatim from
      `github_pr_body_mentions_scope`) and the triggering file families per
      category.
- [x] The same document names all three *scope categories* the check recognizes
      — a distinct set from the three accepted *headings* in the criterion above;
      the headings are what the PR body may say, the categories are what makes it
      required — including Trellis workspace journal/index files, and states that
      the journal/index category is added by planning finalization rather than
      present at PR creation. Verified by comparing the documented list against
      the predicates in `sd-ai-command-pack-review-scope.sh`, not against the
      categories any one PR triggered.
      SATISFIED 2026-08-09: the three categories are enumerated one predicate
      each (`is_copied_review_scope_path`, `is_repository_map_scope_path`,
      `is_trellis_journal_scope_path`), verified against the `main` dispatch in
      `sd-ai-command-pack-review-scope.sh`, with the journal/index category
      stated as added by finalization after the body was authored.
- [x] The same document states why `--prepare-tooling-body` does not cover the
      journal/index case for a custom-bodied PR — because `sd-create-pr` will not
      run it against a user-provided body, not because the diff fails the
      tooling-only test — and therefore that authoring the section by hand is the
      standing requirement for such PRs. A statement that blames the diff shape
      is wrong and does not satisfy this criterion.
      SATISFIED 2026-08-09: the custom-bodied-PR bullet states the preparer is
      deliberately never consulted (`sd-create-pr` byte-for-byte body
      preservation) even when every path would match, and that hand-authoring
      is the standing requirement; it explicitly warns that blaming the diff
      shape points at the wrong remedy.
- [x] The same document states that `task.py archive` invalidates the KB and
      names the refresh command.
      SATISFIED 2026-08-09: the KB convention names the archive commit as a
      staleness source and quotes the exact refresh command
      (`update-spec-kb.py --if-present`).
- [x] The same document states the mixed-scope limitation of
      `--prepare-tooling-body`, including that exit `3` is a non-error that
      requires a hand-authored section.
      SATISFIED 2026-08-09: the mixed-diff bullet states exit `3` is a
      non-error that writes nothing and requires a hand-authored section
      (observed PR #156, PR #172).
- [x] No behavior change: no new or modified check, generator rule, or test
      beyond what documenting these facts requires.
      SATISFIED 2026-08-09: the diff touches only
      `quality-guidelines.md` and this task's artifacts.

## Out of scope

- Adding a PR-body template or a check that authors the scope section.
- Changing either gate's behavior or its failure message.
- Broader review-learnings curation.

## Notes

- Planning depth: PRD-only. Documentation of two existing gates; neither gate's behaviour changes.

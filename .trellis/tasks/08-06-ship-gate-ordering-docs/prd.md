# Document ship-loop gate ordering: PR-body tooling scope and KB refresh points

## Goal

Two deterministic `sd-check` gates block mid-ship for reasons that are not
discoverable before they fire. Both cost a review round to diagnose during the
`se-brand-voice` ship (PR #152). Record them where the next run reads them.

## Background

**`pack.review-scope`.** When a branch changes tooling/generated files, the PR
body must contain a recognized scope heading — `Tooling/generated scope`,
`Generated/tooling scope`, or `Copied/generated scope`
(`scripts/sd-ai-command-pack-review-scope.sh:170`). Nothing prompts for it at PR
creation time, and the failure surfaces only after `sd-review` runs its typed
`sd-check`. Every skill-addition PR regenerates `generated/**`, `manifest.json`,
and the bundled catalog, so every such PR needs the section.

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
- Prefer documentation over new automation. Do not add a new check, a PR
  template requirement, or a generator rule as part of this task.

## Acceptance Criteria

- [ ] `.trellis/spec/backend/quality-guidelines.md` names all three accepted
      scope headings and states which file families trigger the requirement.
- [ ] The same document states that `task.py archive` invalidates the KB and
      names the refresh command.
- [ ] No behavior change: no new or modified check, generator rule, or test
      beyond what documenting these facts requires.

## Out of scope

- Adding a PR-body template or a check that authors the scope section.
- Changing either gate's behavior or its failure message.
- Broader review-learnings curation.

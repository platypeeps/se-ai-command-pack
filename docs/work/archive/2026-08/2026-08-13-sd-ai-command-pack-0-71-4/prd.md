---
title: sd-ai-command-pack 0.71.4 refresh
status: done
created: 2026-08-13
branch: chore/sd-ai-command-pack-0.71.4
---
# sd-ai-command-pack 0.71.4 refresh

## Goal

Install sd-ai-command-pack 0.71.4 in se-ai-command-pack, replacing the installed
0.71.2, as part of fleet campaign `refresh-0.71.4-20260813T212139Z`.

## Release identity

- Release: `0.71.4` (corrective release)
- Source: `platypeeps/sd-ai-command-pack`, tag `v0.71.4`
- Payload digest: `sha256:f4c54899ce669bc5b171e95ab6dbf22702ebf5e121a41201c0a37604cd733767`
- Installed version before this refresh: `0.71.2`
- Base commit: `2d3c0e15abc036d590d7ed5f10de8016df8a5b14` on `main`

## Why the diff is larger than a 0.71.2 to 0.71.4 delta

The installer refused four targets as conflicts because their on-disk content
did not match the recorded 0.71.2 payload:

- `scripts/sd-ai-command-pack-review-preflight.mjs`
- `docs/SD_AI_COMMAND_PACK.md`
- `.agents/skills/sd-help/references/command-catalog.md`
- `.claude/skills/sd-help/references/command-catalog.md`

Each file's history contains only pack-refresh commits, so none carries
se-ai-command-pack-authored content and `--force` discards no local work. Every consumer
refreshed in this campaign produced the identical four-file conflict set, so
this is upstream installer behavior rather than local drift.

## What 0.71.4 corrects

`sd-ai-command-pack-review-preflight.mjs` accepted a seeded task whose
`implement.jsonl` / `check.jsonl` context manifests existed but contained no
usable rows. The `seeded-task` gate now emits `task_context_unfilled` for that
shape, and the whitespace sweep runs before the unfilled decision so a manifest
emptied to padded blank lines reports only the whitespace defect rather than
double-reporting.

## Managed scope

This refresh changes only installer-managed pack files, this task's own
artifacts, and repo-owned deterministic preparation output:

- pack installer targets recorded in `.sd-ai-command-pack/manifest.json`
- `.sd-ai-command-pack/` provenance and installed-target records
- this task's own directory, which finalization archives under
  `.trellis/tasks/archive/` before the pull request is opened
- `.trellis/workspace/**` journal and index entries

No se-ai-command-pack product code is edited.

## Preparation and check commands

- Prepare: none; this consumer declares no deterministic preparation step
- Candidate check: `bash scripts/sd-ai-command-pack-housekeeping.sh --self-test`
- Local gate: the installed typed `sd-check` coordinator

## Requirements

- Install 0.71.4 over 0.71.2 without touching product code.
- Keep the working tree free of changes outside the managed scope above.
- Publish the refresh on `chore/sd-ai-command-pack-0.71.4` and open a PR
  targeting `main`.

## Acceptance Criteria

- [ ] `.sd-ai-command-pack/provenance.json` reports version `0.71.4`.
- [ ] The install audit passes with every recorded target verified.
- [ ] Every candidate check listed above passes.
- [ ] The typed `sd-check` gate passes.
- [ ] The refresh diff contains no path outside the managed scope.
- [ ] The PR is published against `main` and reviewed clean.

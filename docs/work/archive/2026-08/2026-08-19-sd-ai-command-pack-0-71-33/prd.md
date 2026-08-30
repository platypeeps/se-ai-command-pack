---
title: Refresh sd-ai-command-pack to 0.71.33
status: done
created: 2026-08-19
branch: chore/pack-refresh-0.71.33
---
# Refresh sd-ai-command-pack to 0.71.33

## Goal

Fleet refresh: install sd-ai-command-pack v0.71.33 (tag v0.71.33 @ 6c6d05a6450e1d52b22b0b08d8f275d4af358115, payload sha256:0fe1997c752034d6ce6231c235565ac7c79e8c369a42561f24ad1e9dbc67667a) into se-ai-command-pack, replacing the 0.71.22 pin. Managed scope: installer-managed platform files (claude, gemini, github, opencode), receipts, and provenance only; no product-code edits. Prepare: none. Check: the pack housekeeping self-test. Bound to refresh branch chore/pack-refresh-0.71.33 off base d02ef08e441f9fc370168e61bac88b874017cf05. Completion: PR opened, remote review, CI green, merged via housekeeping, post-merge audit confirms 0.71.33.

## Requirements

- Install sd-ai-command-pack v0.71.33 (tag `v0.71.33` @ `6c6d05a6450e1d52b22b0b08d8f275d4af358115`, payload `sha256:0fe1997c752034d6ce6231c235565ac7c79e8c369a42561f24ad1e9dbc67667a`) for exactly the claude, gemini, github, and opencode platforms recorded in the fleet manifest. This consumer is a thin install: its platform set is owned by its pin, so the refresh carries no `--platform` flag.
- Limit the diff to installer-managed platform files, `.sd-ai-command-pack/` manifest and provenance receipts, and this task's own `.trellis/` bookkeeping. No product-code edits.
- Run this consumer's manifest-ordered check command, the pack housekeeping self-test, before the local gate. This consumer declares no preparation command.
- Run the repository's documented full local gate: `make gate-test`, `make gate-lint`, `make lock-check`, `make shell-syntax`, and `make trellis-provenance`, as declared in `.sd-ai-command-pack/check.json`.
- Keep the refresh on branch `chore/pack-refresh-0.71.33` off base `d02ef08e441f9fc370168e61bac88b874017cf05`, published as a single PR.
- Carry no `trellis update` diff. Trellis version drift is owned separately; a mixed PR stops the lane instead of merging.

## Acceptance Criteria

- [x] The pack install audit, run from the sd-ai-command-pack source checkout
  with `--repo` pointed at this repository, passes for all four expected
  platforms and reports installed payload provenance 0.71.33.
- [x] This consumer's manifest-ordered check command passes.
- [x] The declared full local gate passes, or its only findings are dispositioned through the fleet finding severity gate with zero blockers.
- [x] The refresh is committed as exactly one work commit on `chore/pack-refresh-0.71.33`, containing only installer-managed paths.
- [x] The three pre-existing `planning` tasks in this repository are left untouched. This refresh owns only its own task directory.

## Post-archive handoff

Owned by the fleet campaign after this task is archived, not by its acceptance
criteria: publish the branch as one PR whose head carries the work commit plus
this task's archive and journal bookkeeping, merge through the housekeeping
gate, delete the refresh branch, synchronize the default branch, and record the
post-merge install audit as the lane's `post-merge-verification` receipt.

## Local gate disposition

The declared gate passes on every repository check — `make gate-test`,
`make gate-lint`, `make lock-check`, `make shell-syntax`, and
`make trellis-provenance` — and the pack install audit passes with 31 targets
checked at provenance 0.71.33.

The shared review preflight reports 29 findings across two pre-existing files:
28 missing-path references in `.trellis/spec/backend/quality-guidelines.md` and
one personal-absolute-path line in an archived task's `disposition.md` under
`.trellis/tasks/archive/2026-08/`. Neither file is touched by this refresh:
`git diff --name-only origin/main` over those paths returns zero files, and the
offending lines are byte-present in `origin/main`. The missing references name
pack helpers and skill files that stopped existing in this checkout when the
consumer converted to a thin install, so the guard's missing-path rule now
fires on documentation that predates the conversion.

Both groups were dispositioned through the fleet finding severity gate as
contract family `consumer-unrelated`, final disposition `defer-follow-up`, with
the gate returning `continue-with-follow-ups` and zero blockers. Fixing that
debt belongs to a separate session that owns those files.

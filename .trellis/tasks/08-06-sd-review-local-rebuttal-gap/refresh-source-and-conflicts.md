# Refresh source pin and conflict disposition

## Source

- Upstream: sd-ai-command-pack tag `v0.64.32`, commit `59912b94`
  ("Merge pull request #393 from platypeeps/codex/status-worktree-inventory").
- Materialized as a clean detached git worktree (scratchpad
  `sd-pack-v0.64.32`); `git status --short` empty at refresh time. The sibling
  checkout itself was at `v0.64.32-16-g39473e09` with modified installable
  templates and was therefore NOT used as the source, per the PRD's
  clean-source requirement.

## Pre-force dry run (captured)

- `refresh-check.json` — `install.py . --check --json`, exit 3
  (`refresh-required`): installedVersion 0.64.3, sourceVersion 0.64.32,
  changeCount 36 = 34 conflict + 2 updated (+2 preserved, 172 unchanged).
- `refresh-dryrun.txt` — `install.py . --dry-run`, exit 2, per-file listing.

## Conflict disposition

Audit line: "Installed payload provenance: version 0.64.3; vouched file hashes
match." — the installed payload is exactly what the 0.64.3 manifest shipped,
so no conflict can be unexplained local drift. All 34 conflicts are
upstream-version differences in pack-owned payload (scripts/, docs/,
.claude/skills/, .agents/skills/, planning-adversarial-review.md).
Disposition: proceed with forced refresh; keep installer backups.

Note: an earlier review estimate of 59 conflicts came from probing against the
dirty sibling worktree; the clean v0.64.32 tag yields 34.

## Refresh execution and verification (2026-08-09)

- `install.py . --force --backup` from the pinned worktree: exit 0
  (`refresh-apply.txt`). Manifest now records 0.64.32.
- Installer `.bak` backups (34 files) initially failed the structural audit
  ("pack-like file is not listed in installed targets"). They were archived to
  the session scratchpad as `refresh-backups-v0.64.3.tar.gz` (34 entries
  verified) and removed from the tree. Durable restoration path is git: every
  pre-refresh original is in HEAD (`main`/task-branch base), so
  `git checkout HEAD -- <file>` restores any payload file.
- Post-refresh `--check --json`: `state: current`, version 0.64.32, audit
  passed, "vouched file hashes match".
- Fail-closed probes against the installed `review-local` script
  (`failclosed-probe.txt`): malformed value, duplicate id, and unmatched id
  each rejected with the documented error; a matching id is applied and the
  finding retained with `disposition: rebutted`.
- Upstream behavioral tests at the pinned v0.64.32 worktree
  (`upstream-tests.txt`): 6/6 disposition/rebuttal cases pass via
  `python -m unittest tests.test_review_stage -k disposition -k rebut`,
  including `test_rebutted_local_finding_clears_the_gate_but_stays_visible`
  and `test_rebuttal_does_not_carry_to_a_different_head`.

## Local fork retirement (found by refresh-diff unit review)

The refresh reverted local commit `bc01bc2` ("fix(review): recompute
deterministic sd-check every run, don't serve stale cache"), which had forked
the vendored `scripts/sd-ai-command-pack-review.py` with a `_resolve_check()`
recompute wrapper. Upstream v0.64.32 never adopted that shape; it fixed both
live inputs the fork guarded against at their source instead:

- 0.64.22: a failing external-symlink `.obsidian-kb` check row is advisory,
  not blocking (this repo's `.obsidian-kb` IS an external symlink, so this
  applies here).
- 0.64.4 #6: `review-scope.sh` ignores a CLOSED/MERGED same-branch PR body.

Disposition: the revert is accepted — the task PRD forbids local forks of the
vendored surfaces, and the fork's motivating inputs are fixed at source.
`tests/test_review_coordinator.py` (5 tests, all pinning the removed
`_resolve_check`) is deleted with it. The fork lifecycle is the subject of
`08-07-review-py-local-fork`, which should be re-scoped or closed against this
retirement.

Residual, named per the diff-review requirement: upstream's memoization of the
typed sd-check report remains; 0.64.30 adds a new root-task `base_branch`
preflight rule not exercised by this task's verification.

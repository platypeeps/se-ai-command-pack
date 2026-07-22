# Handle root Obsidian KB symlinks safely

## Goal

Prevent the KB refresh helper from following a root .obsidian-kb symlink into an external vault; detect, report, and safely migrate or stop while preserving the target.

## Resolution

Closed without a consumer-local implementation. The helper is an installed
`sd-ai-command-pack` surface, and upstream
[PR #212](https://github.com/platypeeps/sd-ai-command-pack/pull/212) already
shipped the canonical lifecycle contract. That contract intentionally preserves
and uses a valid directory symlink (including an external vault) while rejecting
broken links, non-directory targets, and occupied non-directory roots before
writes. Rejecting every root symlink here would both drift from the installed
source and reverse the accepted upstream behavior. Updating this repository's
installed SD pack is a separate maintenance operation, not an implementation
inside `se-ai-command-pack`.

## Requirements

- Classify the root `.obsidian-kb` path with non-following filesystem checks
  before any existence, directory creation, traversal, copy, prune, or write.
- Treat a root symlink as an explicit conflict in refresh, dry-run, check, and
  `--if-present` modes; never follow it into its target or report it as absent.
- Preserve the symlink and its target by default. Report a recovery path that
  lets the operator move or remove only the link, then regenerate a normal
  ignored directory.
- Keep ordinary absent-directory, real-directory, and legacy symlinks *inside*
  a real KB directory behavior compatible.
- Avoid exposing unnecessary external target details in diagnostics.

## Acceptance Criteria

- [ ] A root symlink to an external directory causes no reads or writes through
      the link and returns a documented nonzero conflict result.
- [ ] `--if-present` detects the root symlink instead of silently skipping it.
- [ ] Dry-run, check, and refresh agree on the root-path classification.
- [ ] Tests cover absolute and relative escaping links, dangling links, an
      absent path, and a normal generated directory while preserving sentinels.
- [ ] Focused tests, full checks, documentation/spec review, and `git diff
      --check` pass.

## Out of Scope

- Copying data into the external target, deleting the target, or automatically
  choosing a migration destination.
- Changing vault-copy instructions or Obsidian application configuration.

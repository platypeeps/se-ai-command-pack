# Handle root Obsidian KB symlinks safely Implementation Plan

## Execution Order

1. Add failing tests for absolute, relative-escaping, and dangling root links in
   refresh, check, dry-run, and `--if-present` modes.
2. Add one non-following root classifier and a shared actionable conflict result.
3. Gate every mode before source discovery, directory creation, traversal, or copy.
4. Preserve current absent-root, real-directory, and internal legacy-link behavior.
5. Update durable quality/error guidance only if the implementation establishes
   a repository-wide filesystem rule not already documented.

## Validation Plan

- Focused KB helper tests with external sentinels.
- `make check` and `git diff --check`.
- Manual dry-run against an isolated root symlink, verifying target checksums and
  entries are unchanged.

## Rollback Points

- Revert the classifier and focused tests together if mode dispatch cannot share
  one safe contract without changing ordinary directory behavior.
- Do not weaken the conflict to a warning or add automatic link deletion to make
  the gate pass.

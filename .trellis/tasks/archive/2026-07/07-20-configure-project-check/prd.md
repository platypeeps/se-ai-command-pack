# Configure repository project check

## Goal

Make the deterministic `sd-review-pr` local gate run this repository's
canonical `make check` target before the shared SD pack full-check, so generated
repository-map drift and the complete Python quality suite are caught before a
remote reviewer is requested.

## Background

- `make check` already owns this repository's tests, Ruff, mypy, generated
  surface parity, release validation, and the Repomix contract.
- The toolchain doctor currently reports `make:check` only as a candidate;
  `SD_AI_COMMAND_PACK_PROJECT_CHECK_COMMAND` is not persisted by this
  repository and doctor does not execute inferred candidates.
- The toolchain doctor recognizes an explicit root package script named
  `check` as a project-check candidate. The review selector separately supports
  a repository-owned `check:full` script and otherwise falls back directly to
  `scripts/sd-ai-command-pack-full-check.sh`.
- The shared full-check does not execute `check:full` from its ordinary package
  script list, so a wrapper can call the shared full-check without recursion.

## Requirements

1. Define a repository-owned `check` script as the single package-level owner
   of `make check`.
2. Provide a `check:full` wrapper that runs the package `check` script before
   `scripts/sd-ai-command-pack-full-check.sh`.
3. Keep the shared pack full-check in the chain so review preflight, install
   audit, Obsidian KB freshness, scope checks, and future shared gates still
   run.
4. Do not invoke `sd-review-pr`, a platform adapter, or
   `scripts/sd-ai-command-pack-review-full-check.sh` from the wrapper.
5. Keep the package metadata private and dependency-free. Do not introduce a
   package install step, dependency declarations, or a lockfile.
6. Preserve existing Make targets and Python-first contributor workflows.
7. Regenerate repository-map output after adding the new root configuration
   file.

## Acceptance Criteria

- [ ] The root package metadata is valid JSON, private, and defines exactly the
      intended `check` and `check:full` scripts without dependencies.
- [ ] `bash scripts/sd-ai-command-pack-review-full-check.sh` selects the
      repository-owned wrapper, runs `make check`, then runs the shared pack
      full-check with Prism and Gito disabled.
- [ ] A failing `make check` prevents the shared review workflow from reaching
      remote-review request steps.
- [ ] `make check` passes, including the checked-in Repomix freshness contract.
- [ ] `bash scripts/sd-ai-command-pack-toolchain.sh doctor` reports
      `package:check` as a candidate while leaving execution to the review
      selector.
- [ ] `make repomix` leaves `docs/repomix-map.md` synchronized with the new
      configuration.

## Out of Scope

- Changing the general SD pack project-check selection contract.
- Editing installed or vendored SD scripts to special-case this repository.
- Adding JavaScript application code, npm dependencies, or a package lockfile.
- Changing GitHub Actions or the contents of `make check`.

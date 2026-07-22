# Implement se-tutorial

## Goal

Create a reader-tested technical tutorial that leads from a defined starting
state to an observable result.

## Requirements

- Resolve audience, objective, environment, prerequisites, version scope, and cleanup needs.
- Structure incremental steps with commands/code, explanation, expected output,
  verification, failure recovery, and final validation.
- Execute examples where tools permit or label them clearly as unverified.
- Protect secrets, production systems, and destructive operations with explicit safeguards.
- Preserve version/date assumptions and cite external technical claims.

## Acceptance Criteria

- [ ] A reader can verify each major checkpoint and the final outcome.
- [ ] Untested code cannot be described as working.
- [ ] Tests cover missing prerequisites, platform differences, destructive steps, and stale APIs.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Running commands on the reader's systems or publishing the tutorial.

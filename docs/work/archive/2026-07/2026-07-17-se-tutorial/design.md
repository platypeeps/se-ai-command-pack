# Implement se-tutorial Design

## Overview

Add `se-tutorial` under Create as a checkpoint-driven technical teaching workflow
that moves a defined reader from a known starting state to an observable result.
Commands and examples are either executed in an authorized environment or labeled
unverified; safety and cleanup are part of the tutorial contract.

## Proposal

Resolve audience, objective, starting state, environment/platform, prerequisites,
version/date scope, permissions, safety constraints, expected final result, and
cleanup/rollback needs. Inventory external technical claims and verify current APIs
or versions from authoritative sources when they may have changed.

Create an outcome contract and prerequisite check before steps. Each incremental
step includes purpose, exact command/code, execution state (`verified`, `partially-
verified`, or `unverified`), expected output, checkpoint, common failure signals,
recovery, and rollback where relevant. Never imply commands ran on the reader's system.

Separate safe local examples from production/destructive operations. Protect
secrets with placeholders and explicit storage guidance. High-impact commands
require warnings, target verification, backup/rollback, and safer alternatives;
omit a command when it cannot be made responsibly executable.

End with final validation against the outcome contract, troubleshooting map,
cleanup, version/date assumptions, citations, and a tested/unverified inventory.
Optional profile use may calibrate prose and assumed expertise but cannot replace
explicit audience/prerequisite declarations.

## Boundaries And Non-Goals

- Do not run commands on the reader's systems or publish the tutorial.
- Do not call unexecuted or partially tested examples working.
- Do not expose real secrets or normalize destructive production operations.
- Do not conceal platform/version limitations.

## Affected Files

- Canonical skill, Create-family registration, technical source/safety/profile
  references, manifest, fixtures/tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Platform differences can invalidate syntax; branch explicitly by environment.
- APIs and package versions drift; date and cite the supported path.
- Expected output may contain nondeterministic values; specify stable assertions.
- Cleanup can be destructive too; verify targets and provide scoped steps.
- Missing prerequisites should stop early with actionable remediation.

## Validation

- Pin outcome/prerequisite contracts, step schema, execution labels, checkpoints,
  recovery/rollback, secret/destructive safeguards, version scope, and final validation.
- Test missing prerequisites, OS differences, stale APIs, destructive steps,
  secret-bearing examples, nondeterministic output, and unverified code.
- Run generation, focused tests, full checks, and diff check.

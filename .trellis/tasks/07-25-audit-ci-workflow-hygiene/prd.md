# CI workflow hygiene and release-script error contract

## Goal

The CI pipeline wastes less (caching, cancellation), the push lane cannot ship ungated payload, and the auto-tag script fails with its documented error contract instead of a raw traceback.

## Requirements

- Add `cache: pip` (cache-dependency-path: requirements-dev.txt) to the three setup-python steps (.github/workflows/tests.yml:28, :40, :55). [A-038]
- Add a `concurrency:` group keyed on workflow+ref with cancel-in-progress for pull requests. [A-039]
- Run check-release-payload on push to main (base = last release tag) as a prerequisite of auto-tag-release, or document that branch protection must forbid direct pushes — coordinate with 07-25-audit-release-gate-scope, which lists this as its optional stretch; implement in exactly one of the two tasks. [A-037]
- create-release-tag.py catches subprocess.TimeoutExpired and FileNotFoundError, mirroring check-release-payload.py's clean GateError-style `error:` contract. [A-014]

## Acceptance Criteria

- [ ] PR runs show pip cache hits; superseded PR runs are cancelled.
- [ ] Push-lane gating decision implemented or explicitly documented (once, without duplicating the sibling task).
- [ ] Simulated git timeout in create-release-tag.py produces the clean `error:` message and exit 1 (test).

## Notes

- Audit findings: A-038, A-039, A-037, A-014 (all P3/S) — .trellis/audit/report-2026-07-25.md.
- Evidence: .github/workflows/tests.yml:1, :28, :48, :88; .github/scripts/create-release-tag.py:21; check-release-payload.py:47.

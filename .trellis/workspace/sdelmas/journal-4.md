# Journal - sdelmas (Part 4)

> Continuation from `journal-3.md` (archived at ~2000 lines)
> Started: 2026-08-09

---



## Session 153: Ship TOCTOU fd-pinning hardening (PR #186)

**Date**: 2026-08-09
**Task**: Ship TOCTOU fd-pinning hardening (PR #186)
**Branch**: `task/08-05-audit-update-source-trust-toctou`

### Summary

Hardened install.py update source-trust gate against TOCTOU: fd-pinned SourceHandle with three-tier platform ladder, fd-relative trust checks, pinned git/exec children, symlinked .git/install.py refusals, gitdir one-hop validation (incl. directory-shape check from Copilot review). 41 module tests, make check 640 OK. PR #186 review loop converged with 14 rebuttals and 2 fix commits.

### Main Changes

- Detailed change bullets were not supplied; see the summary above.

### Git Commits

| Hash | Message |
|------|---------|
| `ba22d24` | (see git log) |
| `2b01e61` | (see git log) |
| `148920f` | (see git log) |
| `6220905` | (see git log) |

### Testing

- Validation was not recorded for this session.

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 154: sd-work-backlog run c441624d iteration 1: vendored-artifact ownership guidance (08-07)

**Date**: 2026-08-09
**Task**: sd-work-backlog run c441624d iteration 1: vendored-artifact ownership guidance (08-07)
**Branch**: `task/08-07-vendored-artifact-upstream-route`

### Summary

Recorded the vendored-artifact ownership lookup, disposition rule, and local-only record format in quality-guidelines.md; verified six classifications against real files; replaced two member tasks' constraint sections with references; converged the 08-07 PRD through two-lane adversarial review; shipped as PR #187 with one Copilot finding fixed.

### Main Changes

- Detailed change bullets were not supplied; see the summary above.

### Git Commits

| Hash | Message |
|------|---------|
| `a1c7774` | (see git log) |
| `50e27e0` | (see git log) |
| `60ca753` | (see git log) |
| `a78c3b7` | (see git log) |

### Testing

- Validation was not recorded for this session.

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 155: sd-work-backlog run c441624d iteration 2: work-loop merge-boundary disposition + relay batch (08-06)

**Date**: 2026-08-09
**Task**: sd-work-backlog run c441624d iteration 2: work-loop merge-boundary disposition + relay batch (08-06)
**Branch**: `task/08-06-work-loop-shipped-sha-after-branch-delete`

### Summary

Executed 08-06-work-loop-shipped-sha-after-branch-delete via the vendored-artifact route: four-field local-only record in PRD and quality-guidelines with the two-step evidence operator procedure; upstream relay batch filed as sd-ai-command-pack#404 and #405; PRD converged to disposition form with 3 Codex concerns addressed; shipped as PR #188 with one Copilot finding fixed.

### Main Changes

- Detailed change bullets were not supplied; see the summary above.

### Git Commits

| Hash | Message |
|------|---------|
| `19fbaf2` | (see git log) |
| `97d81a4` | (see git log) |
| `3ba2a3c` | (see git log) |

### Testing

- Validation was not recorded for this session.

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 156: Iteration 3: planning-mode finalization ordering-trap recovery guidance (PR #189)

**Date**: 2026-08-09
**Task**: Iteration 3: planning-mode finalization ordering-trap recovery guidance (PR #189)
**Branch**: `task/08-06-finalization-ordering-trap`

### Summary

Documented the sanctioned out-of-chain recovery for an sd-ship planning-mode chain stranded by a post-finalization review fix (bundle_scope_invalid): fresh sd-finish-work to a journal-only-recovery receipt, then direct sd-housekeeping --finish-work-receipt. Filed upstream relay sd-ai-command-pack#408; converged and archived task 08-06-finalization-ordering-trap.

### Main Changes

- Detailed change bullets were not supplied; see the summary above.

### Git Commits

| Hash | Message |
|------|---------|
| `9037c53` | (see git log) |
| `f66faa4` | (see git log) |

### Testing

- Validation was not recorded for this session.

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 157: Iteration 4: prism rules lane divergence guidance (PR #190)

**Date**: 2026-08-09
**Task**: Iteration 4: prism rules lane divergence guidance (PR #190)
**Branch**: `task/08-06-prism-rules-lane-divergence`

### Summary

Documented that repository prism rules in .prism/rules.json reach only the shell review lane; the sd-review lane's built-in adapter passes no --rules/--exclude/--fail-on and never reads the file. Recorded gate mechanics, per-case per-lane degradation behaviour, ownership, and the four-field record. Filed upstream relay sd-ai-command-pack#409; archived task 08-06-prism-rules-lane-divergence.

### Main Changes

- Detailed change bullets were not supplied; see the summary above.

### Git Commits

| Hash | Message |
|------|---------|
| `951e070` | (see git log) |
| `d498910` | (see git log) |

### Testing

- Validation was not recorded for this session.

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 158: Document base_branch seeding, correction window, and gate version trap

**Date**: 2026-08-09
**Task**: Document base_branch seeding, correction window, and gate version trap
**Branch**: `task/08-06-task-create-base-branch-default`

### Summary

Iteration 5 of work-loop run c441624d: local-only disposition for 08-06-task-create-base-branch-default. Added quality-guidelines subsection on task.py create base_branch seeding (installed 0.6.7), the v0.6.8 upstream fix and upgrade adoption, the set-base-branch correction deadline, detection facts, and the set-meta version-floor trap; filed relay sd-ai-command-pack#410; swept all active tasks (15/15 base_branch=main); shipped as PR #191.

### Main Changes

- Detailed change bullets were not supplied; see the summary above.

### Git Commits

| Hash | Message |
|------|---------|
| `1ebbf88` | (see git log) |
| `060d595` | (see git log) |
| `0f8367a` | (see git log) |

### Testing

- Validation was not recorded for this session.

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 159: Registry-snapshot layout-assumption assessment: no schema change

**Date**: 2026-08-09
**Task**: Registry-snapshot layout-assumption assessment: no schema change
**Branch**: `task/08-04-audit-registry-snapshot-layout-assumptions`

### Summary

Iteration 6 of work-loop run c441624d: read-only assessment for 08-04-audit-registry-snapshot-layout-assumptions. Verdicts: FIRST_PARTY_REMOTES stays consumer-owned (self-reference trust anchor); adapter paths deferred pending sd snapshot/third pack; discovery split (IGNORED_DIRECTORIES stays, per-pack roots deferred). Converged through three Codex rounds; shipped as PR #192.

### Main Changes

- Detailed change bullets were not supplied; see the summary above.

### Git Commits

| Hash | Message |
|------|---------|
| `2b03e67` | (see git log) |
| `8575f5d` | (see git log) |
| `0c08c59` | (see git log) |

### Testing

- Validation was not recorded for this session.

### Status

[OK] **Completed**

### Next Steps

- None - task complete

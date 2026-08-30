---
title: Fix sd-review coordinator nested-check false-block
status: done
created: 2026-08-04
branch: audit/review-nested-check-falseblock
---
# Fix sd-review coordinator nested-check false-block

## Goal

The `sd-review` coordinator (`scripts/sd-ai-command-pack-review.py`) must not
report deterministic-check failures that pass in every direct invocation of the
same check. During the 2026-08-04 autonomous ship of `audit-maintainer-docs-accuracy`
(PR #129), the coordinator reproducibly blocked the post-finalization
successor-head review on two checks that were, in fact, satisfied. The merge
only completed because the sd-housekeeping eligibility gate (final-bundle
receipt + GitHub CI) does not share the same nested-subprocess path.

## Evidence (2026-08-04, PR #129, head 4640a1e)

- `knowledge.obsidian-kb`: coordinator reports `copies: 470`, `expected: 471`,
  archived-task prd doc "missing", "1 stale generated entry would be removed".
- `pack.review-scope`: coordinator reports the PR body lacks a recognized
  "Tooling/generated scope:" section.
- Both PASS in every direct path, verified repeatedly and immediately adjacent
  in time:
  - `.venv/bin/python scripts/sd-ai-command-pack-update-spec-kb.py --check` -> 471, exit 0 (10/10 runs).
  - `.venv/bin/python scripts/sd-ai-command-pack-check.py --repo . --json` -> both rows `passed`.
  - Same `check.py` run through `sd-ai-command-pack-toolchain.sh run-python` -> both `passed`.
  - Same `check.py` with resolved absolute `--repo` and cwd -> both `passed`.
  - Live PR body contains the section; `review-scope.sh` regex matches it directly.
  - GitHub CI: unittest (ubuntu 3.10/3.13, macOS 3.13), lint, release-payload-gate, ci-result all SUCCESS.
- Only `review.py` -> `check.py` (doubly-nested under `toolchain.sh run-python`)
  reports the stale 470 / missing-section state, across 5 fresh attempt ids.
- `.obsidian-kb` is a directory **symlink** to an external Obsidian vault
  (outside the repo tree); the KB "copies" drift is the archived task's prd
  doc.

## Requirements

- Reproduce the divergence between direct `check.py` and `review.py`-nested
  `check.py` for both `knowledge.obsidian-kb` and `pack.review-scope`.
- Identify the environmental/cwd/nesting factor (candidate: doubly-nested
  `build_tool_environment` cache env, PR-body source, or KB symlink resolution
  under the nested subprocess) that makes the nested check see stale state.
- Make the coordinator's nested check observe the same state a direct
  invocation does, OR make these two checks deterministic across nesting depth.
- Do not weaken either check: a genuinely stale KB or a genuinely missing scope
  section must still block.

## Acceptance Criteria

- [x] A regression test reproduces the pre-fix divergence: `check.py` direct
      passes while `review.py`-nested fails on an identical live tree. Root
      cause is check-report memoization at `review.py:1796` keyed on an identity
      that excludes both checks' live inputs; fix recomputes via
      `_resolve_check`. (test: `test_review_coordinator.ResolveCheckTest.test_stale_cached_failure_is_recomputed_fresh`,
      proven to FAIL against the restored pre-fix caching, PASS after fix)
- [x] After the fix, `review.py` and direct `check.py` return identical
      pass/fail on the same tree because the report is recomputed live every
      invocation. (test: `test_nested_result_matches_direct_for_pass_and_fail`,
      `test_resume_does_not_regress_phase_or_cached_stages`)
- [x] The genuine-failure paths (stale KB, absent scope section) still block in
      both direct and nested invocation. (test: `test_genuine_failure_still_blocks`)

## Notes

- Discovered by the autonomous work-loop (run c1bc2a42) while shipping
  `audit-maintainer-docs-accuracy`. Merge of PR #129 was user-authorized past
  the false block after 5 verified-clean re-checks.
- Impact: every autonomous iteration whose finalization changes `.trellis/**`
  bookkeeping (i.e. every completed task) hits this false-block, costing a full
  investigation cycle each time.

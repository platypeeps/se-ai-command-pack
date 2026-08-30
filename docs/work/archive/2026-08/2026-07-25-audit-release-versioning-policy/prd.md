---
title: Release versioning policy and tag consistency
status: done
created: 2026-07-25
branch: task/07-25-audit-release-versioning-policy
---
# Release versioning policy and tag consistency

## Goal

Every changelog version is fetchable and version numbers carry documented meaning: no more untagged intermediate releases, and consumers can tell removals from routine minors without reading every entry.

## Requirements

- Prevent recurrence of the 0.53.0 gap: gate base→head to exactly one new changelog heading/version step per PR, or collapse intra-PR bumps before merge; record the disposition of the already-untagged 0.53.0 (backfill tag or document as never-shipped). [A-041]
- Document the bump policy in CONTRIBUTING.md: what earns patch vs minor, how removals/breaking changes are flagged (e.g. a Removed/Breaking bullet convention), and/or the 1.0 criteria. [A-042]

## Acceptance Criteria

- [x] A two-bump PR fails the release gate (test in tests/test_release_gate.py).
      `check_single_version_step` compares the branch's `## <version>` tokens
      against the merge-base and requires exactly one addition.
      `test_two_version_headings_in_one_branch_fails` covers the 0.53.0 shape;
      `test_collapsed_intra_branch_bump_passes`,
      `test_bump_reusing_a_base_heading_fails`,
      `test_correcting_an_old_entry_date_is_not_a_new_version`, and
      `test_first_changelog_import_is_not_a_multi_step` pin the other four
      arms. Falsifiability proven directly rather than assumed: the same
      two-bump repository run against the pre-change script from `HEAD` exits
      `0` ("version 1.0.0 -> 1.2.0; changelog heading matches"), and against
      the new script exits `1` ("adds 2 version headings (1.2.0, 1.1.0)").
- [x] CONTRIBUTING states the bump + breaking-change convention; changelog
      template reflects it. `CONTRIBUTING.md` gains "One version per pull
      request" and "What earns a minor versus a patch", the latter grounded in
      observed practice (`0.65.0`/`0.66.0`/`0.68.0` minors, `0.68.3` patch) and
      carrying the `**Removed:**` / `**Breaking:**` lead-bullet convention. The
      repository has no separate changelog template file, so that convention is
      shown as a worked changelog example inside the same section rather than
      duplicated into a template that does not exist.
- [x] 0.53.0 disposition recorded (tag backfilled or documented). Documented as
      never released, not backfilled — `main` went `0.52.1 -> 0.53.1` in one
      step at merge `b93e680`, so `0.53.0` existed only on PR #89's branch
      (`093809c`, re-bumped by `fcbf176`) and was never a shipped state. The
      `## 0.53.0` entry in `CHANGELOG.md` now carries that disposition.

## Notes

- Audit findings: A-041, A-042 (P3/S) — .trellis/audit/report-2026-07-25.md.
- Evidence: CHANGELOG.md:91, :129, :675; docs/SE_AI_COMMAND_PACK.md:837; .github/scripts/create-release-tag.py:57.
- Planning depth: PRD-only. Policy plus tag hygiene; no code contract changes.

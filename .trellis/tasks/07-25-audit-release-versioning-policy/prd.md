# Release versioning policy and tag consistency

## Goal

Every changelog version is fetchable and version numbers carry documented meaning: no more untagged intermediate releases, and consumers can tell removals from routine minors without reading every entry.

## Requirements

- Prevent recurrence of the 0.53.0 gap: gate base→head to exactly one new changelog heading/version step per PR, or collapse intra-PR bumps before merge; record the disposition of the already-untagged 0.53.0 (backfill tag or document as never-shipped). [A-041]
- Document the bump policy in CONTRIBUTING.md: what earns patch vs minor, how removals/breaking changes are flagged (e.g. a Removed/Breaking bullet convention), and/or the 1.0 criteria. [A-042]

## Acceptance Criteria

- [ ] A two-bump PR fails the release gate (test in tests/test_release_gate.py).
- [ ] CONTRIBUTING states the bump + breaking-change convention; changelog template reflects it.
- [ ] 0.53.0 disposition recorded (tag backfilled or documented).

## Notes

- Audit findings: A-041, A-042 (P3/S) — .trellis/audit/report-2026-07-25.md.
- Evidence: CHANGELOG.md:91, :129, :675; docs/SE_AI_COMMAND_PACK.md:837; .github/scripts/create-release-tag.py:57.

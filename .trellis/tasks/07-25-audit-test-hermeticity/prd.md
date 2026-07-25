# Test hermeticity and update e2e coverage

## Goal

`make test` passes on any contributor machine regardless of global git configuration, and the `install.py update` lifecycle — the one command that mutates the user's checkout — has a real end-to-end test.

## Requirements

- Scrub git environment in every subprocess-git test helper: GIT_CONFIG_GLOBAL=/dev/null and GIT_CONFIG_SYSTEM=/dev/null (or HOME pointed at a temp dir) — covers tests/test_release_gate.py:17 and the raw `git init` sites in tests/test_skill_review.py:904, :1238. [A-021]
- Add one update e2e in the ReleaseTagTest style: temp clone with a local bare origin one commit ahead → run install.py update → assert the pull happened and installed files refreshed. [A-022]

## Acceptance Criteria

- [ ] Suite passes with a hostile global config (e.g. commit.gpgsign=true, core.hooksPath set) simulated in CI or a dedicated test.
- [ ] The update e2e runs in CI and fails when the pull/refresh handshake breaks.

## Notes

- Audit findings: A-021 (P3/S), A-022 (P3/M) — .trellis/audit/report-2026-07-25.md.
- Evidence: tests/test_release_gate.py:17, :51; tests/test_skill_review.py:904; tests/test_management.py:108; installer/management.py:146.

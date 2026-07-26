# Harden install.py update source trust

## Goal

`install.py update` refuses to run git against, and execute install.py from, an unverified `sourceRoot` recorded in the plain-JSON provenance receipt — closing the write-one-file-to-code-execution path.

## Requirements

- Require the recorded `sourceRoot` to equal the running checkout (installer.registry.ROOT) unless the user explicitly confirms a different path (flag or interactive confirmation).
- Refuse a recorded path that is not a git repository owned by the current user.
- Keep the legitimate relocated-checkout workflow possible and documented.
- Installer behavior is consumer contract: changelog + version bump discipline applies.

## Acceptance Criteria

- [ ] Test: crafted provenance.json with a foreign sourceRoot causes a clean refusal (no git, no exec).
- [ ] Test: normal same-checkout update path unaffected.
- [ ] Docs describe the confirmation path for intentionally relocated sources.

## Notes

- Audit finding: A-017 (P2/S) — .trellis/audit/report-2026-07-25.md.
- Evidence: installer/management.py:96, :98, :190, :192, :209; install.py:324; installer/provenance.py:145.

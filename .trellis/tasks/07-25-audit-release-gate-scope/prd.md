# Widen release payload gates

## Goal

The release discipline that already exists cannot be bypassed accidentally: the local gate checks the real branch range (not just uncommitted work), and consumer-visible installer changes require the same bump + changelog discipline as skill payload.

## Requirements

- Make `make release-check` range-aware: pass `--base origin/main` (or merge-base) when the ref resolves, falling back to HEAD otherwise.
- Add install.py (exact) and installer/ (prefix) to the gated payload surface in .github/scripts/check-release-payload.py. The carve-out is diff-based: a change that leaves every shipped payload path byte-identical needs no bump. Because `installer/registry.py` (which holds `FAMILY_DESCRIPTIONS`) is now gated payload, family-description source edits DO require a bump; only metadata/catalog changes touching no shipped payload byte stay bump-free.
- Update CONTRIBUTING's release-discipline wording AND `.trellis/spec/backend/quality-guidelines.md` (rows at :157 and :172-173) to match the widened gate, since gating `installer/` changes the family-metadata bump contract.
- Optional stretch (ledger A-037): run the payload gate on push to main (base = last release tag) as a prerequisite of auto-tag-release, or document that branch protection must forbid direct pushes.

## Acceptance Criteria

- [x] When `origin/main` resolves (the normal local case), a committed payload change without a version bump fails `make release-check` locally (today it passes vacuously). Without `origin/main` the check degrades to uncommitted-only (best-effort); CI against the real PR base remains authoritative. (tests: `test_base_auto_uses_origin_main_when_present`, `test_base_auto_falls_back_to_head_without_origin`)
- [x] An installer-only behavior change without bump + changelog fails the gate (test in tests/test_release_gate.py: `test_installer_dir_change_without_bump_fails`, `test_install_py_change_without_bump_fails`).
- [x] The payload carve-out still passes — a change that leaves every shipped payload path byte-identical (no git diff) needs no bump; note that `generated/registry-snapshot.json` is itself shipped payload, so registry-metadata edits that alter it DO require a bump. CONTRIBUTING matches the enforced surface. (tests: `test_no_payload_diff_passes_without_bump`, `test_non_payload_change_passes_without_bump`)

## Notes

- Audit findings: A-035 + A-040 (both P2/S; optional A-037 P3) — .trellis/audit/report-2026-07-25.md.
- Evidence: Makefile:32; .github/scripts/check-release-payload.py:27, :176; .github/workflows/tests.yml:48, :60, :88; CHANGELOG.md:3.

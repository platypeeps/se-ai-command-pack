# Widen release payload gates

## Goal

The release discipline that already exists cannot be bypassed accidentally: the local gate checks the real branch range (not just uncommitted work), and consumer-visible installer changes require the same bump + changelog discipline as skill payload.

## Requirements

- Make `make release-check` range-aware: pass `--base origin/main` (or merge-base) when the ref resolves, falling back to HEAD otherwise.
- Add install.py and installer/ to PAYLOAD_PREFIXES in .github/scripts/check-release-payload.py, keeping the documented carve-out for registry metadata that leaves manifest.json byte-identical.
- Update CONTRIBUTING's release-discipline wording to match the widened gate.
- Optional stretch (ledger A-037): run the payload gate on push to main (base = last release tag) as a prerequisite of auto-tag-release, or document that branch protection must forbid direct pushes.

## Acceptance Criteria

- [ ] A committed payload change without a version bump fails `make release-check` locally (today it passes vacuously).
- [ ] An installer-only behavior change without bump + changelog fails the gate (test in tests/test_release_gate.py).
- [ ] The registry-metadata carve-out still passes; CONTRIBUTING matches the enforced surface.

## Notes

- Audit findings: A-035 + A-040 (both P2/S; optional A-037 P3) — .trellis/audit/report-2026-07-25.md.
- Evidence: Makefile:32; .github/scripts/check-release-payload.py:27, :176; .github/workflows/tests.yml:48, :60, :88; CHANGELOG.md:3.

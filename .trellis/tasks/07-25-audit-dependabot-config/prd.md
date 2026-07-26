# Dependency bot and audit lane

## Goal

Dependency-update PRs can actually arrive in this repo, making the dogfooded sd-update-deps triage workflow functional, and pinned toolchain deps stop aging silently.

## Requirements

- Add .github/dependabot.yml covering pip (requirements-dev.txt) and npm (.opencode/package.json), with sensible schedule and PR limits.
- Planning decision: whether to also add a scheduled pip-audit (or equivalent) CI lane for CVE visibility.
- Note: org-level Dependabot enablement could not be verified offline — confirm during implementation.
- Coordinate with ledger A-032 (the .opencode dependency may simply be removed) and A-033 (transitive pinning) rather than duplicating them.

## Acceptance Criteria

- [ ] Valid dependabot.yml in place (schema-checked); first bot PRs arrive or enablement blocker is documented.
- [ ] sd-update-deps workflow documented as the triage path for these PRs.

## Notes

- Audit finding: A-031 (P2/S) — .trellis/audit/report-2026-07-25.md.
- Evidence: requirements-dev.txt:3; .agents/skills/sd-update-deps/SKILL.md:14, :25; .github/workflows/tests.yml:31.

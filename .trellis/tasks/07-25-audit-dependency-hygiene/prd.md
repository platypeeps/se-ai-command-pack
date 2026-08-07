# Dependency hygiene for npm and transitive pins

## Goal

Every third-party fetch this repo triggers is deliberate, pinned, and reproducible — no floating packages nothing imports, no unpinned transitives, no npm lifecycle scripts running un-reviewed.

## Requirements

- Remove the unused @opencode-ai/plugin from .opencode/package.json (all .opencode JS imports node builtins only); if kept for editor types, pin exact and commit the lockfile with a written justification. [A-032]
- Compile a fully pinned (ideally hash-locked) dev requirements file (uv pip compile / pip-compile) and use it in CI and `make setup`; today 5 mypy transitives float. [A-033]
- scripts/update_repomix: add --ignore-scripts to the npx invocation, or move behind a committed package-lock + npm ci; otherwise record the accepted risk where the pattern is documented (README:463). [A-034]
- Coordinate with 07-25-audit-dependabot-config (bot + audit lane) — that task owns update automation; this one owns the pinning surface.

## Acceptance Criteria

- [ ] Opening the repo in OpenCode fetches nothing unpinned (dependency removed or locked).
- [ ] CI installs from the compiled lock; transitive drift cannot change lane behavior day to day.
- [ ] repomix refresh no longer runs arbitrary install scripts, or the risk is explicitly recorded.

## Notes

- Audit findings: A-032, A-033, A-034 (P3/S) — .trellis/audit/report-2026-07-25.md.
- Evidence: .opencode/package.json:3; .opencode/lib/session-utils.js:2; requirements-dev.txt:5; .github/workflows/tests.yml:43; scripts/update_repomix:24; README.md:463.
- Planning depth: PRD-only. Pinning and lifecycle-script review are bounded edits with no cross-layer contract. Escalate to `design.md` plus `implement.md` — the contract at `.trellis/workflow.md:164` requires both together — only if an unpinned transitive turns out to need a lockfile strategy.

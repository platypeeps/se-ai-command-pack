---
title: Dependency bot and audit lane
status: done
created: 2026-07-25
branch: audit/dependabot-config
---
# Dependency bot and audit lane

## Goal

Dependency-update PRs can actually arrive in this repo, making the dogfooded sd-update-deps triage workflow functional, and pinned toolchain deps stop aging silently.

## Requirements

- Add .github/dependabot.yml covering pip (requirements-dev.txt) with a sensible schedule and PR limit. npm coverage is deferred (see design D1): root package.json has no dependencies, and the only npm manifest with deps, .opencode/package.json, is unused and removal-pending under A-032.
- Planning decision (resolved): no scheduled pip-audit / CVE CI lane in this task — considered and deferred (four pinned dev-only deps, small blast radius); recorded in CONTRIBUTING for later revisit (see design D2).
- Enablement: this repo is not a fork, so committing dependabot.yml to the default branch enables version updates automatically — there is no separate repo toggle needed to turn them on (verified against GitHub docs + live isFork:false). They can still be suppressed by disabling Dependabot at the repository or organization level, observable only post-merge. AC1 does not depend on that post-merge observation: it is met pre-archive by the strictly-checked committed config plus CONTRIBUTING documentation. The post-merge pickup / observed-blocker check is the post-archive handoff below, not acceptance evidence (see design D6).
- Coordinate with ledger A-032 (the .opencode dependency may simply be removed) and A-033 (transitive pinning) rather than duplicating them.

## Acceptance Criteria

All criteria are satisfiable before merge/archive (the completion contract
requires every AC true before `task.py archive`; merge is post-archive).

- [x] Valid `.github/dependabot.yml` committed, passing a strict offline field
      check (every planned field/value asserted; unknown top-level keys
      rejected — see design D4), and the enablement model documented in
      CONTRIBUTING.
- [x] sd-update-deps workflow documented in CONTRIBUTING as the triage path for
      these PRs.

### Acceptance evidence

- AC1: `.github/dependabot.yml` added (version 2, pip, directory `/`, weekly,
  open-pull-requests-limit 5, `chore(deps)` prefix). Strict field check prints
  `dependabot.yml strict field check OK`. Enablement model documented in
  `CONTRIBUTING.md` → "Dependency updates".
- AC2: `CONTRIBUTING.md` → "Dependency updates" documents the `sd-update-deps`
  triage path (classify, merge the safe class through the housekeeping gate,
  park the rest), plus the npm and pip-audit deferrals.

## Post-archive handoff (not an acceptance criterion)

After the PR merges to `main`, confirm Dependabot registered the config (first
`dependabot[bot]` pip PR arrives, or the Dependabot tab shows the config with no
parse errors). If a real config error or an org-level Dependabot disablement is
then observed, record that observed blocker as a follow-up task. This runs after
archive and does not gate completion (see design D6).

## Notes

- Audit finding: A-031 (P2/S) — .trellis/audit/report-2026-07-25.md.
- Evidence: requirements-dev.txt:4-7 (the four pinned deps; lines 1-3 are comments); .agents/skills/sd-update-deps/SKILL.md:14, :25; .github/workflows/tests.yml:31.

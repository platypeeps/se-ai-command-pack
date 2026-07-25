# Repo-own tooling home and vendored-path documentation

## Goal

Contributors can tell editable repo-own source from installed vendored product at a glance, and no dead entry points linger to drift.

## Requirements

- Give repo-own tooling one documented home (e.g. tools/, or explicitly documented .github/scripts) — today 17 of 19 scripts/ files are SD-pack installs and repo-own build scripts sit in .github beside installed prompts. [A-004]
- Add a CONTRIBUTING section listing the vendored do-not-edit path families (scripts/sd-ai-command-pack-*, .github/prompts/sd-*.prompt.md, platform command/skill dirs, .trellis-owned files) and where their sources live. [A-004]
- Resolve the dead wrapper scripts/se-ai-command-pack-skill-review.py: delete it, or document + test it as the supported repo-root invocation (coordinate with 07-25-audit-lint-shipped-payload, which conditionally includes it in the lint scope). [A-026]

## Acceptance Criteria

- [ ] CONTRIBUTING distinguishes editable source from vendored installs with concrete path families.
- [ ] The wrapper is deleted or wired + tested — no unreferenced entry point remains.
- [ ] Makefile references repo-own scripts at their documented home.

## Notes

- Audit findings: A-004 (P3/M), A-026 (P3/S) — .trellis/audit/report-2026-07-25.md.
- Evidence: scripts/se-ai-command-pack-skill-review.py:1, :9; Makefile:14; CONTRIBUTING.md:1.

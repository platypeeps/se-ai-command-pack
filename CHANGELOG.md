# Changelog

## 0.1.0 - 2026-07-16

- Initial release.
- User-level installer (`install.py --user`) with manifest-driven payload,
  provenance receipts under `.se-ai-command-pack/`, anchor-gated platform
  selection (Claude Code/Cowork, OpenAI Codex, shared agents dir), plan-
  before-apply conflict detection, and vouched `--remove`.
- Six knowledge-work skills: `se-research`, `se-brief`, `se-meeting-prep`,
  `se-scan`, `se-digest`, and the pack-management skill `se-pack`.
- Shared `source-standards.md` reference fanned into every research skill.
- Generator (`make generate`) that validates canonical skills and
  regenerates the manifest; release payload gate binding payload changes to
  version bumps and dated changelog headings.

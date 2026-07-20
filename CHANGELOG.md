# Changelog

## 0.3.0 - 2026-07-20

- Add `se-decide`, a read-only decision workflow for recommendations between
  known options with explicit constraints, tradeoffs, uncertainty, reversal
  conditions, and next actions.
- Fan the shared source standards into `se-decide` and generate flat installed
  skill targets for every supported platform.
- Publish the stable outcome-family registry and generated grouped README
  catalog used by this and future skills.

## 0.2.0 - 2026-07-17

- Move pack lifecycle management into tested `install.py` commands:
  `status`, `refresh`, `update`, and `remove`.
- Preserve the convenient bare install and conventional `--version`
  interfaces while making removal command-only.
- Retire `se-pack`; normal refreshes remove its vouched installed copies now
  that lifecycle management is owned entirely by the installer CLI.

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

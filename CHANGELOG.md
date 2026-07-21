# Changelog

## 0.6.0 - 2026-07-20

- Add `se-help`, a read-only discovery and routing skill that lists families,
  explains and compares skills, recommends the smallest-fit workflow, and
  returns a copy-ready prompt without executing it.
- Generate a versioned bundled skill catalog from the same registry family
  metadata and canonical frontmatter model as the README, then fan that shared
  reference into every installed `se-help` copy.
- Distinguish bundled ownership from current availability, external and unknown
  capabilities, and version mismatch states while preserving a separate-request
  execution boundary.

## 0.5.0 - 2026-07-20

- Add `se-fact-check`, a read-only claim audit with supported, partially
  supported, unverified, contradicted, and outdated verdicts plus traceable
  evidence and minimal corrected wording.
- Move `verification-protocol.md` to one shared canonical source, fan it into
  both `se-research` and `se-fact-check`, and preserve the existing installed
  research target on every platform.
- Register the skill under Understand, align pack identity and operator
  guidance, and add focused verdict, safety, boundary, report-contract, and
  target-stability tests.

## 0.4.0 - 2026-07-20

- Add `se-status`, a read-only, objective-oriented project-status workflow that
  distinguishes outcomes from activity and surfaces current state, blockers,
  risks, recorded decisions, asks, next actions, and source gaps.
- Register `se-status` under Coordinate, fan shared source standards into every
  installed copy, and generate flat skill targets for each supported platform.
- Align pack identity and operator guidance with stakeholder-ready status
  reporting and add focused evidence, authority, boundary, and report-contract
  tests.

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

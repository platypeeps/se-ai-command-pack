# Expand skill review across user installs and repository sources

## Goal

Make `se-review-skills` discover the skills installed for the current user,
reconcile every observed copy with verified canonical repository sources, and
review each canonical skill exactly once. When the current repository owns an
installed skill, the repository template is the review and remediation target
even when the installed copy has drifted because the repository may be in the
middle of a refresh.

Also make deterministic inventories and snapshot IDs cover every
registry-mapped shared reference consumed by a selected skill, and make every
final report end with concrete next-step choices.

Review snapshot:
`4e4619ac8aab4220a5390e039393b8f58a5af36f34e44efe30be85ac498cd968`.
Finding: `1.7.9.1`.

## Requirements

- Change the canonical analyzer template
  `templates/skills/se-review-skills/scripts/skill_review.py`; update the
  portable `templates/skills/se-review-skills/SKILL.md` contract and report
  schema for installed discovery, deduplication, routing, and next steps.
- In the default review flow, scan only bounded, known user skill roots that
  exist for supported hosts. Never walk the home directory or infer another
  root from arbitrary filesystem contents.
- Support an explicit way to disable automatic installed discovery and an
  explicit repeatable installed-root override for deterministic tests and
  nonstandard hosts. Validate every override as a bounded skill root.
- Match installed copies to a local repository only through verified manifest,
  provenance, canonical-path, package-identity, and Git ownership evidence.
  A name or content similarity alone is never sufficient ownership evidence.
- When the current verified repository maps an installed target, use its
  canonical template as the review, task, and apply target whether the observed
  installed hash matches or differs. Preserve the observed hash and classify
  match versus drift without treating drift as authority to edit the install.
- When the same canonical skill appears in multiple installed roots, return one
  review record and one finding set. Preserve every install surface, observed
  path, hash, platform, drift state, and mapping evidence in that record.
- Keep unmatched installed skills reviewable as bounded evidence, but do not
  create tasks or edits unless a canonical owner repository and safe write
  boundary are independently verified.
- Resolve shared-reference membership from verified package registry metadata,
  not names, prose similarity, installed copies, or directory guessing.
- Include each selected skill's shared reference sources in related-resource
  coverage with canonical path, role, and content hash.
- Include those hashes and mappings in snapshot identity so any shared-reference
  content or membership change invalidates an earlier snapshot.
- Keep source paths bounded by the verified first-party template allowlist and
  reject missing, escaped, or symlinked shared resources.
- Preserve analyzer read-only behavior: no network access, reviewed-content
  execution, imports of untrusted package code, or filesystem writes.
- Preserve registry order and existing installed-copy, SD-adapter, target, and
  ownership behavior.
- End every review report with a `Next steps` section that names the smallest
  safe selectors or handoffs for accepted findings, drift refresh, unresolved
  ownership, unavailable roots, and a no-findings result. Suggestions never
  create tasks, edit, install, refresh, or publish implicitly.

## Acceptance Criteria

- [x] Inventorying `se-research` reports both `source-standards.md` and
      `verification-protocol.md` as canonical shared resources.
- [x] Default review inventory discovers skills from each existing supported
      user install root without scanning the whole home directory.
- [x] An explicit opt-out performs repository-only discovery, and explicit
      installed-root overrides are deterministic and boundary-checked.
- [x] Matching installed copies from multiple platforms produce one canonical
      skill record with complete per-install evidence and no duplicate finding
      surface.
- [x] A drifted installed copy still routes review and task creation to the
      verified local repository template while retaining the drift evidence.
- [x] A same-named but unverified installed skill is not silently claimed by the
      local repository and cannot create a task there.
- [x] Inventorying a skill without shared references does not acquire unrelated
      resources.
- [x] Changing a shared reference's content or registry membership changes the
      affected skill and repository snapshot IDs.
- [x] Missing, escaped, or symlinked shared-reference fixtures fail closed.
- [x] Existing SE, SD, installed-copy, pair-comparison, and no-execution
      inventory tests remain green.
- [x] Focused analyzer tests and generated-surface checks pass.
- [x] The portable report contract requires a final `Next steps` section with
      selector-ready recommendations and explicit non-execution boundaries.

## Notes

- Reproduction from the reviewed snapshot: `inventory --skill se-research`
  returned an empty `references` list and hashed only `se-research/SKILL.md`.
- Primary risk: executing or trusting repository registry code while trying to
  discover mappings. Reuse the analyzer's existing deterministic registry
  parsing boundary instead.
- A changed installed copy is evidence of drift, not a local customization that
  overrides a verified repository source during review or remediation.

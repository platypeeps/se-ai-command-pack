# Relay A-032 upstream to mindfold-ai/Trellis

## Status

**RELAYED — upstream PR filed; awaiting upstream review/merge.**

Per-PR approval record: on 2026-08-20 the maintainer explicitly approved
opening this specific upstream PR (interactive session selection "Yes, open
PR" against this task). With that approval recorded, the relay was executed
the same day: **mindfold-ai/Trellis#565**
(`sdelmas:fix/drop-unused-opencode-plugin-dep` → `mindfold-ai:main`) proposes
dropping the unused dependency by reducing the vendored template manifest to
`{}`, with the pin+lockfile alternative offered in the PR body.

Previously PARKED: the autonomous run-level authority excludes opening an
upstream Trellis pull request (`.trellis/spec/backend/quality-guidelines.md`,
"Vendored-Artifact Ownership And Upstream Route", rule 4); the per-PR approval
above is what unblocked it.

## Goal

Propose upstream the fix that audit finding A-032 identified but this
repository cannot make: `.opencode/package.json` declares
`@opencode-ai/plugin: ^1.14.39` while no `.opencode` JavaScript imports it.

The local disposition is already complete and merged (PR #197, task
`.trellis/tasks/archive/2026-08/07-25-audit-dependency-hygiene`). This task
owns only the upstream relay — the half that needs an approval that this
repository's autonomous runs do not have.

## Evidence carried forward

- **Owning pack**: upstream Trellis (`mindfold-ai/Trellis`), version `0.6.7`
  per `.trellis/.version`.
- **File**: `.opencode/package.json` — Registry A member
  (`.trellis/.template-hashes.json`, machine-local), absent from Registry B
  (`.sd-ai-command-pack/manifest.json`), `templateReceipted` in
  `.github/trellis-provenance.json`.
- **Behaviour**: every import in `.opencode/lib/*.js` and
  `.opencode/plugins/*.js` resolves to a node builtin or a sibling module, so a
  caret range is resolved and installed for a package nothing uses.
  `.gitignore:70` ignores `.opencode/node_modules/`, meaning those installs land
  inside the consumer's checkout.
- **Proposed upstream fix**: drop the dependency, or pin it exactly and ship a
  lockfile if it is kept for editor types.
- **Upstream pull request**: mindfold-ai/Trellis#565, opened 2026-08-20 with
  the per-PR approval recorded under Status above.

The full four-field record lives in
`.trellis/spec/backend/quality-guidelines.md` ("Scenario: Vendored OpenCode npm
Manifest") and in the archived task's `prd.md`.

## Acceptance Criteria

- [x] Explicit per-PR approval from the maintainer is recorded in this task
      before any upstream repository is touched. (Status section, 2026-08-20.)
- [x] An upstream pull request against `mindfold-ai/Trellis` proposes the fix,
      citing the import evidence above. (mindfold-ai/Trellis#565.)
- [x] The relay is logged the way that the precedented relays are
      (`quality-guidelines.md` cites platypeeps/sd-ai-command-pack#397, #398,
      #399 as the pattern), and the local-only record is updated to point at
      the filed PR instead of saying none was opened. (Scenario: Vendored
      OpenCode npm Manifest, field 4, updated in the same change.)

## Notes

- Do **not** edit or delete `.opencode/package.json` locally as a shortcut. A
  local removal is reverted silently by the next Trellis refresh; that failure
  mode is already recorded under Vendored Pack Lifecycle.
- Unparking is a maintainer decision, not an inference from repository
  evidence.

# PARKED: Relay A-032 upstream to mindfold-ai/Trellis

## Status

**PARKED — blocked on explicit per-PR approval for an upstream pull request.**

The autonomous run-level authority explicitly excludes opening an upstream
Trellis pull request (`.trellis/spec/backend/quality-guidelines.md`,
"Vendored-Artifact Ownership And Upstream Route", rule 4). Nothing in this task
may be implemented until the maintainer approves that specific PR.

## Goal

Propose upstream the fix that audit finding A-032 identified but this
repository cannot make: `.opencode/package.json` declares
`@opencode-ai/plugin: ^1.14.39` while no `.opencode` JavaScript imports it.

The local disposition is already complete and merged (PR #197, task
`.trellis/tasks/archive/2026-08/07-25-audit-dependency-hygiene`). This task
owns only the upstream relay — the half that needs approval this repository's
autonomous runs do not have.

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
- **No upstream pull request has been opened**, and upstream approval was not
  sought.

The full four-field record lives in
`.trellis/spec/backend/quality-guidelines.md` ("Scenario: Vendored OpenCode npm
Manifest") and in the archived task's `prd.md`.

## Acceptance Criteria

- [ ] Explicit per-PR approval from the maintainer is recorded in this task
      before any upstream repository is touched.
- [ ] An upstream pull request against `mindfold-ai/Trellis` proposes the fix,
      citing the import evidence above.
- [ ] The relay is logged the way the precedented relays are
      (`quality-guidelines.md` cites platypeeps/sd-ai-command-pack#397, #398,
      #399 as the pattern), and the local-only record is updated to point at
      the filed PR instead of saying none was opened.

## Notes

- Do **not** edit or delete `.opencode/package.json` locally as a shortcut. A
  local removal is reverted silently by the next Trellis refresh; that failure
  mode is already recorded under Vendored Pack Lifecycle.
- Unparking is a maintainer decision, not an inference from repository
  evidence.

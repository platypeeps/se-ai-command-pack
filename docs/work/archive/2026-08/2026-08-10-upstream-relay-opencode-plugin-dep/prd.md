---
title: "Relay A-032 unused @opencode-ai/plugin dependency (resolved in fork main; upstream PR #565 withdrawn)"
status: done
created: 2026-08-10
---
# Relay A-032 upstream to mindfold-ai/Trellis

## Status

**RESOLVED IN THE FORK — upstream PR withdrawn after a retarget decision.**

Per-PR approval record: on 2026-08-20 the maintainer explicitly approved
opening this specific upstream PR (interactive session selection "Yes, open
PR" against this task). With that approval recorded, the relay was executed
the same day as **mindfold-ai/Trellis#565** (proposing an empty `{}` template
manifest). Later the same day the maintainer directed the relays at the fork
the fleet actually consumes (`sdelmas/Trellis`, the source of the vendored
`0.6.16-sd.*` runtime). Fork `main` already ships the fix — the vendored
OpenCode template manifest is `{"type": "module"}` with no
`@opencode-ai/plugin` dependency — so there was nothing to retarget and
**#565 was closed with that rationale**. The defect is resolved for every
fork consumer; reopening upstream remains available if ever wanted.

**COMPLETE — verified in this repository at the 0.6.16-sd.8 refresh
(2026-08-20).** `.opencode/package.json` here is `{"type": "module"}` with no
dependency; `git log` on the path shows the fixed manifest actually arrived
with the 0.6.16-sd.1 vendored roll (#251, commit 644c560), before this task's
relay was even filed. Ledger A-032 closed as fixed in the same change; the
spec scenario's field 4 records the resolution. Task archived.

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
  the per-PR approval recorded under Status above; closed the same day after
  the retarget decision — fork `main` (`sdelmas/Trellis`) already carries the
  fix.

The full four-field record lives in
`.trellis/spec/backend/quality-guidelines.md` ("Scenario: Vendored OpenCode npm
Manifest") and in the archived task's `prd.md`.

## Acceptance Criteria

- [x] Explicit per-PR approval from the maintainer is recorded in this task
      before any upstream repository is touched. (Status section, 2026-08-20.)
- [x] An upstream pull request against `mindfold-ai/Trellis` proposes the fix,
      citing the import evidence above. (mindfold-ai/Trellis#565; withdrawn
      2026-08-20 after the maintainer retargeted the relays at the
      `sdelmas/Trellis` fork, whose `main` already ships the fix.)
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

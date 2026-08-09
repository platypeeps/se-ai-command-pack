# Fifty-nine tracked platform files lack any integrity receipt and the gitignore allowlist is fragile

## Goal

Give the `trellis init` half of the vendored platform surface the same two
properties the sd-ai-command-pack half already has: an integrity record that
can distinguish upstream content from local hand-edits, and tracking rules
that survive a re-init. Decide what is fixable locally versus routed upstream,
and record it.

## Problem

Verified 2026-08-08:

- **59 of 348 tracked platform-dot-dir files have no hash record from any
  receipt.** Two registries exist: the sd pack's
  `.sd-ai-command-pack/provenance.json` holds 202 file hashes (verified clean
  2026-08-08: 202 matching, 0 drifted, 0 missing), of which 173 are under the
  six platform dot-dirs; Trellis's `.trellis/.template-hashes.json` carries
  148 hashes of which 116 cover tracked platform paths. Union with no
  overlap: 173 + 116 = 289 covered, leaving 59 tracked platform files with no
  receipt: `.agents` 46, `.codex` 7, `.github` 6 — and some of those may be
  repo-own CI/generator files rather than Trellis output, which the inventory
  must settle. For those 59, nothing distinguishes an upstream update from a
  local hand-edit.
- **The `trellis-update-spec/SKILL.md` variance is only partially receipted.**
  It lives in three content variants across four dirs (`.agents` /
  `.claude`+`.opencode` byte-identical pair / `.github`), differing in
  invocation syntax. `.template-hashes.json` records distinct hashes for the
  OpenCode and GitHub variants — so that part of the variance is upstream-
  intended and detectable — but the `.agents` copy is among the unreceipted
  59, where drift would be invisible.
- **`.claude/` tracking rests on a fragile hand-written allowlist.**
  `.gitignore` uses `.claude/*` with targeted re-includes for `sd-*` skills
  only: the 9 `.claude/skills/trellis-*/` dirs are ignored while `.agents`,
  `.opencode`, and `.github` track theirs. A fresh clone reproduces the sd
  surface but not the Claude trellis surface. CONTRIBUTING.md:99-104
  documents the sharper failure mode — re-running `trellis init` re-asserts a
  wholesale `.claude/` ignore, silently hiding every adapter — and notes the
  durable upstream fix has not landed.
- **`.gitignore` is itself a pack install target without a receipt.** It
  appears in `.sd-ai-command-pack/installed-targets.txt` (it carries a
  generated `trellis-gitignore` block) but is absent from `provenance.json`,
  so a pack reinstall rewriting it — including clobbering the hand-written
  allowlist that sits above the generated block — trips no integrity check.
- **Surface asymmetry with no stated reason:** `trellis-start` exists as a
  skill only in `.agents/skills` with a command twin only in
  `.opencode/commands`; no `.claude`, `.gemini`, or `.github` surface at all.
  (`trellis-continue`/`trellis-finish-work` have twins elsewhere.)

Not in scope as a question: whether `.claude/skills/trellis-*` should be
tracked. That was decided by the user on 2026-08-04 (archived task
`07-25-audit-claude-gitignore-owner`: track sd adapters only, other `.claude`
skills stay ignored) and is published policy in CONTRIBUTING.md:89-103. This
task takes the asymmetry as accepted and addresses only its durability.

## Requirements

- **Inventory first.** Rebuild the uncovered-file inventory from both
  ownership registries (`provenance.json` union `.template-hashes.json`)
  and classify each of the ~59 remainder paths as Trellis output, repo-own,
  or other. Only positively-identified Trellis output is in scope for a
  receipt.
- **Integrity record.** Decide and record how the unreceipted Trellis-output
  files get one: an upstream request that `trellis init` write provenance the
  way the sd installer does, a repo-local checksum record generated from the
  current known-good state, or an explicit "accepted: these files are
  unverifiable" statement. If local, the record must be regenerable and
  checkable by a command a gate could run.
- **Gitignore durability.** Record the defense for the allowlist: at minimum a
  check (local gate or CI) that fails when tracked `.claude` adapter paths
  become ignored again, since the known trigger (`trellis init` re-run) is
  outside this repo's control. Add `.gitignore` to whatever integrity record
  exists, or record why it stays exempt.
- **Variant + orphan disposition.** For the unreceipted `.agents` copy of
  `trellis-update-spec`, the ignored-by-policy `.claude` copy (also in
  neither receipt — disposition or explicitly exempt it without reopening the
  settled tracking decision), and the `trellis-start` orphan: classify each
  as intended (record where) or defect (route upstream). No local edits to
  the vendored files themselves.
- Upstream-routable items follow the contract from
  `08-07-vendored-artifact-upstream-route` once it lands. This task is not
  yet enrolled in that task's canonical instance table; enrollment, with its
  derived-count reconciliation, happens per that task's own contract at
  routing time, not by this filing.

## Acceptance Criteria

- [ ] A written disposition covers the four in-scope areas (inventory
      classification, integrity record, gitignore durability, variant/orphan
      classification), each with its chosen route.
- [ ] If a local checksum manifest is chosen: running its check command on a
      clean tree passes, and modifying one covered file by hand makes it
      fail; both demonstrated, not asserted.
- [ ] If the gitignore check is implemented: `git check-ignore` on a tracked
      `.claude` adapter path is exercised by the check, and the check fails
      when a wholesale `.claude/` ignore is simulated.
- [ ] The count of tracked platform-dot-dir files uncovered by the union of
      both registries is re-enumerated at completion and either reduced to
      zero or explicitly accepted with the number and classification stated.

## Out of scope

- Changing upstream Trellis or sd-ai-command-pack themselves — proposals
  only, via the routing contract.
- The sd-covered 202 files (already receipted and verified clean) and the
  116 template-hashed Trellis paths (already receipted).
- Reopening the `.claude` tracking-asymmetry decision (settled 2026-08-04,
  archived task `07-25-audit-claude-gitignore-owner`).
- Content review of the trellis skills — this task is about integrity
  machinery, not what the skills say.

## Notes

- Sourced from the 2026-08-08 deep review (duplication/overlap lane). File
  counts and the provenance verification (202/202 clean) are from that run;
  re-enumerate before acting.
- The unreceipted `.agents` copy of `trellis-update-spec` is the concrete
  exhibit for why the gap matters: two sibling variants (OpenCode, GitHub)
  are hash-receipted in `.template-hashes.json`, while the `.agents` copy and
  the untracked-by-policy `.claude` copy are receipted nowhere.
- Adversarial review (2026-08-08) corrected the original premise: the first
  filing claimed 175 unreceipted files, having missed
  `.trellis/.template-hashes.json` as a second registry; the union-based
  count is 59, and the tracking-symmetry question was cut as already decided.
- Lightweight; PRD-only unless the local-manifest route is chosen and grows a
  generator — then add design.md before start.

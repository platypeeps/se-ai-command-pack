# Sixty tracked platform files lack any integrity receipt and the gitignore allowlist is fragile

> Count in the title updated from fifty-nine by the 2026-08-09 re-measurement
> below; the original 2026-08-08 figures remain in the Problem section as the
> filing-time record.

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

- [x] A written disposition covers the four in-scope areas (inventory
      classification, integrity record, gitignore durability, variant/orphan
      classification), each with its chosen route. — The "Chosen routes"
      list under Re-measurement, converged through three adversarial review
      rounds plus host-lane closures.
- [x] If a local checksum manifest is chosen: running its check command on a
      clean tree passes, and modifying one covered file by hand makes it
      fail; both demonstrated, not asserted. — Demonstrated 2026-08-09 in a
      disposable detached worktree of commit 68f6017: clean tree exit 0
      ("trellis-provenance check: ok (54 hashed, 352 tracked platform files
      covered)"); after appending a byte to the `.agents`
      `trellis-update-spec` skill, exit 1 with "drifted:
      .agents/skills/trellis-update-spec/SKILL.md". Also demonstrated:
      registry-absent CI parity (exit 0 with no
      `.trellis/.template-hashes.json` in the worktree) and `--write`
      byte-stability (`cmp` byte-identical after regeneration).
- [x] If the gitignore check is implemented: `git check-ignore` on a tracked
      `.claude` adapter path is exercised by the check, and the check fails
      when a wholesale `.claude/` ignore is simulated. — Same worktree:
      appending `.claude/` to `.gitignore` produced exit 1 with 59
      `ignored-tracked-path` findings (every tracked `.claude` path) plus
      "drifted: .gitignore". The assertion uses `--no-index` with exact
      exit-status mapping; both are locked by
      `tests/test_trellis_provenance.py` (24 tests, all passing).
- [x] The count of tracked platform-dot-dir files uncovered by the union of
      both registries is re-enumerated at completion and either reduced to
      zero or explicitly accepted with the number and classification stated.
      — Re-enumerated on the shipped tree: 351 tracked dot-dir files,
      original-union uncovered = 62, explicitly accepted and fully
      classified (46 `.agents` + 7 `.codex` receipted in the manifest; 9
      `.github` repo-own: the 6 CI/release files, the PR template, and the
      new checker + manifest). The checker's four-set coverage metric is 0
      uncovered ("352 tracked platform files covered", including
      `.gitignore`), enforced continuously by `make check`, sd-check, and
      the release-payload-gate CI job.

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

## Re-measurement (2026-08-09, execution session)

Fresh enumeration before acting, per the Notes requirement. Corrections to
the 2026-08-08 figures:

- **Uncovered count is 60, not 59.** 349 tracked files under the six platform
  dot-dirs; the registry union covers 289; uncovered = 60: `.agents` 46,
  `.codex` 7, `.github` 7 (the earlier count had `.github` 6). The
  `.trellis/.template-hashes.json` reader must use the v2 schema (hashes
  nested under a `"hashes"` key); reading it flat under-counts coverage.
- **`.github` classification:** 6 of the 7 are repo-own (added by this repo's
  release/CI commits, absent from `installed-targets.txt`):
  `.github/dependabot.yml`, `.github/workflows/tests.yml`,
  `.github/scripts/generate-skill-surfaces.py`,
  `.github/scripts/aggregate-ci-result.py`,
  `.github/scripts/check-release-payload.py`,
  `.github/scripts/create-release-tag.py`. The 7th,
  `.github/PULL_REQUEST_TEMPLATE.md`, is a
  pack install target (`installed-targets.txt:132`) absent from
  `provenance.json`, as is `.gitignore` (`installed-targets.txt:155`) — but
  see the next bullet: both absences are intentional upstream, so the
  template is classified repo-own (user-tunable), not
  pack-installed-unreceipted.
- **The remaining 53 (46 `.agents` + 7 `.codex`) are Trellis init output**:
  all added by the Trellis init commit `ef34a2b` and unmodified since. All 53
  are in scope for a receipt.
- **The variant picture confirms the original filing: three distinct
  contents across four copies.** `trellis-update-spec` hashes (sha256 first
  8): `.agents` `003ce08a` (unique, unreceipted), `.claude` == `.opencode`
  `d975db7a` (receipted via the OpenCode entry; the `.claude` copy is
  untracked by policy), `.github` `e37452de` (receipted).
- **The pack-provenance omissions are intentional, not upstream defects.**
  Upstream pack source (`installer/provenance.py:88`) deliberately excludes
  force-preserved targets and `.gitignore` from provenance, and
  `PULL_REQUEST_TEMPLATE.md` is force-preserved (`installer/registry.py:1951`)
  — i.e., user-tunable after install. No upstream issue is warranted for
  either. Consequence: `PULL_REQUEST_TEMPLATE.md` is classified repo-own
  (user-tunable), not pack-installed-unreceipted; `.gitignore` is hashed
  locally as an explicit durability policy, not as a defect remedy.

**Chosen routes** (the written disposition the first AC requires):

1. **Inventory:** 53 Trellis-output files (46 `.agents` + 7 `.codex`) in
   scope for a receipt; 7 `.github` files classified repo-own and excluded —
   the 6 CI/release files (git history is their integrity record) plus
   `PULL_REQUEST_TEMPLATE.md` (force-preserved by the pack, user-tunable).
   Local receipt covers 54 files: the 53 plus `.gitignore` (explicit local
   durability policy).
2. **Integrity record:** a repo-local checksum manifest generated from the
   current known-good state, checked by a repo-own generator/checker script;
   both live under the repo-own `.github` area (exact prospective paths and
   schema are in `design.md`, which owns forward-looking detail). The
   manifest is
   self-contained for CI: `.trellis/.template-hashes.json` is gitignored and
   untracked, so the manifest snapshots that registry's covered-path list
   and the checker consults the live registry only when present locally.
   Wiring: a guard-safe check registered in `.sd-ai-command-pack/check.json`
   (repo-customizable registration file — tracked, absent from
   `installed-targets.txt` and `provenance.json`), a `make` target on the
   `check:` chain, and an explicit CI step in the `release-payload-gate`
   job (a release prerequisite via `auto-tag-release`/`ci-result` `needs`).
   An upstream request (that `trellis init` write provenance the way the sd
   installer does) is recorded as routable via
   `08-07-vendored-artifact-upstream-route`; the local manifest is the
   defense until that lands. Per the Notes rule this route grows a
   generator, so `design.md` is added before start.
3. **Gitignore durability:** the same check script asserts every tracked
   `.claude` path is not ignored — `git check-ignore --no-index` must exit
   nonzero for each (`--no-index` is required: without it Git suppresses
   ignore reporting for tracked paths and the assertion is vacuous) — so a
   re-run of `trellis init` re-asserting a wholesale `.claude/` ignore fails
   the gate. `.gitignore` itself is hashed in the manifest.
4. **Variant/orphan:** each case classified per the requirement's
   intended-or-defect binary. The `.agents` `trellis-update-spec` divergent
   content and the `trellis-start` skill/command asymmetry are classified
   **suspected upstream defects** — unmodified init output proves origin,
   not intent, and no upstream contract demonstrating intent was found —
   and both are routed upstream as questions via the
   `08-07-vendored-artifact-upstream-route` contract at routing time
   (recorded locally now; Trellis upstream is external, no filing under
   current authority). Both files are receipted in the manifest meanwhile,
   so any further drift is visible. The `.claude` `trellis-update-spec`
   copy is explicitly exempt: untracked by settled policy, so no
   tracked-content receipt can apply to it.

**AC4 metrics, stated up front:** shipping the script and manifest adds two
tracked `.github` files, so the original two-registry-union uncovered count
becomes 62 at completion — explicitly accepted, every path classified above
(53 receipted Trellis output, 7 + 2 repo-own including the new checker and
manifest). The checker's own four-set coverage metric (union plus manifest
`files`/`repoOwn`/snapshot) must be zero on the shipped tree. Both numbers
are reported at completion.

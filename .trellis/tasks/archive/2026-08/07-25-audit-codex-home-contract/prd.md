# Resolve CODEX_HOME contract drift

## Goal

README, operator guide, and installer agree on whether the codex platform honors `$CODEX_HOME`. Today README.md:360 promises it, docs/SE_AI_COMMAND_PACK.md:927 denies all env reads, and the installer hard-codes `.codex/skills`.

## Requirements

- Decide: implement `$CODEX_HOME` resolution in platform selection, or retract the README claim.
- If implemented: resolve the codex row's skills_dir/anchor through `CODEX_HOME` when set, with a test covering a relocated home.
- If retracted: remove the "(honors `$CODEX_HOME`)" parenthetical, document the `--root`/symlink workaround, and regenerate derived surfaces (repomix map).
- Either way, the operator guide's environment-variables statement must remain true.

## Decision (2026-08-04, user-approved)

Resolve by **retracting** the README claim, not implementing `$CODEX_HOME`.
Rationale: code is the source of truth — `installer/registry.py` hard-codes the
codex row (`.codex/skills`/`.codex`), no code path reads `$CODEX_HOME`, and the
operator guide (`docs/SE_AI_COMMAND_PACK.md`) already states "No environment
variables are read". The README parenthetical is the lone incorrect outlier.
Implementing resolution would add unshipped consumer-facing behavior and, per
the cross-program note, double the codex-surface contract question — out of
scope for a consistency fix. Retract keeps this lightweight and low-risk. This
selects the "retract" branch already enumerated in Requirements/AC.

## Acceptance Criteria

- [x] The hand-authored sources — README.md, docs/SE_AI_COMMAND_PACK.md,
      install.py, installer/ — carry only mutually consistent `$CODEX_HOME`
      statements (codex reads a fixed `~/.codex`; no env resolution).
- [x] README documents the relocation workaround (`install.py --root` /
      symlink `~/.codex`) in place of the retracted claim.
- [x] Changelog entry (consumer-visible contract).

### Deferred / out of scope (planning review, C-1 / C-2)

- `docs/repomix-map.md` embeds a packed copy of the README table (line ~23355)
  and of the audit report/ledger text. It is a generated repomix snapshot that
  is **not** freshness-gated (`make check` does not verify it) and is refreshed
  in bulk at version-refresh time — it is already ~28 commits stale on `main`.
  A full `make repomix` regen here would fold ~28 commits of unrelated repo
  drift into an A-044 doc fix (and trip the pr-body/review-scope gates), so the
  map regen is **deferred** to the next scheduled bulk `make repomix` refresh,
  which will pick up the corrected README table automatically. The grep-
  consistency AC above therefore scopes to hand-authored sources, excluding the
  generated `docs/repomix-map.md` snapshot and the historical `.trellis/audit/`
  records (which correctly describe the pre-fix drift).

## Notes

- Audit finding: A-044 (P2/S) — found independently by 4 reviewers; see .trellis/audit/report-2026-07-25.md.
- Evidence: README.md:360, installer/registry.py:61, docs/SE_AI_COMMAND_PACK.md:927.

## Cross-program coordination (2026-07-25 review)

- Resolve BEFORE (or within the design gate of) `07-25-agent-artifact-kind`: that task
  ships a second codex surface (agent rows on the codex anchor), doubling the scope of the
  CODEX_HOME contract question if it is still open.

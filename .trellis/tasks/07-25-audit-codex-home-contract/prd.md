# Resolve CODEX_HOME contract drift

## Goal

README, operator guide, and installer agree on whether the codex platform honors `$CODEX_HOME`. Today README.md:360 promises it, docs/SE_AI_COMMAND_PACK.md:927 denies all env reads, and the installer hard-codes `.codex/skills`.

## Requirements

- Decide: implement `$CODEX_HOME` resolution in platform selection, or retract the README claim.
- If implemented: resolve the codex row's skills_dir/anchor through `CODEX_HOME` when set, with a test covering a relocated home.
- If retracted: remove the "(honors `$CODEX_HOME`)" parenthetical, document the `--root`/symlink workaround, and regenerate derived surfaces (repomix map).
- Either way, the operator guide's environment-variables statement must remain true.

## Acceptance Criteria

- [ ] `grep -r CODEX_HOME README.md docs/ install.py installer/` shows only mutually consistent statements (and code, if implemented).
- [ ] If implemented: test proves skills land under a relocated `$CODEX_HOME`.
- [ ] Changelog entry (consumer-visible contract).

## Notes

- Audit finding: A-044 (P2/S) — found independently by 4 reviewers; see .trellis/audit/report-2026-07-25.md.
- Evidence: README.md:360, installer/registry.py:61, docs/SE_AI_COMMAND_PACK.md:927.

## Cross-program coordination (2026-07-25 review)

- Resolve BEFORE (or within the design gate of) `07-25-agent-artifact-kind`: that task
  ships a second codex surface (agent rows on the codex anchor), doubling the scope of the
  CODEX_HOME contract question if it is still open.

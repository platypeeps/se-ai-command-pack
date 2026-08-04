# Fix .claude dogfood tracking conflict

## Goal

Make the Claude-platform dogfood state reproducible: a fresh clone either contains the receipt-claimed `.claude/*` surfaces or the receipts stop claiming them. One owner decides `.claude/` tracking policy.

## Decision (user, 2026-08-04)

Option (a): track the sd-ai-command-pack Claude adapters, reaching parity with the
21 tracked `.gemini/commands/sd/*` twins. Local-only third-party skills under
`.claude/skills/` stay ignored. See `design.md`.

## Generator ownership (verified 2026-08-04)

Neither rule source is vendored in this repo (grep for the block strings across
`installer/`, `scripts/`, `.trellis/scripts/`, root `*.py` returns zero hits):

- `.gitignore:27` `.claude/` is emitted by the external **`trellis init`** binary.
- The `# sd-ai-command-pack trellis-gitignore` managed block (`.gitignore:55-197`)
  is emitted by the external **`sd-ai-command-pack` installer`**; its `.claude/**`
  rules (`:92-98`) are already narrow and symmetric with `.gemini` — not the
  conflict. This repo's own `install.py` never rewrites `.gitignore`.

The sole conflict is the external `trellis init` wholesale `.claude/`. Durable
oscillation-proofing requires an upstream change to that binary, which is out of
this repo-local task's scope and is recorded as a separate follow-up task.

## Requirements

- Resolve the conflict so the receipt-claimed `.claude/*` sd-adapters are tracked
  (parity with the 21 tracked `.gemini/commands/sd/*` twins).
- Record the ownership decision where contributors will find it (`CONTRIBUTING.md`).
- File a follow-up task for the upstream `trellis init` change (make it treat
  `.claude` like `.gemini`: narrow rules, no wholesale ignore).

## Acceptance Criteria

- [ ] `git check-ignore .claude/commands/sd/start.md` no longer matches (adapters
      tracked); a local-only skill (e.g. `.claude/skills/caveman/SKILL.md`) is
      still ignored (no over-capture).
- [ ] `scripts/sd-ai-command-pack-install-audit.py` reports no missing-target
      failures/warnings for the `.claude/*` targets.
- [ ] In-repo stability: this repo's `install.py` does not rewrite `.gitignore`
      (verified), so the sd-pack side does not oscillate. The `trellis init` side
      is documented in `CONTRIBUTING.md` and tracked as a follow-up; it cannot be
      enforced in-repo against an external binary. (AC re-scoped 2026-08-04 from
      the original "re-running both generators leaves `.gitignore` stable", which
      assumed both generators were in-repo — they are not.)

## Notes

- Audit finding: A-001 (P2/S) — .trellis/audit/report-2026-07-25.md, ledger.md.
- Evidence: .gitignore:27, .gitignore:92-98, .sd-ai-command-pack/installed-targets.txt, scripts/sd-ai-command-pack-install-audit.py:489.
- Receipt now claims 59 `.claude/*` targets (report said 21 on 2026-07-25); finding valid, scope grew.

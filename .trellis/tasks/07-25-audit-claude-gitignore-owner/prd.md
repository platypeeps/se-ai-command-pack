# Fix .claude dogfood tracking conflict

## Goal

Make the Claude-platform dogfood state reproducible: a fresh clone either contains the receipt-claimed `.claude/*` surfaces or the receipts stop claiming them. One owner decides `.claude/` tracking policy.

## Requirements

- Resolve the conflict between the Trellis rule `.gitignore:27` (`.claude/`) and the SD-pack managed block re-includes (`.gitignore:92-95`).
- Either (a) narrow the Trellis rule so the managed re-includes work (parity with the 21 tracked `.gemini/commands/sd/*` twins), or (b) make the SD install stop claiming `.claude` targets and drop them from `.sd-ai-command-pack/installed-targets.txt`.
- The two generators (Trellis init and `install.py`) must stop re-asserting opposite rules on refresh.
- Record the ownership decision where contributors will find it.

## Acceptance Criteria

- [ ] `git check-ignore .claude/commands/sd/start.md` no longer contradicts the receipts (tracked, or no longer claimed).
- [ ] `scripts/sd-ai-command-pack-install-audit.py` reports no missing-target failures on a fresh clone.
- [ ] Re-running both generators leaves `.gitignore` stable (no oscillation).

## Notes

- Audit finding: A-001 (P2/S) — .trellis/audit/report-2026-07-25.md, ledger.md.
- Evidence: .gitignore:27, .gitignore:92-95, .sd-ai-command-pack/installed-targets.txt, scripts/sd-ai-command-pack-install-audit.py:489.

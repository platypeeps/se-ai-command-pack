# Repomix map policy decision

## Goal

One deliberate policy for the 1 MB generated docs/repomix-map.md (currently ~45% of history weight, freshness enforced only by a manual chore): either stop committing it, or gate its freshness automatically.

## Requirements

- Decide (planning gate): (a) gitignore the map and generate on demand via `make repomix` — preferred by the audit; or (b) keep committing it and add a `--check` drift mode wired into the local full-check path.
- Update .trellis/spec/backend/quality-guidelines.md:1130 and the README section to match the chosen policy.
- Verify consumers (sd-update-spec reads it "when present"; install-audit already excludes it) keep working under the chosen policy.
- Option (a) may note that history rewrite is a separate, later decision.

## Acceptance Criteria

- [x] Chosen policy implemented; no silent-drift state remains possible.
- [x] Spec + README updated consistently; `make repomix` behavior documented.
- [x] Consumers verified working (sd-update-spec path exercised or reasoned in the task).

## Notes

- Audit finding: A-025 (P2/M, merged bloat+improvements) — .trellis/audit/report-2026-07-25.md.
- Evidence: docs/repomix-map.md:1; .trellis/spec/backend/quality-guidelines.md:1130; scripts/sd-ai-command-pack-install-audit.py:246; tests/test_repomix.py:89-97.

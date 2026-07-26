# Canonical workflow entry points per platform

## Goal

One canonical entry point per workflow per platform: agents following the routing docs cannot silently bypass the SD wrappers' added recording and gating steps by invoking the wrapped trellis commands directly.

## Requirements

- Decide the mechanism: the SD install amends the agent-routing doc (AGENTS.md Trellis-managed block) to name the sd:* wrappers as canonical, or the install suppresses/shadows the duplicated trellis:* command surface on each platform.
- Apply consistently across all installed platforms (both command sets currently ship side by side everywhere).
- Coordinate ownership with the Trellis-managed block (same two-owners theme as 07-25-audit-claude-gitignore-owner).

## Acceptance Criteria

- [ ] Routing documentation names exactly one canonical entry point per workflow; the non-canonical path is absent or explicitly marked as bypassed-behavior.
- [ ] Session-record behavior no longer diverges by entry point (verified for finish-work).

## Notes

- Audit finding: A-005 (P3/S) — .trellis/audit/report-2026-07-25.md.
- Evidence: AGENTS.md:13; .agents/skills/sd-finish-work/SKILL.md:11; .gemini/commands/sd/finish-work.toml:1.

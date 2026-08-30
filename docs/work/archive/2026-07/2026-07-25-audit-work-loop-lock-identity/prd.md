---
title: Fix work-loop stale-lock recovery race
status: done
created: 2026-07-25
---
# Fix work-loop stale-lock recovery race

## SUPERSEDED — moved upstream to sd-ai-command-pack (2026-07-25)

These findings (A-012) target vendored SD-pack scripts; the fix belongs in the
sd-ai-command-pack source repository. Tracked there as
`.trellis/tasks/07-25-fix-work-loop-lock-race` since 2026-07-25. The SE-side audit ledger entries
carry notes pointing upstream; the vendored copies in this repo refresh through
the normal pack update rollout — no separate SE-side work remains.

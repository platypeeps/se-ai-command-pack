# Watchlist State Sentinel Terminology Implementation Plan

1. Add failing contract pins for caller-specific acceptance, cross-rejection,
   and shared-reference neutrality.
2. Update the shared state reference and canonical watchlist skill without
   broadening either strict argument surface.
3. Preserve version-1 state shape, first-baseline behavior, recovery boundaries,
   and pending-item semantics.
4. Bump release metadata, generate twice, run focused tests, `make check`, and
   the full review gate.
5. Capture the reusable contract in Trellis specs and complete the single
   PR-through-merge lifecycle.

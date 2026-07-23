# Deterministic Monitor-State Staleness Implementation Plan

1. Add failing contract pins for the explicit-policy, continuity-gap, fresh,
   and no-policy branches.
2. Define one deterministic staleness decision rule in the shared state schema
   without adding caller-specific arguments.
3. Make `se-monitor` apply that rule before selecting its comparison branch and
   preserve all existing recovery and qualified-comparison boundaries.
4. Bump release metadata, regenerate supported targets twice, and run focused
   tests plus `make check` and the full review gate.
5. Capture any durable contract in Trellis specs and complete the single
   PR-through-merge lifecycle.

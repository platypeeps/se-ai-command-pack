# Deterministic Monitor-State Staleness Design

## Overview

The monitor currently names a readable state as stale without defining the
decision rule. That leaves identical state vulnerable to different recovery
branches based on an unstated age judgment. The state schema is shared with
`se-watchlist`, so the rule must describe caller policy and source continuity
without changing either skill's argument surface.

## Proposal

- Treat a readable version-1 state as stale only when an explicit caller
  freshness policy is violated or a source-specific continuity failure leaves
  the requested comparison interval unrecoverable from the recorded boundary.
- Treat age alone as metadata when no freshness horizon was supplied; it does
  not select the stale branch.
- Keep source-specific dates, coverage, comparison boundaries, and gaps
  visible. A stale state permits only qualified comparison and never converts
  non-observation into resolution.
- Preserve the distinct absent/new, malformed, unsupported-version, and fresh
  comparison branches.

## Validation

Focused contract coverage will pin explicit-policy stale, continuity-gap
stale, fresh, and no-policy behavior in both the monitor skill and shared state
reference. Generation parity, the release gate, and the full repository check
must remain green.

# Watchlist State Sentinel Terminology Design

## Overview

The shared state reference currently names only `baseline=new`, although
`se-watchlist` exposes the strict `checkpoint=new` argument. The reference must
describe first-state creation without implying that either caller accepts the
other caller's argument name.

## Proposal

- Describe the shared behavior as a caller-specific explicit new-state
  sentinel rather than a universal argument.
- State that `se-monitor` uses `baseline=new` and `se-watchlist` uses
  `checkpoint=new`.
- Make the sentinels non-interchangeable and preserve both skills' strict
  unknown-argument stop rules.
- Preserve the version-1 schema, first-baseline behavior, per-source recovery,
  pending items, and all state-validation branches.

## Validation

Focused contract coverage will pin both accepted names, both cross-rejections,
caller-neutral shared wording, and unchanged recovery semantics. Generation,
release, and full repository gates must remain green.

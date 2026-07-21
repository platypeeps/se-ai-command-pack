# Implement se-monitor

## Goal

Add a read-only monitoring workflow based on explicit baselines, meaningful-change thresholds, dated deltas, and a framework-neutral persistence and scheduling contract.

## Background

`se-brief` provides a current snapshot, but recurring monitoring needs an
explicit baseline and must report only meaningful change since the prior run.
Persistence and scheduling capabilities differ by platform, so the portable
contract must be designed before implementation.

## Requirements

- Define monitor subject, source scope, baseline, cadence or comparison window,
  and meaningful-change thresholds.
- Compare current evidence to the explicit prior baseline and separate new,
  changed, unchanged, resolved, and unverifiable items.
- Date every delta and preserve source quality/confidence signals.
- Define a framework-neutral state artifact or context contract, including
  behavior when prior state is missing, unreadable, stale, or incompatible.
- Keep scheduling optional and capability-based; report when the current
  platform cannot persist state or create recurring runs.
- Remain read-only and never subscribe, notify, or mutate external systems
  without separate authorization.
- Define boundaries from `se-brief`, `se-status`, and `se-research`.

## Acceptance Criteria

- [ ] The skill can produce a first baseline and a later delta report with
      deterministic handling of missing or stale prior state.
- [ ] Unchanged information is summarized rather than repeatedly presented as
      new.
- [ ] The design remains usable without a specific automation product or
      connector.
- [ ] Safety rules prohibit implicit subscriptions, notifications, and external
      writes.
- [ ] Skill validation, generated surfaces, documentation, release metadata,
      and full pack checks pass.

## Out of Scope

- Shipping a background daemon or scheduler.
- Platform-specific automation adapters in the initial skill.
- Alert delivery without explicit user authorization.

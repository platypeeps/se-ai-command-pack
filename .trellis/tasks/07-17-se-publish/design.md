# Implement se-publish Design

## Overview

Add `se-publish` under Create as a read-only adaptation workflow for an already
approved source artifact. It preserves semantic and evidentiary traceability while
producing destination-appropriate drafts and previews; it does not discover the
underlying synthesis or publish anything itself.

## Proposal

Require source artifact, audience, destination format, objective, tone, constraints,
and optional `profile=auto|off|locator`. Inventory source version, load-bearing
claims, citations, required nuance, sensitive content, approved omissions, and
unsupported gaps. Make inferred audience/tone choices visible for confirmation.

Support capability-neutral drafts for Slack message/canvas, Notion page, internal
memo, announcement, briefing, and YouTube outline. Apply a destination contract
covering length, hierarchy, scanability, calls to action, link/citation affordances,
accessibility, and confidentiality. Preserve meaning; label material omissions,
compression, reordered context, changed terminology, and proposed additions.

Do not add promotional certainty or unsupported claims. Profile use may adapt
voice within outward-safe scope, with current instructions and destination norms
taking precedence; never inject private-only details or personal claims. Return
source/destination metadata, draft, adaptation ledger, citation check, sensitivity
check, preview, and connector-ready handoff.

Direct sending or publication requires a separate explicit write request and a
fresh preview in the connector-specific workflow.

## Boundaries And Non-Goals

- Do not send, publish, schedule, manage social media, or create media assets.
- Do not replace `se-digest`; the source synthesis must already be accepted.
- Do not introduce unsupported promotional claims or silently drop citations.
- Do not expose private profile or source content to a broader destination.

## Affected Files

- Canonical skill, Create-family registration, source/profile/safety references,
  manifest, destination fixtures/tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Tight limits can force loss of nuance; surface an omission ledger or refuse unsafe compression.
- Destination norms may conflict with accessibility or evidence requirements; evidence wins.
- Sensitive internal content may be inappropriate for the requested audience.
- Citation formats may not transfer directly; preserve linkable provenance.
- A stale source artifact must not be presented as current without verification.

## Validation

- Pin required source/audience/objective, destination contracts, adaptation ledger,
  citation retention, outward-safe profile scope, preview, and read-only behavior.
- Test tight limits, citation retention, destination mismatch, sensitive content,
  stale source, unsupported promotion, profile leakage, and write requests.
- Run generation, focused tests, full checks, and diff check.

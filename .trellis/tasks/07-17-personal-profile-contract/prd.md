# Design the personal profile integration contract

## Goal

Define a portable, privacy-preserving contract for a user-owned personal
operating profile and for the outward-facing SE skills that may consume it.

## Background

The profile is intended to improve papers, articles, presentations, proposals,
and generated communications by preserving the user's voice, values,
preferences, expertise, goals, and boundaries. It must not become a hidden
psychological dossier, a source of fabricated personal claims, or a mechanism
for leaking private evidence into public outputs.

## Requirements

- Define one Markdown profile schema with stable sections for identity terms the
  user chooses to share, values, goals, expertise, interests, working and
  communication preferences, voice/style evidence, decision patterns, audience
  modes, boundaries, active hypotheses, contradictions, and revision history.
- Define audience overlays as sparse overrides on the base profile rather than
  duplicated personas. Initial examples should cover technical peers,
  executives, public writing, close collaborators, and private reflection while
  allowing user-defined audiences. Each overlay records purpose, audience,
  applicable channels, tone/structure preferences, disclosure boundaries, and
  its own provenance/freshness metadata.
- Define overlay selection explicitly: a user-specified overlay wins; otherwise
  use a unique audience/channel match; ambiguous or missing matches fall back to
  the base profile and are disclosed. Overlays cannot weaken privacy,
  confidentiality, factual-integrity, or explicit current-instruction rules.
- Require every durable profile assertion to include provenance, evidence date,
  confidence, scope, and status. Distinguish `explicit`, `observed`, and
  `inferred`; inferred traits remain proposed until approved.
- Define scopes such as `private-only`, `internal`, and `outward-safe`. Private
  source material must never be quoted or exposed merely because a derived
  preference is usable in outward communication.
- Define precedence: current explicit instructions override profile settings;
  audience/purpose constraints override general style preferences; confirmed
  profile entries override hypotheses; absence of a profile yields transparent
  defaults rather than blocking ordinary work.
- Define profile discovery without embedding a personal path in the public
  skill. An explicit invocation path or private configuration may locate the
  Obsidian note; Notion is the fallback when Obsidian is unavailable.
- Define connector-neutral read, preview, write, preservation, conflict, and
  read-back behavior. Do not add credentials or personal locations to the pack.
- Define which outward-facing skills consume the contract, initially including
  `se-author`, `se-paper`, `se-proposal`, `se-presentation`, `se-publish`,
  `se-technical-editor`, and communication-producing Coordinate skills.
- Profile-aware skills must disclose material profile assumptions, avoid
  inventing personal experience/opinions, and permit an explicit `profile=off`
  or equivalent per invocation.
- Define privacy-safe testing using synthetic profiles only.
- Define an on-demand and optionally scheduled review contract that reports
  proposed additions, changed evidence, stale entries, contradictions,
  overgeneralizations, audience-overlay drift, unused entries, and deletion or
  consolidation candidates. Review produces a preview and never applies
  changes without the same approval rules as ordinary maintenance.

## Acceptance Criteria

- [ ] The artifact is readable and editable by the user without special tooling.
- [ ] Every assertion has provenance, confidence, scope, status, and freshness.
- [ ] Sensitive or protected attributes are neither inferred nor stored without
      explicit user direction.
- [ ] Outward-facing outputs can use preferences without exposing private source
      text or presenting inferred experience as fact.
- [ ] Explicit current instructions and audience needs have documented precedence.
- [ ] Audience overlays are sparse, traceable, explicitly selected or safely
      matched, and cannot override privacy or factual-integrity constraints.
- [ ] Periodic review identifies stale, contradictory, overgeneralized, unused,
      and audience-specific entries without silently rewriting the profile.
- [ ] Missing, stale, conflicting, or unreachable profiles have safe behavior.
- [ ] Obsidian-primary and Notion-fallback persistence remains connector-neutral
      and requires verified read-back after writes.
- [ ] Consumer skills and their required tests/docs are enumerated.

## Out of Scope

- Clinical or psychometric assessment, manipulation, identity prediction,
  employee evaluation, surveillance, or automated reputation scoring.
- A hosted profile service, cross-user profile, secret store, or public profile
  directory.

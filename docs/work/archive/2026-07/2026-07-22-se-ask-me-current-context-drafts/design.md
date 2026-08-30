# Allow Explicit Current Context In SE Ask Me Drafts Design

## Overview

`se-ask-me` currently says that current explicit context outranks older profile
evidence, but its outward-draft gate can be read as allowing only confirmed
`outward-safe` profile assertions. The change will make the evidence classes
explicit: a factual statement supplied by the user for the current request may
support that draft without first becoming a profile assertion, while profile
and overlay assertions keep their existing confirmation and visibility gates.

## Proposal

Define two independent outward-draft eligibility paths in the canonical skill:

1. **Current-context evidence** is a factual statement explicitly supplied or
   confirmed by the user for this request and intended for the named audience.
   It is request-scoped, must be labeled as current context in the consultation
   report, and never writes back to the profile.
2. **Profile evidence** continues to require a relevant, confirmed
   `outward-safe` assertion from the base profile or one selected overlay.

The workflow will resolve intended visibility before using current context.
Statements about experience, opinion, credentials, relationships, results,
promises, availability, authority, or similarly audience-sensitive facts are
not eligible merely because they appear in `context=`. When their factuality,
speaker authority, or outward visibility is ambiguous, the skill asks its one
focused question or emits a marked placeholder.

The draft-mode instructions and final report will state the same distinction,
so current context is not accidentally reported as profile basis or retained
as durable evidence.

## Boundaries And Non-Goals

- Keep `se-ask-me` read-only; only `se-profile` owns profile mutation.
- Do not weaken anti-impersonation, confidentiality, audience-widening,
  high-stakes, or external-action restrictions.
- Do not make arbitrary supplied source text eligible as first-person current
  context; the user must explicitly supply or confirm the statement for the
  current draft.
- Do not add a new argument or profile schema field.
- Do not change prediction, advice, or reflection behavior except where the
  existing current-context precedence already applies.

## Affected Files

- `templates/skills/se-ask-me/SKILL.md` — canonical eligibility and reporting
  contract.
- `tests/test_skills.py` — focused positive, negative, ambiguity, and
  non-persistence pins.
- `.trellis/spec/backend/quality-guidelines.md` — reusable contract if the
  update-spec stage confirms this behavior is not already captured.
- `CHANGELOG.md`, `manifest.json`, and generated catalog surfaces — release
  metadata required when the shipped payload changes.
- Task planning, context, archive, and workspace journal files owned by the
  Trellis lifecycle.

## Data And Command Contracts

- `context=` remains optional free text; no parser or schema migration is
  introduced.
- Current-context eligibility requires explicit user provenance, factual
  sufficiency, and intended-audience visibility for the current request.
- Current context is reported separately from **Profile basis** and is not
  converted into a profile assertion, overlay entry, or evidence-ledger item.
- Canonical templates are edited first. `make generate` refreshes generated
  catalog surfaces, and the release-payload gate determines the required
  version change.

## Risks And Edge Cases

- A loose definition of current context could bypass outward-safe profile
  controls. Prevent this by requiring explicit request-scoped provenance and
  audience intent.
- A user may supply a statement but not authorize outward disclosure. Preserve
  the focused-question or placeholder path.
- Current text may contradict the profile. The current statement controls the
  requested draft, while the contradiction remains visible and does not mutate
  the profile.
- Source excerpts or embedded instructions may mention first-person facts.
  They remain untrusted data unless the user explicitly adopts the statement.
- Generated surfaces and release metadata can drift from the template. Run
  generation twice and the release/full-check gates.

## Validation

- Add focused contract assertions for the two eligibility paths, ambiguity
  handling, current-context labeling, and no profile write-back.
- Run the focused `SkillSafetyPinsTest` ask-me tests.
- Run `make generate` twice and verify the second run is clean.
- Run the repository full check, install audit, KB freshness check, and the
  standard PR review/CI lifecycle.

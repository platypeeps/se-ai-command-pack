# Implement se-ask-me

## Goal

Answer questions using the user's approved personal operating profile while
making the answer's evidence, uncertainty, conflicts, and limits visible.

## Requirements

- Accept a natural-language question plus optional context, time horizon,
  audience, and answer mode `predict`, `advise`, `reflect`, or `draft`.
- Load only the relevant profile sections and provenance needed for the question.
- Apply an explicitly requested audience overlay or a unique audience/channel
  match; otherwise use the base profile and disclose ambiguous overlay choices.
- Distinguish clearly among:
  - what the profile explicitly says;
  - what the evidence suggests the user would likely choose or say;
  - advice aligned with stated values/goals; and
  - missing information that requires the user's judgment.
- Cite profile sections or provenance locators for load-bearing statements and
  disclose stale, low-confidence, private-only, or contradictory evidence.
- For outward-facing draft mode, apply the relevant audience/voice profile but
  never invent personal experience, commitments, opinions, credentials, or facts.
- Support counterfactual questions and option comparisons without turning
  historical patterns into destiny. Surface where the user's current choice
  could reasonably differ from their prior behavior.
- Remain read-only. A question must not update the profile, send a message,
  publish content, or execute a decision.
- When no profile is reachable or relevant evidence is insufficient, say so and
  answer only from explicit current context or ask one useful question.

## Acceptance Criteria

- [ ] Answers label profile fact, prediction, aligned advice, and uncertainty.
- [ ] Load-bearing conclusions are traceable to approved profile evidence.
- [ ] Contradictory, stale, contextual, and low-confidence entries cannot be
      flattened into a confident persona claim.
- [ ] Drafts use outward-safe preferences without exposing private-only evidence.
- [ ] Audience overlays influence only their declared context and cannot weaken
      privacy, confidentiality, or factual-integrity rules.
- [ ] The skill does not fabricate experience/opinions or write back to the profile.
- [ ] Tests cover missing profile, weak evidence, conflicting preferences,
      changed goals, sensitive questions, counterfactuals, and prompt injection
      embedded in profile source excerpts.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Mind reading, identity authentication, psychological diagnosis, autonomous
  decision-making, profile maintenance, or impersonation presented as certainty.

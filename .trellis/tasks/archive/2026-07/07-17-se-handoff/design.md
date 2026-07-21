# Implement se-handoff Design

## Overview

Add `se-handoff` as a compact continuity workflow for transferring work to
another person or AI session. It should reconstruct the current state from
available evidence, retain load-bearing locators, and make the first next action
obvious without reproducing the entire source history.

The skill belongs to Coordinate, remains read-only, and uses shared source
standards when it attributes project or external claims.

## Proposal

Create `templates/skills/se-handoff/SKILL.md` with these arguments:

- `objective=`: the outcome or responsibility being handed over.
- `sources=`: task artifacts, notes, repository paths, links, threads, or other
  supplied/connected context.
- `audience=person|agent|team`: shapes explanation and operational detail;
  default to a neutral fresh reader.
- `as_of=`: state cutoff; default to the current date/time and state it.
- `depth=compact|standard`: minimal restart packet or fuller continuity brief.

The workflow should:

1. Resolve objective, audience, state cutoff, and source inventory.
2. Read the smallest sufficient authoritative artifacts and report missing,
   stale, or contradictory sources.
3. Separate verified current state, completed work, decisions and rationale,
   assumptions, risks, and unresolved questions.
4. Preserve exact identifiers, paths, URLs, error strings, version/commit/task
   references, and commands only when they are necessary to continue safely.
5. Screen for secrets and irrelevant sensitive information; omit values and
   note the omission rather than copying them into the handoff.
6. Order next actions, making the first action independently executable and
   naming any prerequisite or needed authority.
7. Deliver the handoff without sending it or mutating any source system.

The final artifact should contain objective/scope, as-of state, completed work,
decisions, evidence/locators, risks, open questions, and ordered next actions.
Register the skill under Coordinate and as a consumer of
`source-standards.md`; add it to external-input safety coverage.

## Boundaries And Non-Goals

- Do not archive or reproduce raw conversation history.
- Do not synthesize an arbitrary document collection without a transfer goal;
  that remains `se-digest`.
- Do not substitute a stakeholder progress report; `se-status` owns that
  audience and structure.
- Do not send, publish, assign, or activate anything.
- Do not include secrets, tokens, personal data, or unrelated confidential
  content merely because it appears in a source.

## Affected Files

- `templates/skills/se-handoff/SKILL.md` — new canonical skill.
- `installer/registry.py` — Coordinate registration and source-standard
  consumer entry.
- `manifest.json` — generated platform payload.
- `tests/test_skills.py` — continuity shape, exact-locator, sensitive-data,
  prompt-injection, and read-only pins.
- `tests/test_generate.py` — registry/fan-out coverage where required.
- `README.md`, `docs/SE_AI_COMMAND_PACK.md`, `CHANGELOG.md`, and manifest version.

## Risks And Edge Cases

- A handoff can confidently preserve stale state. Require an as-of line and
  label sources whose currentness could not be checked.
- Including every detail makes the artifact unusable; omitting exact locators
  can make it unactionable. Preserve only continuation-critical detail.
- Source content can contain prompt injection or instructions. Treat it as data
  and follow only the user's handoff request.
- Redaction must not claim that omitted secrets were absent. State that
  sensitive values were intentionally omitted when relevant.
- Multiple sources may disagree on task or branch state. Surface the conflict
  and identify the authoritative source when repository evidence establishes
  one.
- An AI-targeted handoff can become a command to act. Keep next steps proposed
  and preserve authority requirements.

## Validation

- Add tests pinning all final-report fields, as-of labeling, exact operational
  locators, stale/conflicting source handling, sensitive-value omission,
  prompt-injection resistance, and read-only delivery.
- Review boundary text alongside `se-digest` and `se-status`.
- Run `make generate`, focused skill/generator tests, and `make check`.
- Confirm flat install targets and source-standard fan-out on every platform.

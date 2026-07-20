# Implement se-fact-check Design

## Overview

Add `se-fact-check` as a claim-led audit workflow. Unlike `se-research`, which
starts from an open question, this skill starts from a supplied artifact or
claim list, inventories material assertions, verifies them individually, and
returns a traceable verdict ledger.

The existing verification protocol should become a shared canonical reference
consumed by both `se-research` and `se-fact-check`. Its installed target under
`se-research/references/verification-protocol.md` must remain unchanged.

## Proposal

Create `templates/skills/se-fact-check/SKILL.md` with these arguments:

- `input=`: supplied file, link, transcript, draft, or attached artifact;
  required unless explicit `claims=` are present.
- `claims=`: an explicit subset or standalone list of assertions to audit.
- `scope=material|all`: default `material`; audit conclusion-changing and
  decision-relevant claims rather than every harmless statement.
- `as_of=`: date against which time-sensitive claims should be judged; default
  to the current date and state it.
- `format=ledger|memo`: claim-by-claim table or a forwardable audit memo.

Use exactly five verdicts:

- `supported`: evidence supports the claim as written.
- `partially supported`: a narrower or qualified version is supported.
- `unverified`: available evidence cannot establish the claim.
- `contradicted`: stronger credible evidence conflicts with the claim.
- `outdated`: the claim was once supportable but is no longer current.

The workflow should inventory and normalize claims before searching, distinguish
fact-checkable assertions from opinion/prediction, apply the claim ladder,
consult primary evidence where available, capture dates and locators, and offer
minimal corrected wording for partial, contradicted, or outdated claims. It
must not silently rewrite the whole input.

Move
`templates/skills/se-research/references/verification-protocol.md` to
`templates/skills/_shared/references/verification-protocol.md`, then register
both `se-research` and `se-fact-check` as consumers. The generator already fans
a shared reference basename into each consumer's `references/` directory, so
the installed `se-research` path remains stable while `se-fact-check` gains the
same protocol. Register both source standards and verification protocol for the
new skill. Generalize only the protocol's research-brief-specific introductory
wording so the shared source truth accurately covers both research reports and
claim audits; keep its claim ladder, passes, and failure behavior unchanged.

## Boundaries And Non-Goals

- Do not answer a broad research question; route that to `se-research`.
- Do not synthesize several documents into one position; route that to
  `se-digest` unless the request is explicitly to audit their claims.
- Do not treat opinion, rhetoric, or forecasts as binary factual assertions.
- Do not perform general copy-editing or publish a corrected document.
- Do not infer the contents of inaccessible, paywalled, or corrupted sources.

## Affected Files

- `templates/skills/se-fact-check/SKILL.md` — new canonical skill.
- `templates/skills/se-research/references/verification-protocol.md` — moved to
  the shared reference location.
- `templates/skills/_shared/references/verification-protocol.md` — shared
  canonical protocol after the move.
- `installer/registry.py` — skill/family registration and two shared-reference
  consumer sets.
- `manifest.json` — regenerated skill/reference fan-out.
- `tests/test_skills.py` — verdict, safety, protocol, and boundary pins.
- `tests/test_generate.py` — shared-reference source/target stability coverage.
- `README.md`, generator/manifest identity, `docs/SE_AI_COMMAND_PACK.md`,
  `CHANGELOG.md`, and manifest version `0.5.0`.

## Risks And Edge Cases

- Moving the protocol source can accidentally delete the installed research
  copy. Pin the unchanged target path in generator tests.
- One sentence can contain several independently verifiable claims. Split them
  without losing the original locator.
- A claim can be technically true but misleadingly broad. Use `partially
  supported` and explain the missing qualification rather than forcing a binary
  verdict.
- Time-sensitive claims need an explicit `as_of` date; otherwise `outdated`
  cannot be assessed consistently.
- Conflicting credible sources should remain visible. Do not collapse them into
  a stronger verdict than the evidence permits.
- Corrected wording can drift into authorship. Limit it to the smallest change
  needed to match evidence.

## Validation

- Add a generator test proving the shared verification protocol targets both
  skills and preserves the existing research target.
- Add skill tests pinning all five verdict names, material-claim inventory,
  primary-source preference, dates/locators, minimal correction, prompt-
  injection resistance, and read-only behavior.
- Run `make generate` and review the source-path change plus target stability.
- Run focused skill/generator tests and then `make check`, including the release
  payload/version gate.

# Preserve Unverified Claims In Evidence Audits Design

## Overview

The shared verification protocol currently permits an unverifiable
load-bearing claim to be dropped. That is appropriate only as a publication
boundary: an unsupported claim must not appear as an asserted conclusion. It
is unsafe for a claim audit, where dropping the claim also removes the evidence
gap and makes the audit ledger incomplete.

## Proposal

Separate two outcomes in the shared protocol:

1. Every evaluated claim remains traceable in the claim or evidence-gap ledger
   with its status and missing evidence.
2. An unverified load-bearing claim is excluded from conclusions,
   recommendations, and other output that would assert it as established.

`se-fact-check` will state this audit-specific consequence directly: every
audited factual claim receives exactly one verdict, including unsupported
load-bearing claims. The final report will keep the claim in both the complete
claim ledger and the evidence-gap view without allowing it to support the
summary conclusion.

## Shared-Task Coordination

The planned `se-shared-evidence-claim-sensitive` task also owns
`verification-protocol.md`, but its scope is corroboration and freshness. This
task changes only failure handling and audit completeness. It preserves the
current two-source rule verbatim so the later task can revise that rule on top
of an already-complete ledger contract without conflict.

## Boundaries And Non-Goals

- Do not change the five fact-check verdicts or their meanings.
- Do not weaken source tiers, corroboration, disconfirmation, conflict,
  inaccessible-source, or confidence requirements.
- Do not treat `unverified` as evidence for a conclusion.
- Do not rewrite or publish the user's artifact.
- Change canonical templates first, then regenerate installed surfaces.

## Affected Files

- `templates/skills/_shared/references/verification-protocol.md` — separate
  ledger retention from conclusion exclusion.
- `templates/skills/se-fact-check/SKILL.md` — make complete audit handling
  explicit in workflow, safety, and report contracts.
- `tests/test_skills.py` — focused positive and negative contract pins.
- Release metadata and generated catalog surfaces when required by the payload
  gate.

## Risks And Edge Cases

- “Preserve” could be misread as “repeat in the conclusion.” Pin explicit
  exclusion from conclusions and recommendations.
- “Every claim” could accidentally include rhetoric or opinion in factual
  verdict totals. Keep non-fact-checkable items visible but separately typed.
- A shared protocol used by non-audit skills still needs a practical omission
  boundary. Allow omission from asserted narrative while retaining the claim
  in an evidence-gap or verification record.
- Later claim-sensitive corroboration work must not overwrite this failure
  contract. Keep the edits narrowly separated by section.

## Validation

- Add a focused test that pins complete-ledger retention, `unverified`, the
  evidence gap, and conclusion exclusion in both canonical resources.
- Run focused fact-check contract tests and shared-reference installation
  checks.
- Run generation twice, the release payload gate, `make check`, the full review
  check, GitHub CI, and direct review-thread inspection.

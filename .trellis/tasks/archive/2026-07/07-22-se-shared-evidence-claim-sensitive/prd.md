# Make shared evidence rules claim-sensitive

## Goal

Make the shared evidence contract sensitive to the kind of claim being
evaluated. Preserve conservative dating, corroboration, disconfirmation, and
failure handling without automatically treating every source older than twelve
months as stale or every dispositive claim as unverified without two sources.

Review snapshot:
`4e4619ac8aab4220a5390e039393b8f58a5af36f34e44efe30be85ac498cd968`.
Findings: `1.1.1`, `1.1.2`.

## Requirements

- Change only the canonical evidence templates:
  - `templates/skills/_shared/references/source-standards.md`;
  - `templates/skills/_shared/references/verification-protocol.md`.
- Define freshness relative to claim volatility, applicable version or period,
  supersession, and any explicit domain horizon. Stable historical or immutable
  primary evidence must not become stale solely because twelve months elapsed.
- Continue to date mutable facts and visibly bound evidence to the version,
  jurisdiction, environment, or period it actually covers.
- Permit one authoritative primary record to support a load-bearing claim only
  when that record is dispositive for the narrowly stated claim and its
  applicability is verified.
- Continue to require corroboration and disconfirmation for empirical,
  interpretive, disputed, surprising, or interested-party claims. Do not turn a
  vendor assertion into a dispositive record merely because it is first-party.
- Preserve the existing source tiers, independence checks, conflict handling,
  inaccessible-source behavior, calibrated confidence, and honest unverified
  path.
- Add focused behavior pins for both accepted exceptions and conservative
  negative cases, then regenerate and verify every target surface.

## Acceptance Criteria

- [ ] A stable historical or immutable primary source is not labeled stale only
      because it is older than twelve months.
- [ ] An old mutable fact is labeled stale or inapplicable when its explicit or
      domain-appropriate freshness horizon has expired.
- [ ] A single dispositive authoritative record can support its exact bounded
      claim with visible date and applicability.
- [ ] Empirical, disputed, interpretive, and interested-party claims still
      require independent corroboration or remain visibly low-confidence or
      unverified.
- [ ] Existing conflict, disconfirmation, inaccessible-source, and no-evidence
      behavior remains intact.
- [ ] Focused skill tests, generated-surface checks, and the release-payload gate
      pass.

## Notes

- Primary risk: wording the authoritative-record exception too broadly and
  weakening evidence quality. Tests must distinguish dispositive records from
  self-serving claims.
- This is one package-wide shared-reference task rather than duplicate tasks for
  every consuming skill.

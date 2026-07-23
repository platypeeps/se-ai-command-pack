# Claim-Sensitive Shared Evidence Design

## Overview

The shared evidence references currently treat age and source count as broad
proxies for applicability. That over-classifies stable records as stale and
understates when one authoritative record is actually dispositive, while a
broad exception could also weaken empirical and disputed-claim verification.

## Proposal

- Determine freshness from claim volatility, the applicable version or period,
  supersession evidence, and any explicit domain horizon. Age alone is not a
  stale signal for immutable or stable historical evidence.
- Bound mutable claims to a visible date, jurisdiction, version, environment,
  or period and mark them stale or inapplicable when their relevant horizon or
  applicability has expired.
- Permit one authoritative primary record only for a narrowly stated claim
  where the record is legally, operationally, or mechanically dispositive and
  its identity and applicability are verified.
- Retain independent corroboration and disconfirmation for empirical,
  interpretive, disputed, surprising, or interested-party claims.

## Boundaries

- Do not weaken source tiers, independence checks, conflict handling,
  inaccessible-source behavior, calibrated confidence, or the unverified path.
- Do not treat a first-party vendor assertion as dispositive merely because it
  is primary.
- Keep the public contract in the two canonical shared references and pin both
  accepted exceptions and conservative negative cases in focused tests.

## Risks And Validation

The principal risk is ambiguous wording that allows convenience to masquerade
as dispositive authority. Tests must distinguish immutable history from mutable
facts, official records from interested assertions, and exact bounded claims
from empirical or interpretive conclusions. Generation, release, and full
repository gates must remain green.

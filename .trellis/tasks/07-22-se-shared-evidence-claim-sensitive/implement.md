# Claim-Sensitive Shared Evidence Implementation Plan

1. Start the feature branch and load the two canonical evidence references,
   their consuming contract tests, and backend quality guidance.
2. Add failing focused pins for volatility-aware freshness, dispositive
   authoritative records, and conservative corroboration counterexamples.
3. Rewrite the freshness and verification rules in both shared references with
   explicit applicability, supersession, independence, and disconfirmation
   boundaries.
4. Bump release metadata, generate twice, and run focused tests, `make check`,
   and the full review gate.
5. Capture any reusable evidence-contract rule in Trellis specs, then complete
   the single PR-through-merge lifecycle.

## Review Notes

- Freshness is claim-sensitive, not a universal clock.
- A dispositive record supports only the exact claim within its authority.
- Empirical, disputed, interpretive, surprising, and interested-party claims
  remain corroboration-sensitive.
- Failure and inaccessible-source paths must stay conservative and visible.

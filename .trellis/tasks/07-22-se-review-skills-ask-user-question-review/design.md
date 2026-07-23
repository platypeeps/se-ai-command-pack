# Skill-Review Interaction Design Assessment

## Overview

`se-review-skills` evaluates authority, safety, failures, and portability but
does not explicitly detect workflows that should request structured user input.
The review must distinguish a necessary decision or approval from keywords,
discoverable facts, safe defaults, and optional preferences.

## Proposal

- Add interaction design to the capability ledger and semantic rubric.
- Classify structured input as required, useful but non-blocking, or
  inappropriate based on whether an unresolved choice materially affects
  scope, authority, output, cost, side effects, or an accepted preference.
- Name Claude `AskUserQuestion`, require a verified platform equivalent when
  available, and preserve a concise direct-question fallback without adding
  host-only canonical metadata.
- Require each finding to identify the decision, blocking state, smallest
  instruction change, prompt shape, fallback, nonresponse behavior, and
  validation. Do not force option lists for free-form input.
- Keep review mode read-only and semantic judgment outside the analyzer.

## Validation

Focused contract tests will pin positive, negative, keyword-only, option,
free-form, fallback, and mutation-boundary behavior. Generation parity, release
checks, and the full repository gate must remain green.

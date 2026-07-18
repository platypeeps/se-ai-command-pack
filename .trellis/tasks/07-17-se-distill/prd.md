# Implement se-distill

## Goal

Condense a supplied topic or source corpus to approximately 10% of its original
size while retaining at least the most decision-relevant 80% of its informational
value for a stated audience and purpose.

## Background

“80% of important information” is a prioritization target, not an objectively
measurable universal guarantee. The skill must operationalize importance through
the user's purpose, audience, decisions, and required invariants, then disclose
material losses and uncertainty.

## Requirements

- Accept a topic plus sources, or a supplied corpus; do not invent a topic
  treatment from unsupported background knowledge.
- Resolve audience, purpose, target length/ratio, must-keep facts, and tolerance
  for omitted examples, history, nuance, or implementation detail.
- Build an importance map before compression: thesis, conclusions, decisions,
  constraints, causal structure, strongest evidence, risks, exceptions, and actions.
- Target output at no more than 10% of measured source words/tokens by default;
  report actual ratio and request relaxation when required invariants cannot fit.
- Preserve attribution and distinguish source claims from synthesis.
- Include a loss ledger naming omitted categories, contested points, and details
  that could change a decision.
- Support executive, study, decision, and technical distillation modes without
  duplicating `se-digest`, which reconciles sources at normal useful length.

## Acceptance Criteria

- [ ] Output states source size, output size, compression ratio, audience, and purpose.
- [ ] A traceable importance map controls what survives compression.
- [ ] Thesis, decisions, constraints, strongest evidence, major risks, and
      decision-changing exceptions cannot be silently dropped.
- [ ] When 10% is unsafe, the skill explains why and offers a smallest-safe result
      rather than falsely claiming the target was met.
- [ ] A loss ledger lets the reader judge whether to consult the full source.
- [ ] Tests cover short sources, conflicting sources, technical material,
      citation retention, impossible ratios, and prompt injection.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Lossless compression guarantees, replacing source material, or unrestricted research.

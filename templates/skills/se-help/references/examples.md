# SE Help Examples

Use these examples to demonstrate routing and handoffs. The generated catalog,
not this file, remains authoritative for bundled skill ownership.

## Family prompts

- **Understand**: `$se-help goal="Audit the factual claims in this draft and preserve their original locations."` routes to `$se-fact-check`.
- **Decide**: `$se-help goal="Recommend one of these three known vendors using our constraints and evidence."` routes to `$se-decide`.
- **Create**: `$se-help goal="Turn this approved technical brief into an audience-specific slide story with source traceability."` routes to `$se-presentation`.
- **Coordinate**: `$se-help goal="Report project outcomes, blockers, risks, decisions, and next actions since Friday."` routes to `$se-status`.
- **Operate**: `$se-help mode=tour` introduces the pack and its current availability labels.
- **Improve**: `$se-help goal="Review this technical draft for correctness, citations, structure, and voice before revision."` routes to `$se-technical-editor`.

## Common comparisons

- `$se-help mode=compare skills=se-research,se-digest` distinguishes open evidence gathering from supplied-corpus synthesis.
- `$se-help mode=compare skills=se-brief,se-status` distinguishes topic updates from objective-oriented project reporting.
- `$se-help mode=compare skills=se-scan,se-decide` distinguishes candidate discovery from choosing among known options.

## Workflow handoffs

### Evidence to decision

1. `$se-research` produces a sourced evidence brief.
2. `$se-decide` consumes that brief plus known options, criteria, and constraints to produce a recommendation.

### Corpus to decision

1. `$se-digest` produces a decision-ready synthesis with disagreements surfaced.
2. `$se-decide` consumes the synthesis and explicit alternatives to produce a recommendation.

### Meeting preparation to status

1. `$se-meeting-prep` produces a dossier, talking points, and questions.
2. After the meeting, `$se-status` consumes recorded outcomes and project sources to produce an objective-oriented update.

Each handoff is a separate request. Help recommends the sequence but never runs
either stage.

## Ambiguous and unavailable requests

- "Help me understand this" is ambiguous between `$se-research`, `$se-digest`, and `$se-fact-check`; ask one question about whether the user wants new evidence, synthesis of supplied material, or a claim audit.
- An unknown or externally provided skill is labeled external or unknown, never bundled merely because its name resembles `$se-help`.
- A bundled skill missing from the current capability inventory is labeled included in the installed pack but not discoverable now; report observed versions and use the native status/update path without guessing the cause.

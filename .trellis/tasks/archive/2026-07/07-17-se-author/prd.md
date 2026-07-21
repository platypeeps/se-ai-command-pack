# Implement se-author

## Goal

Add the primary interactive workflow for developing a thematic prompt or a
ranked topic suggestion into an original, evidence-backed technical article.

## Requirements

- Accept an optional theme, audience, format, objective, and target length.
- When no theme is supplied, invoke or reproduce the `se-topic-radar` contract
  and present ten ranked opportunities before authoring begins.
- Test the selected idea for audience value, timeliness, defensible thesis,
  firsthand contribution, novelty, and available evidence.
- Conduct an adaptive interview one high-value question at a time; challenge
  vague claims and preserve the user's answers separately from generated prose.
- Obtain approval for an editorial brief containing thesis, audience, reader
  outcome, original contribution, evidence needs, format, length, and tone.
- Maintain a durable, resumable workspace for brief, interview, evidence ledger,
  outline, draft, and review state without requiring a specific storage tool.
- Draft in explicit passes: skeleton, substantive draft, voice, compression,
  reader comprehension, and integrity.
- Review technical correctness, citations, novelty, objections, confidentiality,
  structure, and voice before producing a publication handoff.
- Reuse `se-research`, `se-fact-check`, `se-distill`, `se-technical-editor`, and
  `se-publish` rather than duplicating their deeper contracts.

## Acceptance Criteria

- [ ] Both supplied-theme and no-theme entry paths converge on an approved brief.
- [ ] The interview asks one question at a time and records original contribution.
- [ ] Research cannot silently replace the approved thesis or author perspective.
- [ ] A resumed session can identify its last approved checkpoint and artifacts.
- [ ] The final package includes article, title options, summary, evidence state,
      adaptation suggestions, and follow-up ideas without publishing automatically.
- [ ] Tests cover weak themes, insufficient originality, unsupported claims,
      resume behavior, sensitive material, and prompt injection.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Research-paper methodology, direct publication, or impersonating an authorial
  experience the user did not provide.

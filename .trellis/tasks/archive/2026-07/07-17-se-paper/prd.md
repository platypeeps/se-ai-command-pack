# Implement se-paper

## Goal

Guide development of a credible research paper from question selection through
literature review, method, evidence, analysis, limitations, and submission-ready draft.

## Requirements

- Accept an optional research theme, question, field, intended contribution,
  venue, methodology constraints, evidence/data, and citation style.
- When no question is supplied, use the topic-radar contract but rank candidates
  for researchability, contribution, evidence access, ethics, feasibility, and novelty.
- Conduct a one-question-at-a-time interview to refine research question,
  hypotheses where appropriate, contribution, scope, method, and validity threats.
- Require an approved research brief and literature-search protocol with source
  inclusion/exclusion criteria before claiming review completeness.
- Maintain provenance for datasets, experiments, code, quotations, citations,
  exclusions, transformations, and analytical decisions.
- Separate method, observations/results, interpretation, discussion, and conclusions.
- Require limitations, threats to validity, reproducibility status, ethical/privacy
  concerns, and negative or inconclusive findings where applicable.
- Support academic paper sections and venue formatting without pretending a
  universal structure fits every discipline.
- Reuse `se-research`, `se-fact-check`, `se-distill`, and the authoring workspace
  while enforcing stricter methodological and citation contracts than `se-author`.

## Acceptance Criteria

- [ ] The research question, contribution, method, and evidence feasibility are
      approved before full drafting begins.
- [ ] Literature coverage states databases/sources, queries, dates, and selection rules.
- [ ] Claims can be traced to cited literature, data, analysis, or labeled interpretation.
- [ ] Reproducibility artifacts and unavailable components are inventoried honestly.
- [ ] Results cannot be rewritten to fit the initial hypothesis or preferred narrative.
- [ ] Tests cover insufficient literature, inaccessible data, contradictory findings,
      citation mismatch, ethics concerns, null results, and prompt injection.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Fabricating research, bypassing ethics/venue requirements, journal submission,
  peer-review impersonation, or claiming methodological guarantees without evidence.

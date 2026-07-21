# Implement se-knowledge-gap

## Goal

Audit a defined knowledge scope across sources such as Obsidian, Notion, Slack,
and documents to identify what is missing, conflicting, stale, or unsupported.

## Requirements

- Require a topic/question, intended decision or audience, source inventory,
  and freshness threshold.
- Build a claim/decision map with provenance before classifying gaps.
- Identify contradictions, outdated guidance, duplicate authorities, missing
  rationale, unresolved questions, and low-confidence claims.
- Distinguish inaccessible-source gaps from genuine absence of knowledge.
- Recommend a prioritized closure plan and appropriate follow-up workflows.
- Reuse `se-fact-check` for individual claim verdicts and `se-research` for new
  external evidence; this skill audits the existing knowledge system.

## Acceptance Criteria

- [ ] Every reported gap cites the searched scope and supporting evidence.
- [ ] “Not found” cannot become “does not exist” when coverage is incomplete.
- [ ] Contradictions preserve both positions, dates, and authority signals.
- [ ] Tests cover stale sources, access gaps, terminology mismatch, duplicate
      records, and prompt injection.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Automatically rewriting source documents or conducting unlimited new research.

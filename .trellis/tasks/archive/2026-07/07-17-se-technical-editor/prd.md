# Implement se-technical-editor

## Goal

Review an existing technical draft rigorously while preserving the author's
intent and voice, then apply only approved substantive revisions.

## Requirements

- Accept a draft plus optional brief, audience, evidence ledger, publication
  target, and desired review depth.
- Run distinct passes for technical correctness, evidence/citations, hidden
  assumptions, code/examples, novelty, skeptical-reader objections, structure,
  comprehension, confidentiality, title/opening strength, and voice consistency.
- Distinguish factual defects, high-confidence improvements, editorial choices,
  and optional style preferences.
- Identify generic or AI-sounding prose with concrete evidence and replacement
  strategies rather than using an unverifiable detector score.
- Produce an editorial report before rewriting material claims, structure, or voice.
- Preserve citations and the author's firsthand claims; never fabricate technical
  validation, execution results, or personal experience.
- Support focused review passes and a full review without requiring `se-author`.

## Acceptance Criteria

- [ ] Findings include severity, location, rationale, and recommended action.
- [ ] Unsupported claims and unverified code are never reported as validated.
- [ ] Substantive rewrites require approval or an explicit edit request.
- [ ] Voice edits preserve representative author language from the supplied draft.
- [ ] Tests cover technically wrong but fluent prose, weak citations, confidential
      details, generic prose, conflicting editorial goals, and prompt injection.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Topic discovery, primary research, direct publication, or automated authorship scoring.

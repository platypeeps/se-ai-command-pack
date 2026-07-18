# Implement se-technical-editor Design

## Overview

Add `se-technical-editor` under Improve as a multi-pass review workflow for an
existing technical draft. It produces an evidence-located editorial report first
and preserves author intent, citations, firsthand claims, and representative voice;
substantive changes require approval or an explicit edit request.

## Proposal

Accept draft plus optional brief, audience, evidence ledger, publication target,
review depth or focused passes, and `profile=auto|off|locator`. Establish the
draft's intended claim, audience outcome, authoritative source version, and
confidentiality constraints before review.

Run distinct passes for technical correctness, evidence/citations, hidden
assumptions, code/examples, novelty, skeptical-reader objections, structure,
comprehension, confidentiality, title/opening, and voice. Each finding records
severity, location, category, evidence/rationale, confidence, and recommended
action. Classify findings as factual defect, high-confidence improvement,
editorial choice, or optional style preference.

Never call code or a claim validated unless execution or authoritative evidence
supports it. Identify generic or AI-sounding prose through concrete textual
symptoms and replacement strategies, not detector scores. Build a voice sample
from representative supplied language; an outward-safe profile may supplement
preferences but never override the draft's evidenced voice or add experiences.

Return the editorial report, prioritized revision plan, verification gaps, and
approval boundary. Apply only explicitly requested edits, preserving citations
and providing a substantive change ledger.

## Boundaries And Non-Goals

- Do not discover topics, conduct primary research, publish, or score authorship.
- Do not report unexecuted code, unsupported claims, or citations as validated.
- Do not materially rewrite claims, structure, or voice without approval/explicit request.
- Do not fabricate personal experience or erase deliberate author choices silently.

## Affected Files

- Canonical skill, Improve-family registration, source/profile references,
  manifest, fixtures/tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Fluent prose can conceal technical errors; correctness pass precedes polish.
- Conflicting editorial goals require explicit prioritization.
- Confidential details may need redaction before broader evidence checks.
- Weak citations can support adjacent facts but not the stated claim.
- Profile/draft voice conflicts should favor current instructions and supplied draft evidence.

## Validation

- Pin pass separation, finding schema/classes, validation vocabulary, report-before-
  rewrite, approval gate, citation/voice preservation, and profile limits.
- Test technically wrong fluent prose, weak citations, unverified code, confidential
  details, generic prose, conflicting goals, profile conflict, and injection.
- Run generation, focused tests, full checks, and diff check.

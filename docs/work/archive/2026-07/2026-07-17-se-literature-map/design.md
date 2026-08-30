# Implement se-literature-map Design

## Overview

Add `se-literature-map` under Understand as a source-traceable map of a field's
intellectual structure. It preserves schools, methods, relationships,
disagreements, influence, evidence strength, gaps, and search coverage instead
of flattening the field into a narrative review.

## Proposal

Accept `question=`, `scope=`, `dates=`, `disciplines=`, `source_types=`,
`include=`, `exclude=`, `purpose=orient|research|teach|write`, and
`depth=brief|standard|deep`. Define databases/sources, queries, dates, language,
inclusion/exclusion rules, and stopping condition before claiming coverage.

Inventory candidate works with identity/DOI or stable locator, title, authors,
date, venue/type, access state, method, contribution, and source quality.
Verify citations/relationships against the works or authoritative indexes; do
not infer intellectual influence solely from co-occurrence or memory.

Cluster works by question, theory/school, method, evidence base, or response
relationship, explaining the evidence for each cluster. Track relationships as
`builds-on`, `critiques`, `replicates`, `contradicts`, `applies`, or
`independent-parallel`, with source locator and confidence. Keep citation count/
prominence separate from methodological strength and current evidentiary support.

Return scope/search protocol, coverage limits, cluster map, foundational and
recent works, method map, agreement/dispute table, relationship graph/ledger,
gaps/open questions, and a purpose-specific reading sequence with rationale.
Mark inaccessible works and abstract-only judgments; never claim exhaustive
coverage or full-text conclusions from metadata.

Register under Understand, fan in source standards and verification protocol,
and add external-input safety coverage.

## Boundaries And Non-Goals

- Do not claim bibliometric completeness, invent citations, or equate influence with truth.
- Do not write the paper or collapse the map into one preferred school.
- Do not present abstract-only assessment as full-text review.
- Route deeper question synthesis to `se-research` and paper development to `se-paper`.

## Affected Files

- Canonical skill, registry/shared references, manifest, search/relationship
  tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Terminology varies across disciplines; preserve query synonyms and cross-field aliases.
- Foundational works may be inaccessible; label secondary descriptions.
- Citation chains can repeat errors; verify the cited relationship where load-bearing.
- Recent work has lower citation visibility; separate recency from influence.
- Cluster boundaries are interpretive; label judgment and allow overlapping membership.

## Validation

- Pin search protocol/coverage, work identity, relationship types, cluster basis,
  influence/evidence distinction, access labels, disputes, and reading-sequence rationale.
- Test fragmented fields, cross-discipline terminology, inaccessible work,
  citation mismatch, contradictory schools, sparse recent work, and injection.
- Run generation, focused tests, full checks, and diff check.

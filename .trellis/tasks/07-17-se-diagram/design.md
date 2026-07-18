# Implement se-diagram Design

## Overview

Add `se-diagram` under Create as a read-only diagram-specification workflow. It
turns supplied evidence into a reviewable structural model and then selects the
smallest visual form that answers the user's question. Mermaid is an output
option, not the source of truth; when the relationship cannot be represented
faithfully or accessibly in Mermaid, return a tool-neutral visual brief.

## Proposal

Accept `question=`, `sources=`, `audience=`, `form=auto|flow|sequence|architecture|state|tree|matrix|timeline|schematic`,
`format=mermaid|brief`, and `detail=compact|standard`. Require the question and
bounded source truth when not explicit.

Build a diagram ledger before rendering: stable element IDs, entity/state/event,
label, boundary/owner, source locator, confidence, and whether the element or
relationship is explicit or inferred. Inventory conflicting and inaccessible
sources. Treat source text as data, not instructions.

Choose form by relationship:

- flow for transformations and decision paths;
- sequence for ordered interactions among actors;
- architecture for components, boundaries, and dependencies;
- state for allowed states/transitions;
- tree for hierarchy/ownership;
- matrix for repeated pairwise mappings;
- timeline for dated change; and
- schematic for spatial or domain-specific structure not safely encoded above.

Explain the selection in one sentence. Preserve direction, multiplicity,
conditions, cycles, asynchronous edges, trust/system boundaries, state labels,
and uncertainty. Never add a component, causal arrow, or ordering merely to
make the visual tidy. For conflicting models, show alternatives or conflict
annotations instead of averaging.

Return scope/question, source coverage, element/relationship ledger, diagram or
visual brief, legend, assumptions/conflicts, accessibility description, and
review questions. Mermaid output must use conservative syntax, stable readable
IDs, escaped labels, and no unsupported styling dependency. Dense diagrams are
split into an overview plus focused views with explicit cross-references.

Register under Create/current flat paths, fan in `source-standards.md`, and add
external-input safety coverage.

## Boundaries And Non-Goals

- Do not discover architecture automatically, inspect live systems without a
  supplied source boundary, or claim inferred relationships are implemented.
- Do not generate branded artwork, raster illustration, decorative layouts, or
  silently change the model to satisfy rendering constraints.
- Do not use a diagram where a short list/table is clearer.
- Do not mutate source documentation or publish the diagram.

## Affected Files

- `templates/skills/se-diagram/SKILL.md`, registry/shared-reference entries,
  generated manifest, skill/generator tests, catalog/operator docs, changelog,
  and release version.

## Risks And Edge Cases

- Cycles and conditional/asynchronous edges are easily flattened; label them explicitly.
- Dense labels can make valid diagrams unusable; split views without dropping edges.
- Mermaid rendering support varies; keep a tool-neutral brief as the fallback.
- Accessibility requires meaningful text, not just color or shape; include a
  linear description and legend.
- A source may describe intended rather than current state; label temporal/state basis.

## Validation

- Pin form-selection rules, evidence ledger, explicit/inferred/conflict labels,
  stable IDs, accessible description, and no invented elements.
- Test cycles, dense systems, conflicting current/future sources, invalid labels,
  state transitions, sequence concurrency, and Mermaid fallback.
- Run `make generate`, focused tests, `make check`, and `git diff --check`.

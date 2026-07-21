# Implement se-diagram

## Goal

Develop a precise, reviewable diagram specification for a system, process,
concept, comparison, hierarchy, or event sequence.

## Requirements

- Resolve the question the visual must answer, audience, source truth, and output format.
- Extract entities, relationships, direction, boundaries, states, labels, and uncertainty.
- Select the smallest fitting form: flow, sequence, architecture, state, tree,
  matrix, timeline, or annotated schematic.
- Produce Mermaid when suitable or a tool-neutral visual brief when not.
- Never invent components or causal relationships to make the layout attractive.

## Acceptance Criteria

- [ ] Every visual element maps to supplied evidence or labeled inference.
- [ ] The chosen visual form is justified by the relationship being shown.
- [ ] Tests cover cycles, uncertainty, dense systems, conflicting sources, and accessibility labels.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Raster illustration, branded design, or automatic architecture discovery.

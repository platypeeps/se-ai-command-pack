# Implement se-explain Design

## Overview

Add `se-explain` under Understand as an audience-calibrated explanation
workflow. It owns one concept/question at progressive depth, not a curriculum,
assessment, or open-ended research task.

## Proposal

Accept `topic=`, `audience=`, `purpose=`, `prior_knowledge=`, `depth=brief|standard|deep`,
`sources=`, and `format=prose|walkthrough|qa`. Correct a false premise before
building on it. For current or disputed claims, use supplied/verified sources or
route to research; distinguish stable general knowledge from sourced facts.

Build a concept skeleton: essential model, prerequisites, mechanism, example,
boundaries, common misconceptions, and next useful question. Choose only layers
needed for the audience/purpose. Define specialized terms at first use, preserve
necessary precision, and avoid condescension or fake simplicity.

When using an analogy, label it, map each part to the real mechanism, and name
where it breaks. Examples must not silently become evidence. Separate facts,
assumptions, simplifications, and unresolved/current claims.

Return the direct model first, then intuition/example, mechanism, limitations,
misconceptions, quick self-check, and next learning step as appropriate.
Follow-ups should deepen or zoom into the requested layer without repeating the
entire prior response; maintain a short “established so far” context.

Register under Understand, fan in source standards, and include external-input
safety when sources are supplied.

## Boundaries And Non-Goals

- Do not create a full curriculum (`se-learn`), study artifact (`se-study-guide`),
  or mastery assessment (`se-socratic-review`).
- Do not invent authority for current/disputed claims or preserve a false premise.
- Do not use analogy as proof or omit the failure boundary of simplification.
- Do not over-personalize beyond stated audience/prior knowledge.

## Affected Files

- Canonical skill, registry/source-standard fan-out, manifest, focused tests,
  catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Novice framing can become inaccurate; retain the minimum mechanism and limitations.
- Expert users need compression, not definitions of basics; adapt vocabulary and depth.
- A topic may span several concepts; answer the stated question and expose prerequisites.
- Current examples can age; date and source unstable claims.
- Follow-ups can drift scope; restate the active question when needed.

## Validation

- Pin audience adaptation, false-premise correction, layer selection, analogy
  mapping/failure, fact/assumption separation, progressive follow-up, and routing boundaries.
- Test novice/expert, current claim, disputed claim, no sources, misleading
  analogy, prerequisite gap, and injection.
- Run generation, focused tests, full checks, and diff check.

# Implement se-study-guide Design

## Overview

Add `se-study-guide` under Understand as a source-bound transformation from
learning material into retrieval and application practice. Selection is driven
by what the learner must understand/use, not by ordinary summary importance.

## Proposal

Accept `sources=`, `learner=`, `purpose=`, `target_level=`, `prerequisites=`,
`scope=`, and `format=standard|flashcards|practice`. Inventory and read supplied
sources fully in bounded passes; report unreadable/omitted regions, versions,
and conflicting definitions.

Build a source concept ledger: concept/definition, prerequisite, relationship,
notation, worked example, misconception/trap, application, and locator. Separate
source content from generated analogy, exercise, distractor, solution, and inference.

Return a dependency-aware concept map, essential definitions, prerequisite
repair, worked examples, common traps, retrieval questions, flashcard-ready
prompts, practice problems, solutions/rubrics, and spaced review order. Cover
recall, explanation, application, comparison, error diagnosis, and transfer.

Every generated answer/solution cites source locators or is labeled generated
inference. Preserve exact technical notation and define transformations. When
sources conflict, present both definitions/context rather than choosing silently.
Difficulty matches the learner but required concepts are not silently removed.

Register under Understand, fan in source standards, and add injection safety.

## Boundaries And Non-Goals

- Do not conduct a live teaching/assessment session or certify mastery.
- Do not add external research without approval or invent missing source answers.
- Do not replace `se-distill`; retention/application coverage can require more space.
- Do not create deceptive flashcards with ambiguous prompts or unsupported distractors.

## Affected Files

- Canonical skill, registry/shared references, manifest, source/practice tests,
  catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Thin sources may not support practice solutions; label gaps and generated scaffolding.
- Flashcards can encourage isolated trivia; include relationship/application prompts.
- Technical notation can be corrupted by paraphrase; preserve exact forms and locators.
- Conflicting curricula may use identical terms differently; scope definitions.
- Answer leakage in question wording reduces retrieval value; review prompts independently.

## Validation

- Pin full coverage disclosure, concept ledger, source/generated separation,
  question-type coverage, solutions/locators, prerequisite adaptation, and conflict handling.
- Test thin sources, unreadable sections, notation, conflicting definitions,
  novice/expert learner, ambiguous flashcards, and injection.
- Run generation, focused tests, full checks, and diff check.

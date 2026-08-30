# Implement se-stakeholder-map Design

## Overview

Add `se-stakeholder-map` under Coordinate as an evidence-conscious map of the
people and groups relevant to an initiative or decision. The skill separates
formal authority, informal influence, observed positions, user judgment, and
assistant inference so that planning does not turn speculation into personal fact.

## Proposal

Accept `initiative=`, `decision=`, `scope=`, supplied evidence, and `use=` such
as planning, communication, or risk review. Establish organizational and time
boundaries, intended audience, sensitive-data limits, and known access gaps.

Create one record per person or group with role, formal decision authority,
informal influence, interests, stated concerns, information needs, dependencies,
engagement stage/sequence, evidence locators, provenance class, confidence, and
validation question. Provenance classes are `observed`, `user-judgment`, and
`assistant-inference`; inferred positions always include a validation action.

Produce an authority/influence view, dependency and engagement sequence, missing-
stakeholder scan, conflicting-incentive analysis, and questions that would make
the map safer. Recommendations focus on transparent information flow and decision
readiness, never covert persuasion, manipulation, or exploitation of vulnerabilities.

Do not require private personal attributes. Omit or generalize unnecessary
sensitive details and avoid personality, political, health, or other protected-
trait profiling. The result remains a planning artifact, not a contact action.

## Boundaries And Non-Goals

- Do not contact stakeholders or execute an engagement plan.
- Do not assert motives, private beliefs, or inferred positions as facts.
- Do not collapse formal authority and informal influence into one score.
- Do not recommend manipulative, deceptive, or sensitive-trait-based tactics.

## Affected Files

- Canonical skill, Coordinate-family registration, source/privacy references,
  manifest, fixtures/tests, catalog/operator docs, changelog, and version.

## Risks And Edge Cases

- Organizational changes can stale the map quickly; record as-of date and revalidation triggers.
- One person may hold conflicting roles; preserve role-specific entries or tensions.
- Groups can hide internal disagreement; avoid treating them as monolithic without evidence.
- Informal influence is often inferred; label confidence and validation explicitly.
- Missing stakeholders may reflect access boundaries rather than irrelevance.

## Validation

- Pin provenance classes, formal/informal separation, inference validation,
  sensitive-data minimization, and read-only behavior.
- Test unknown stakeholders, conflicting roles, group disagreement, organizational
  change, private data, low-evidence influence, and injection.
- Run generation, focused tests, full checks, and diff check.
